"""Service functions for cash and balance related operations."""


from copy import deepcopy
from datetime import date
from logging import getLogger
from os import getenv
from typing import cast

from ...raw_data.models import StockDividend, StockSplit
from ...stocks.models import StockPortfolio
from ...transactions.enums import Currency
from ...transactions.models import CashTransaction, StockTransaction
from ..dataclasses import CashBalanceSnapshot, StockPortfolioSnapshot
from ..queries import sum_cash_transactions
from .replay import generate_snapshot_series
from .stocks import (
    get_all_stocks_since_inceptions,
    get_first_transaction,
    get_portfolio,
)

LOGGER = getLogger(__name__)


def get_portfolio_cash_balance(
    payouts: list[StockDividend],
    series: list[date],
    initial: CashBalanceSnapshot,
    portfolio_snapshots: dict[date, StockPortfolioSnapshot],
) -> dict[date, CashBalanceSnapshot]:
    """Creates a timeseries from the portfolio cash balance at each date in the series."""

    LOGGER.debug(
        "Generate series for %s transaction(s) at %s snapshot date(s).",
        len(payouts),
        len(series),
    )

    def add_dividend_payout(
        snapshot: CashBalanceSnapshot, payout: StockDividend
    ) -> CashBalanceSnapshot:
        portfolio_snapshot = portfolio_snapshots[payout.date]
        position = portfolio_snapshot.positions.get(payout.ticker.ticker, None)

        if position:
            snapshot.USD += payout.amount * position.shares

        return snapshot

    def take_snapshot(
        snapshot: CashBalanceSnapshot, snapshot_date: date
    ) -> CashBalanceSnapshot:
        # pylint: disable=unused-argument

        return deepcopy(snapshot)

    return generate_snapshot_series(
        initial=initial,
        actions=payouts,
        series=series,
        operation=add_dividend_payout,
        take_snapshot=take_snapshot,
    )


def get_portfolio_cash_balance_snapshot(
    portfolios: list[StockPortfolio], snapshot_date: date = date.today()
) -> CashBalanceSnapshot:
    """Returns the cash balance of the portfolio at a given time."""

    LOGGER.debug(
        "Calculate cash balance for %s portfolio at %s.",
        len(portfolios),
        snapshot_date,
    )

    balance = CashBalanceSnapshot()

    usd, eur, huf = sum_cash_transactions(portfolios, snapshot_date)
    balance.USD = usd or 0
    balance.EUR = eur or 0
    balance.HUF = huf or 0

    owned_stocks = get_all_stocks_since_inceptions(portfolios, snapshot_date)
    first_transaction = get_first_transaction(portfolios)
    dividend_payouts = cast(
        list[StockDividend],
        (
            StockDividend.objects.filter(
                ticker__in=owned_stocks,
                date__lte=snapshot_date,
                date__gte=first_transaction.date,
            )
            if first_transaction
            else []
        ),
    )

    transactions = StockTransaction.objects.filter(
        portfolio__in=portfolios, date__lte=snapshot_date
    )
    splits = StockSplit.objects.filter(date__lte=snapshot_date)
    actions = sorted([*transactions, *splits], key=lambda x: x.date)
    snapshot_dates = list({dividend.date for dividend in dividend_payouts})
    owner = portfolios[0].owner if portfolios else None
    portfolio_snapshots = get_portfolio(actions, snapshot_dates, owner)

    return get_portfolio_cash_balance(
        payouts=dividend_payouts,
        series=[snapshot_date],
        initial=balance,
        portfolio_snapshots=portfolio_snapshots,
    )[snapshot_date]


def get_invested_capital(
    transactions: list[CashTransaction], series: list[date]
) -> dict[date, CashBalanceSnapshot]:
    """Creates a timeseries from the current invested capital at each date in the series."""

    LOGGER.debug(
        "Generate series for %s transaction(s) at %s snapshot date(s).",
        len(transactions),
        len(series),
    )

    def sum_cash_balance(
        snapshot: CashBalanceSnapshot, transaction: CashTransaction
    ) -> CashBalanceSnapshot:
        snapshot[transaction.currency] += transaction.amount

        return snapshot

    def take_snapshot(
        snapshot: CashBalanceSnapshot, snapshot_date: date
    ) -> CashBalanceSnapshot:
        # pylint: disable=unused-argument

        return deepcopy(snapshot)

    return generate_snapshot_series(
        initial=CashBalanceSnapshot(),
        actions=transactions,
        series=series,
        operation=sum_cash_balance,
        take_snapshot=take_snapshot,
    )


def get_invested_capital_snapshot(
    portfolios: list[StockPortfolio], snapshot_date: date = date.today()
) -> CashBalanceSnapshot:
    """Returns the invested capital of the portfolio at a given time."""

    LOGGER.debug(
        "Calculate invested capital for %s portfolio at %s.",
        len(portfolios),
        snapshot_date,
    )

    cash_transactions = cast(
        list[CashTransaction],
        CashTransaction.objects.filter(
            portfolio__in=portfolios,
            date__lte=snapshot_date,
        ),
    )

    return get_invested_capital(cash_transactions, [snapshot_date])[snapshot_date]


def balance_to_usd(balance: CashBalanceSnapshot) -> float:
    """Converts each item in the cash balance to USD."""

    huf_usd_fx = 1 / float(cast(str, getenv("USD_HUF_FX_RATE")))
    eur_usd_fx = float(cast(str, getenv("EUR_USD_FX_RATE")))

    return balance.USD + balance.EUR * eur_usd_fx + balance.HUF * huf_usd_fx


def transaction_to_usd(transaction: CashTransaction) -> CashTransaction:
    """Converts a general transaction to a USD based transaction."""

    if transaction.currency == Currency.US_DOLLAR:
        return transaction

    if transaction.currency == Currency.EURO:
        eur_usd_fx = float(cast(str, getenv("EUR_USD_FX_RATE")))

        return CashTransaction(
            date=transaction.date,
            owner=transaction.owner,
            portfolio=transaction.portfolio,
            created_at=transaction.created_at,
            updated_at=transaction.updated_at,
            currency=Currency.US_DOLLAR,
            amount=transaction.amount * eur_usd_fx,
        )

    if transaction.currency == Currency.HUNGARIAN_FORINT:
        huf_usd_fx = 1 / float(cast(str, getenv("USD_HUF_FX_RATE")))

        return CashTransaction(
            date=transaction.date,
            owner=transaction.owner,
            portfolio=transaction.portfolio,
            created_at=transaction.created_at,
            updated_at=transaction.updated_at,
            currency=Currency.US_DOLLAR,
            amount=transaction.amount * huf_usd_fx,
        )

    raise Exception("Unknown currency.")
