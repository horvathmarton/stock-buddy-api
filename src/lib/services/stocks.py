"""Service functions for stock portfolio related operations."""

from copy import deepcopy
from datetime import date
from logging import getLogger
from typing import Optional

from django.contrib.auth.models import User

from ...raw_data.models import StockDividend, StockPrice, StockSplit
from ...stocks.models import Stock, StockPortfolio
from ...transactions.models import StockTransaction
from ..dataclasses import StockPortfolioSnapshot, StockPositionSnapshot
from .replay import generate_snapshot_series

LOGGER = getLogger(__name__)


def get_portfolio(
    actions: list[StockTransaction | StockSplit],
    series: list[date],
    owner: User,
) -> dict[date, StockPortfolioSnapshot]:
    """Creates a timeseries from the portfolio at each date in the series."""

    LOGGER.debug(
        "Generate series for %s actions(s) at %s snapshot date(s) for a portfolio.",
        len(actions),
        len(series),
    )

    series = sorted(series)
    if not series:
        return {}

    last_snapshot_date = series[-1]

    def sum_portfolio(
        snapshot: StockPortfolioSnapshot, action: StockTransaction | StockSplit
    ):
        ticker = action.ticker.ticker
        positions = snapshot.positions

        if isinstance(action, StockTransaction) and ticker not in positions:
            latest_price = __get_latest_stock_price(ticker, last_snapshot_date)
            latest_dividend = __get_latest_dividend(ticker, last_snapshot_date)

            # In this situation we consider a negative or zero value a spinoff sellout.
            if action.amount > 0:
                positions[ticker] = __create_position(
                    action, latest_price, latest_dividend
                )
        elif isinstance(action, StockTransaction) and ticker in positions:
            updated_position = __update_position(positions[ticker], action)
            positions[ticker] = updated_position

            if updated_position.shares == 0:
                del positions[ticker]
            elif updated_position.shares < 0:
                raise Exception("Negative position size is not allowed.")
        elif isinstance(action, StockSplit) and ticker in positions:
            split_position = __split_position(positions[ticker], action)
            positions[ticker] = split_position

        return snapshot

    def take_snapshot(
        snapshot: StockPortfolioSnapshot, snapshot_date: date
    ) -> StockPortfolioSnapshot:
        return StockPortfolioSnapshot(
            positions=deepcopy(snapshot.positions),
            date=snapshot_date,
            owner=owner,
        )

    return generate_snapshot_series(
        initial=StockPortfolioSnapshot(positions={}, date=date.today(), owner=owner),
        actions=actions,
        series=series,
        operation=sum_portfolio,
        take_snapshot=take_snapshot,
    )


def get_portfolio_snapshot(
    portfolios: list[StockPortfolio], snapshot_date: date = date.today()
) -> StockPortfolioSnapshot:
    """Summarizes the positions by ticker for each snapshot date."""

    LOGGER.debug(
        "Calculate portfolio snapshot for %s portfolio at %s.",
        len(portfolios),
        snapshot_date,
    )

    transactions = StockTransaction.objects.filter(
        portfolio__in=portfolios, date__lte=snapshot_date
    )
    splits = StockSplit.objects.filter(date__lte=snapshot_date)
    actions = sorted([*transactions, *splits], key=lambda x: x.date)

    return get_portfolio(actions, [snapshot_date], portfolios[0].owner)[snapshot_date]


def get_all_stocks_since_inceptions(
    portfolios: list[StockPortfolio], snapshot_date: date = date.today()
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


def get_first_transaction(portfolios: list[StockPortfolio]):
    """Returns the first stock transaction of the list of portfolio if there is any, otherwise it returns None."""

    return (
        StockTransaction.objects.filter(portfolio__in=portfolios)
        .order_by("date")
        .first()
    )


def __get_latest_stock_price(ticker: Stock, snapshot_date: date) -> Optional[float]:
    """Queries the latest stock price info for the stock."""

    try:
        return (
            StockPrice.objects.filter(ticker=ticker, date__lte=snapshot_date)
            .latest("date")
            .value
        )
    except StockPrice.DoesNotExist:
        return None


def __get_latest_dividend(ticker: Stock, snapshot_date: date) -> float:
    """Queries for the latest dividend info for the stock."""

    try:
        latest_dividend_date = (
            StockDividend.objects.filter(ticker=ticker, date__lte=snapshot_date)
            .latest("date")
            .date
        )

        return StockDividend.objects.filter(ticker=ticker, date=latest_dividend_date)[
            0
        ].amount

    except StockDividend.DoesNotExist:
        # It is possible that the stock doesn't pay dividend
        # in that case we just return 0.
        return 0.0


def __create_position(
    transaction: StockTransaction,
    latest_price: Optional[float],
    latest_dividend: float,
) -> StockPositionSnapshot:
    """Helper function to generate a new position entity."""

    # The dividend info is multiplied by 4 to project the latest quarterly
    # value to the next year.
    return StockPositionSnapshot(
        stock=transaction.ticker,
        shares=transaction.amount,
        price=latest_price or transaction.price,
        dividend=latest_dividend * 4,
        purchase_price=transaction.price,
        first_purchase_date=transaction.date,
        latest_purchase_date=transaction.date,
    )


def __update_position(
    current_position: StockPositionSnapshot, transaction: StockTransaction
) -> StockPositionSnapshot:
    """Helper function to update a position entity."""

    # We only change the average price if we buy more stock.
    # We should keep the average untouched when selling.
    if transaction.amount >= 0:
        current_position.purchase_price = round(
            (current_position.size_at_cost + (transaction.amount * transaction.price))
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


def __split_position(
    current_position: StockPositionSnapshot, split: StockSplit
) -> StockPositionSnapshot:
    """Helper function to split a position entity."""

    ratio = split.ratio

    current_position.shares = int(current_position.shares * ratio)
    current_position.purchase_price /= ratio
    current_position.dividend /= ratio

    return current_position
