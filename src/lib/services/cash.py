"""A service to generate cash balance snapshots."""


from datetime import date
from logging import getLogger
from os import getenv

from ...raw_data.models import StockDividend
from ...stocks.models import StockPortfolio
from ...transactions.models import CashTransaction
from ..dataclasses import CashBalanceSnapshot
from ..queries import sum_cash_transactions
from ..services.stocks import StocksService

LOGGER = getLogger(__name__)


class CashService:
    """Cash balance snapshot generator."""

    def __init__(self):
        # pylint: disable=missing-function-docstring

        self.stocks_service = StocksService()

    def get_portfolio_cash_balance(
        self, portfolios: list[StockPortfolio], snapshot_date: date = date.today()
    ) -> CashBalanceSnapshot:
        """Returns the cash balance of the portfolio at a given time."""

        LOGGER.debug("Generate cash balance snapshot for %s portfolio", len(portfolios))

        balance = CashBalanceSnapshot()

        usd, eur, huf = sum_cash_transactions(portfolios, snapshot_date)
        balance.USD = usd or 0
        balance.EUR = eur or 0
        balance.HUF = huf or 0

        owned_stocks = self.stocks_service.get_all_stocks_since_inceptions(
            portfolios, snapshot_date
        )
        first_transaction = self.stocks_service.get_first_transaction(portfolios)
        dividend_payouts = (
            StockDividend.objects.filter(
                ticker__in=owned_stocks,
                payout_date__lte=snapshot_date,
                payout_date__gte=first_transaction.date,
            )
            if first_transaction
            else []
        )

        snapshot_dates = list({dividend.payout_date for dividend in dividend_payouts})
        portfolio_snapshots = self.stocks_service.get_portfolio_snapshot_series(
            portfolios, snapshot_dates
        )

        for dividend in dividend_payouts:
            portfolio_snapshot = portfolio_snapshots[dividend.payout_date]

            position = portfolio_snapshot.positions.get(dividend.ticker.ticker, None)

            if position:
                balance.USD += dividend.amount * position.shares

        return balance

    @staticmethod
    def get_invested_capital(
        portfolios: list[StockPortfolio], snapshot_date: date = date.today()
    ) -> CashBalanceSnapshot:
        """Returns the invested capital of the portfolio at a given time."""

        LOGGER.debug("Calculate invested capital for %s portfolio", len(portfolios))

        balance = CashBalanceSnapshot()

        cash_transactions = CashTransaction.objects.filter(
            portfolio__in=portfolios,
            date__lte=snapshot_date,
        )

        for transaction in cash_transactions:
            balance[transaction.currency] += transaction.amount

        return balance

    @staticmethod
    def balance_to_usd(balance: CashBalanceSnapshot) -> float:
        """Converts each item in the cash balance to USD."""

        huf_usd_fx = 1 / float(getenv("USD_HUF_FX_RATE"))  # type: ignore
        eur_usd_fx = float(getenv("EUR_USD_FX_RATE"))  # type: ignore

        return balance.USD + balance.EUR * eur_usd_fx + balance.HUF * huf_usd_fx
