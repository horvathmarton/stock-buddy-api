"""
Basic financial calculation realted services and functions.
"""

from datetime import date
from typing import List, Dict

from apps.raw_data.models import StockDividend, StockPrice, StockSplit
from apps.stocks.models import Stock, StockPortfolio
from apps.transactions.models import StockTransaction

from ..dataclasses import StockPositionSnapshot, StockPortfolioSnapshot


class FinanceService:
    """Implements some basic Excel finance functions and a portfolio snapshot generator."""

    @staticmethod
    def present_value(
        rate: float,
        periods: float,
        periodic_payment: float,
        future_value: float = 0,
        paid_at_period_start: bool = False,
    ) -> float:
        """Present value. Discounts the provided value to present."""

        raise NotImplementedError("This function has not been implemented yet.")

    @staticmethod
    def future_value(
        rate: float,
        periods: float,
        periodic_payment: float,
        present_value: float,
        paid_at_period_start: bool = False,
    ) -> float:
        """Future value. Compounds the provided value to future."""

        raise NotImplementedError("This function has not been implemented yet.")

    @staticmethod
    def rri(periods: float, present_value: float, future_value: float) -> float:
        """
        Rate of investment return.
        Calculate Compound Annual Growth Rate (CAGR).

        Rounding to four precision to avoid floating point math error.
        """

        return round((future_value / present_value) ** (1 / periods) - 1, 4)

    def internal_rate_of_return(self) -> str:
        """Calculates the internal rate of return (IRR) from a list of cash flows."""

        raise NotImplementedError("This function has not been implemented yet.")

    def net_present_value(self):
        """Discounts the net present value form a list of cash flows at the discount rate."""

        raise NotImplementedError("This function has not been implemented yet.")

    @classmethod
    def get_portfolio_snapshot(
        cls, portfolios: List[StockPortfolio], snapshot_date: date = date.today()
    ) -> StockPortfolioSnapshot:
        """Returns the snapshot of the portfolio at a given time."""

        positions = cls.__get_postions_for_portfolio(portfolios, snapshot_date)

        return StockPortfolioSnapshot(positions=positions, owner=portfolios[0].owner)

    @classmethod
    def __get_postions_for_portfolio(
        cls, portfolios: List[StockPortfolio], snapshot_date: date
    ) -> Dict[str, StockPositionSnapshot]:
        """Summarizes the positions by ticker for the portfolio."""

        transactions = StockTransaction.objects.filter(
            portfolio__in=portfolios, date__lte=snapshot_date
        )
        splits = StockSplit.objects.filter(date__lte=snapshot_date)
        actions = sorted([*transactions, *splits], key=lambda x: x.date)

        positions = {}
        for action in actions:
            ticker = action.ticker.ticker

            if isinstance(action, StockTransaction) and ticker not in positions:
                latest_price = cls.__get_latest_stock_price(ticker, snapshot_date)
                latest_dividend = cls.__get_latest_dividend(ticker, snapshot_date)

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

        return positions

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
        ratio = split.ratio

        current_position.shares = int(current_position.shares * ratio)
        current_position.purchase_price /= ratio
        current_position.dividend /= ratio

        return current_position
