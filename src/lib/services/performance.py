"""Service functions for performance related operations"""

from datetime import date, datetime
from logging import getLogger
from math import prod
from typing import cast

from ...raw_data.models import StockDividend, StockPrice
from ...transactions.models import CashTransaction, StockTransaction
from ..dataclasses import (
    PerformanceSnapshot,
    StockPortfolioSnapshot,
    StockPositionSnapshot,
)
from ..helpers import get_latest_snapshot
from .cash import transaction_to_usd
from .replay import generate_snapshot_series

LOGGER = getLogger(__name__)


def get_position_performance(
    portfolio_snapshots: dict[date, StockPortfolioSnapshot],
    price_info: list[StockPrice],
    dividends: list[StockDividend],
    transactions: list[StockTransaction],
    series: list[date],
) -> dict[date, PerformanceSnapshot]:
    """Creates a timeseries from the position performance at each date in the series."""

    LOGGER.debug("Generate %s performance snapshots for a position.", len(series))

    series = sorted(series)
    if not series or not portfolio_snapshots:
        return {}

    actions = sorted(
        cast(
            list[StockPrice | StockDividend | StockTransaction],
            [*price_info, *dividends, *transactions],
        ),
        key=lambda x: x.date,
    )
    first_snapshot_date = series[0]
    first_snapshot = portfolio_snapshots[first_snapshot_date]
    initial_position = first_snapshot.positions.get(
        actions[0].ticker.ticker
    ) or StockPositionSnapshot(
        stock=actions[0].ticker,
        shares=0,
        price=0,
        dividend=0,
        purchase_price=0,
        first_purchase_date=datetime.now().date(),
        latest_purchase_date=datetime.now().date(),
    )

    def accumulate(
        snapshot: PerformanceSnapshot,
        action: StockPrice | StockDividend | StockTransaction,
    ) -> PerformanceSnapshot:
        portfolio = get_latest_snapshot(action.date, portfolio_snapshots)

        if not portfolio:
            return snapshot

        position = portfolio.positions.get(action.ticker.ticker)

        if not position:
            return snapshot

        if isinstance(action, StockPrice):
            return PerformanceSnapshot(
                date=snapshot.date,
                base_size=snapshot.base_size,
                appreciation=action.value * position.shares - snapshot.base_size,
                dividends=snapshot.dividends,
                cash_flow=snapshot.cash_flow,
            )

        if isinstance(action, StockDividend):
            return PerformanceSnapshot(
                date=snapshot.date,
                base_size=snapshot.base_size,
                appreciation=snapshot.appreciation,
                dividends=snapshot.dividends + action.amount * position.shares,
                cash_flow=snapshot.cash_flow,
            )

        if isinstance(action, StockTransaction):
            return PerformanceSnapshot(
                date=snapshot.date,
                base_size=snapshot.base_size,
                appreciation=snapshot.appreciation,
                dividends=snapshot.dividends,
                cash_flow=snapshot.cash_flow + action.price * action.amount,
            )

        return snapshot

    def take_snapshot(
        snapshot: PerformanceSnapshot, target_date: date
    ) -> PerformanceSnapshot:
        taken = PerformanceSnapshot(
            date=target_date,
            base_size=snapshot.base_size,
            appreciation=snapshot.appreciation,
            dividends=snapshot.dividends,
            cash_flow=snapshot.cash_flow,
        )

        snapshot.date = target_date
        snapshot.base_size = snapshot.capital_size
        snapshot.appreciation = 0
        snapshot.dividends = 0
        snapshot.cash_flow = 0

        return taken

    return generate_snapshot_series(
        initial=PerformanceSnapshot(
            date=first_snapshot_date,
            base_size=initial_position.size,
        ),
        actions=actions,
        series=series,
        operation=accumulate,
        take_snapshot=take_snapshot,
    )


def get_portfolio_performance(
    portfolio_snapshots: dict[date, StockPortfolioSnapshot],
    dividends: list[StockDividend],
    cash_transactions: list[CashTransaction],
    series: list[date],
) -> dict[date, PerformanceSnapshot]:
    """Creates a timeseries from the portfolio performance at each date in the series."""

    LOGGER.debug("Generate %s performance snapshots for a portfolio.", len(series))

    if not portfolio_snapshots or not series:
        return {}

    first_snapshot_date = series[0]
    first_snapshot = portfolio_snapshots[first_snapshot_date]

    def accumulate(
        snapshot: PerformanceSnapshot,
        action: StockPortfolioSnapshot | StockDividend | CashTransaction,
    ) -> PerformanceSnapshot:
        if isinstance(action, CashTransaction):
            currency_adjusted_action = transaction_to_usd(action)

            return PerformanceSnapshot(
                date=snapshot.date,
                base_size=snapshot.base_size,
                appreciation=snapshot.appreciation,
                dividends=snapshot.dividends,
                cash_flow=snapshot.cash_flow + currency_adjusted_action.amount,
            )

        if isinstance(action, StockPortfolioSnapshot):
            return PerformanceSnapshot(
                date=snapshot.date,
                base_size=snapshot.base_size,
                appreciation=action.assets_under_management - snapshot.base_size,
                dividends=snapshot.dividends,
                cash_flow=snapshot.cash_flow,
            )

        if isinstance(action, StockDividend):
            portfolio = get_latest_snapshot(
                cast(date, action.date), portfolio_snapshots
            )

            if not portfolio:
                return snapshot

            position = portfolio.positions.get(action.ticker.ticker)

            if not position:
                return snapshot

            return PerformanceSnapshot(
                date=snapshot.date,
                base_size=snapshot.base_size,
                appreciation=snapshot.appreciation,
                dividends=snapshot.dividends + action.amount * position.shares,
                cash_flow=snapshot.cash_flow,
            )

        raise Exception("Unknown action type.")

    def take_snapshot(
        snapshot: PerformanceSnapshot, target_date: date
    ) -> PerformanceSnapshot:
        taken = PerformanceSnapshot(
            date=target_date,
            base_size=snapshot.base_size,
            appreciation=snapshot.appreciation,
            dividends=snapshot.dividends,
            cash_flow=snapshot.cash_flow,
        )

        snapshot.date = target_date
        snapshot.base_size = snapshot.capital_size
        snapshot.appreciation = 0
        snapshot.dividends = 0
        snapshot.cash_flow = 0

        return taken

    return generate_snapshot_series(
        initial=PerformanceSnapshot(
            date=first_snapshot_date,
            base_size=first_snapshot.assets_under_management,
        ),
        actions=sorted(
            cast(
                list[StockPortfolioSnapshot | StockDividend | CashTransaction],
                [*portfolio_snapshots.values(), *dividends, *cash_transactions],
            ),
            key=lambda x: cast(date, x.date),
        ),
        series=series,
        operation=accumulate,
        take_snapshot=take_snapshot,
    )


def time_weighted_return(performance_snapshots: list[PerformanceSnapshot]) -> float:
    """Calculate the time weighted return of the position or portfolio."""

    return prod((1 + snapshot.performance for snapshot in performance_snapshots)) - 1
