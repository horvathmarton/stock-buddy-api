"""
A service to generate snapshots from a stock portfolio.
"""

from datetime import date
from logging import getLogger

from apps.raw_data.models import StockDividend, StockPrice, StockSplit
from apps.stocks.models import Stock, StockPortfolio
from apps.transactions.models import StockTransaction

from ..dataclasses import StockPortfolioSnapshot, StockPositionSnapshot

LOGGER = getLogger(__name__)


class StocksService:
    """Portfolio snapshot generator."""

    @classmethod
    def get_portfolio_snapshot(
        cls, portfolios: list[StockPortfolio], snapshot_date: date = date.today()
    ) -> StockPortfolioSnapshot:
        """Summarizes the positions by ticker for the portfolio."""
        return cls.get_portfolio_snapshot_series(portfolios, [snapshot_date])[
            snapshot_date
        ]

    @classmethod
    def get_portfolio_snapshot_series(
        cls, portfolios: list[StockPortfolio], snapshot_dates: list[date]
    ) -> dict[date, StockPortfolioSnapshot]:
        LOGGER.debug(
            "Generating snapshot for %s portfolio(s) at %s snapshot date(s).",
            len(portfolios),
            len(snapshot_dates),
        )

        if not snapshot_dates:
            return {}

        snapshot_dates = sorted(snapshot_dates)
        last_snapshot_date = snapshot_dates[-1]

        transactions = StockTransaction.objects.filter(
            portfolio__in=portfolios, date__lte=last_snapshot_date
        )
        splits = StockSplit.objects.filter(date__lte=last_snapshot_date)
        actions = sorted([*transactions, *splits], key=lambda x: x.date)

        positions = {}
        snapshots = {}
        for action in actions:
            # Take a snapshot if the next action would not affect the next snapshot date.
            while action.date > snapshot_dates[0]:
                snapshots[snapshot_dates[0]] = StockPortfolioSnapshot(
                    positions=positions, owner=portfolios[0].owner
                )
                snapshot_dates = snapshot_dates[1:]

            ticker = action.ticker.ticker

            if isinstance(action, StockTransaction) and ticker not in positions:
                latest_price = cls.__get_latest_stock_price(ticker, last_snapshot_date)
                latest_dividend = cls.__get_latest_dividend(ticker, last_snapshot_date)

                # In this situation we consider a negative or zero value a spinoff sellout.
                if action.amount > 0:
                    positions[ticker] = cls.__create_position(
                        action, latest_price, latest_dividend
                    )
            elif isinstance(action, StockTransaction) and ticker in positions:
                updated_position = cls.__update_position(positions[ticker], action)
                positions[ticker] = updated_position

                if updated_position.shares == 0:
                    del positions[ticker]
                elif updated_position.shares < 0:
                    raise Exception("Negative position size is not allowed.")
            elif isinstance(action, StockSplit) and ticker in positions:
                split_position = cls.__split_position(positions[ticker], action)
                positions[ticker] = split_position

        # When we are done with the replay we take all the snapshots after the last action.
        while snapshot_dates:
            snapshots[snapshot_dates[0]] = StockPortfolioSnapshot(
                positions=positions, owner=portfolios[0].owner
            )
            snapshot_dates = snapshot_dates[1:]

        return snapshots

    @classmethod
    def get_all_stocks_since_inceptions(
        cls, portfolios: list[StockPortfolio], snapshot_date: date = date.today()
    ):
        """
        Returns a list of all stocks that has been transacted by the provided list of portfolios
        up until the snapshot date.
        """

        return (
            StockTransaction.objects.filter(
                portfolio__in=portfolios, date__lte=snapshot_date
            )
            .values("ticker")
            .distinct()
        )

    @classmethod
    def get_first_transaction(cls, portfolios: list[StockPortfolio]):
        """Returns the first stock transaction of the list of portfolio if there is any, otherwise it returns None."""

        return (
            StockTransaction.objects.filter(portfolio__in=portfolios)
            .order_by("date")
            .first()
        )

    @staticmethod
    def __get_latest_stock_price(ticker: Stock, snapshot_date: date) -> float:
        """Queries the latest stock price info for the stock."""

        latest_price_date = (
            StockPrice.objects.filter(ticker=ticker, date__lte=snapshot_date)
            .latest("date")
            .date
        )

        return StockPrice.objects.filter(ticker=ticker, date=latest_price_date)[0].value

    @staticmethod
    def __get_latest_dividend(ticker: Stock, snapshot_date: date) -> float:
        """Queries for the latest dividend info for the stock."""

        try:
            latest_dividend_date = (
                StockDividend.objects.filter(
                    ticker=ticker, payout_date__lte=snapshot_date
                )
                .latest("payout_date")
                .payout_date
            )

            return StockDividend.objects.filter(
                ticker=ticker, payout_date=latest_dividend_date
            )[0].amount

        except StockDividend.DoesNotExist:
            # It is possible that the stock doesn't pay dividend
            # in that case we just return 0.
            return 0.0

    @staticmethod
    def __create_position(
        transaction: StockTransaction, latest_price: float, latest_dividend: float
    ) -> StockPositionSnapshot:
        """Helper function to generate a new position entity."""

        # The dividend info is multiplied by 4 to project the latest quarterly
        # value to the next year.
        return StockPositionSnapshot(
            stock=transaction.ticker,
            shares=transaction.amount,
            price=latest_price,
            dividend=latest_dividend * 4,
            purchase_price=transaction.price,
            first_purchase_date=transaction.date,
            latest_purchase_date=transaction.date,
        )

    @staticmethod
    def __update_position(
        current_position: StockPositionSnapshot, transaction: StockTransaction
    ) -> StockPositionSnapshot:
        """Helper function to update a position entity."""

        # We only change the average price if we buy more stock.
        # We should keep the average untouched when selling.
        if transaction.amount >= 0:
            current_position.purchase_price = round(
                (
                    current_position.size_at_cost
                    + (transaction.amount * transaction.price)
                )
                / (current_position.shares + transaction.amount),
                2,
            )

        current_position.first_purchase_date = min(
            current_position.first_purchase_date, transaction.date
        )
        current_position.latest_purchase_date = max(
            current_position.latest_purchase_date, transaction.date
        )
        current_position.shares += transaction.amount

        return current_position

    @staticmethod
    def __split_position(
        current_position: StockPositionSnapshot, split: StockSplit
    ) -> StockPositionSnapshot:
        """Helper function to split a position entity."""

        ratio = split.ratio

        current_position.shares = int(current_position.shares * ratio)
        current_position.purchase_price /= ratio
        current_position.dividend /= ratio

        return current_position
