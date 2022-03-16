"""A service to generate cash balance snapshots."""


from datetime import date
from logging import getLogger
from apps.raw_data.models import StockDividend

from apps.stocks.models import StockPortfolio
from apps.transactions.models import CashTransaction, ForexTransaction, StockTransaction
from lib.dataclasses import CashBalanceSnapshot
from lib.queries import sum_cash_transactions
from lib.services.stocks import StocksService


LOGGER = getLogger(__name__)


class CashService:
    """Cash balance snapshot generator."""

    def __init__(self):
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

        for transaction in dividend_payouts:
            # pylint: disable=fixme
            # TODO: This will be painfully slow for large dataset.
            # TODO: We need to find a better way to calculate.
            portfolio_snapshot = self.stocks_service.get_portfolio_snapshot(
                portfolios, snapshot_date=transaction.payout_date
            )

            position = portfolio_snapshot.positions.get(transaction.ticker.ticker, None)

            if position:
                balance.USD += transaction.amount * position.shares

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
