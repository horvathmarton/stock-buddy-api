"""Test cases for cash service."""

from datetime import date
from django.test import TestCase

from apps.transactions.enums import Currency
from apps.transactions.models import CashTransaction, ForexTransaction, StockTransaction
from core.test.seed import generate_test_data
from lib.dataclasses import CashBalanceSnapshot
from lib.services.cash import CashService


class TestGetCashBalanceSnapshot(TestCase):
    """Returns the cash balance of the portfolio at a given time."""

    def setUp(self):
        self.service = CashService()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.USERS = data.USERS
        cls.PORTFOLIOS = data.PORTFOLIOS
        cls.STOCKS = data.STOCKS

    def test_empty_portfolio(self):
        self.assertEqual(
            self.service.get_portfolio_cash_balance(
                [self.PORTFOLIOS.main],
                date(2021, 1, 1),
            ),
            CashBalanceSnapshot(USD=0, EUR=0, HUF=0),
        )

    def test_summarize_different_currency_inflows(self):
        """
        Transfer money into the account twice in different currencies.

        Both should be presented in the balance.
        """

        CashTransaction.objects.create(
            currency=Currency.HUNGARIAN_FORINT,
            amount=1_000,
            date=date(2021, 1, 1),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )
        CashTransaction.objects.create(
            currency=Currency.US_DOLLAR,
            amount=100,
            date=date(2021, 1, 1),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )

        result = self.service.get_portfolio_cash_balance(
            [self.PORTFOLIOS.main], date(2021, 1, 1)
        )

        self.assertEqual(result, CashBalanceSnapshot(HUF=1_000, USD=100))

    def test_summarize_same_currency_inflows(self):
        """
        Transfer money into the account twice in the same currency.

        They should be added up on the balance.
        """

        CashTransaction.objects.create(
            currency=Currency.HUNGARIAN_FORINT,
            amount=1_000,
            date=date(2021, 1, 1),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )
        CashTransaction.objects.create(
            currency=Currency.HUNGARIAN_FORINT,
            amount=2_000,
            date=date(2021, 1, 1),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )

        result = self.service.get_portfolio_cash_balance(
            [self.PORTFOLIOS.main], date(2021, 1, 1)
        )

        self.assertEqual(result, CashBalanceSnapshot(HUF=3_000))

    def test_summarize_bidirectional_flows(self):
        """
        Transfer money into and out of the account in the same currency.

        They should be summed up on the balance.
        """

        CashTransaction.objects.create(
            currency=Currency.HUNGARIAN_FORINT,
            amount=3_000,
            date=date(2021, 1, 1),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )
        CashTransaction.objects.create(
            currency=Currency.HUNGARIAN_FORINT,
            amount=-1_000,
            date=date(2021, 1, 1),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )

        result = self.service.get_portfolio_cash_balance(
            [self.PORTFOLIOS.main], date(2021, 1, 1)
        )

        self.assertEqual(result, CashBalanceSnapshot(HUF=2_000))

    def test_doesnt_contain_excluded_portfolios(self):
        """When requesting for one portfolio it shouldn't contain transactions from other portfolios of the user."""

        CashTransaction.objects.create(
            currency=Currency.HUNGARIAN_FORINT,
            amount=3_000,
            date=date(2021, 1, 1),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )
        CashTransaction.objects.create(
            currency=Currency.HUNGARIAN_FORINT,
            amount=1_000,
            date=date(2021, 1, 1),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )
        CashTransaction.objects.create(
            currency=Currency.HUNGARIAN_FORINT,
            amount=1_000,
            date=date(2021, 1, 1),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.other,
        )

        result = self.service.get_portfolio_cash_balance(
            [self.PORTFOLIOS.main], date(2021, 1, 1)
        )

        self.assertEqual(result, CashBalanceSnapshot(HUF=4_000))

    def test_doesnt_contain_other_users_portfolio(self):
        """When requesting for a user's portfolios it shouldn't contain transactions from other user's portfolios."""

        CashTransaction.objects.create(
            currency=Currency.HUNGARIAN_FORINT,
            amount=3_000,
            date=date(2021, 1, 1),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )
        CashTransaction.objects.create(
            currency=Currency.HUNGARIAN_FORINT,
            amount=1_000,
            date=date(2021, 1, 1),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )
        CashTransaction.objects.create(
            currency=Currency.HUNGARIAN_FORINT,
            amount=2_000,
            date=date(2021, 1, 1),
            owner=self.USERS.other,
            portfolio=self.PORTFOLIOS.other_users,
        )

        result = self.service.get_portfolio_cash_balance(
            [self.PORTFOLIOS.main], date(2021, 1, 1)
        )

        self.assertEqual(result, CashBalanceSnapshot(HUF=4_000))

    def test_could_handle_multiple_portfolios(self):
        """Request multiple portfolios. The result should be merged into a summary."""

        CashTransaction.objects.create(
            currency=Currency.HUNGARIAN_FORINT,
            amount=3_000,
            date=date(2021, 1, 1),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )
        CashTransaction.objects.create(
            currency=Currency.HUNGARIAN_FORINT,
            amount=1_000,
            date=date(2021, 1, 1),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )
        CashTransaction.objects.create(
            currency=Currency.HUNGARIAN_FORINT,
            amount=1_000,
            date=date(2021, 1, 1),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.other,
        )
        CashTransaction.objects.create(
            currency=Currency.HUNGARIAN_FORINT,
            amount=1_000,
            date=date(2021, 1, 1),
            owner=self.USERS.other,
            portfolio=self.PORTFOLIOS.other_users,
        )

        result = self.service.get_portfolio_cash_balance(
            [self.PORTFOLIOS.main, self.PORTFOLIOS.other], date(2021, 1, 1)
        )

        self.assertEqual(result, CashBalanceSnapshot(HUF=5_000))

    def test_at_parameter_works_properly(self):
        """Transactions executed later than the snapshot date should not be considered."""

        CashTransaction.objects.create(
            currency=Currency.HUNGARIAN_FORINT,
            amount=3_000,
            date=date(2021, 1, 1),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )
        CashTransaction.objects.create(
            currency=Currency.HUNGARIAN_FORINT,
            amount=1_000,
            date=date(2021, 1, 1),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )
        CashTransaction.objects.create(
            currency=Currency.HUNGARIAN_FORINT,
            amount=1_000,
            date=date(2021, 1, 2),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )

        result = self.service.get_portfolio_cash_balance(
            [self.PORTFOLIOS.main, self.PORTFOLIOS.other], date(2021, 1, 1)
        )

        self.assertEqual(result, CashBalanceSnapshot(HUF=4_000))

    def test_forex_transaction_transfers(self):
        """
        Transfer into the account in two currencies and then execute a forex transaction within the account.

        The result should incorporate the forex transaction.
        """

        CashTransaction.objects.create(
            currency=Currency.HUNGARIAN_FORINT,
            amount=2_000,
            date=date(2021, 1, 1),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )
        CashTransaction.objects.create(
            currency=Currency.HUNGARIAN_FORINT,
            amount=2_000,
            date=date(2021, 1, 1),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )
        CashTransaction.objects.create(
            currency=Currency.EURO,
            amount=100,
            date=date(2021, 1, 1),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )

        ForexTransaction.objects.create(
            date=date(2021, 1, 1),
            amount=3_000,
            ratio=1 / 300,  # Exchange 3000 HUF to 10 EUR.
            source_currency=Currency.HUNGARIAN_FORINT,
            target_currency=Currency.EURO,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )

        result = self.service.get_portfolio_cash_balance(
            [self.PORTFOLIOS.main, self.PORTFOLIOS.other], date(2021, 1, 1)
        )

        self.assertEqual(result, CashBalanceSnapshot(EUR=110, HUF=1_000))

    def test_stock_purchase(self):
        """
        Transfer money into the account and then buy a stock.

        The result should be reduced with the purchase price.
        """

        CashTransaction.objects.create(
            currency=Currency.HUNGARIAN_FORINT,
            amount=45_000,
            date=date(2021, 1, 1),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )

        ForexTransaction.objects.create(
            date=date(2021, 1, 1),
            amount=45_000,
            ratio=1 / 300,  # Exchange 45000 HUF to 150 USD.
            source_currency=Currency.HUNGARIAN_FORINT,
            target_currency=Currency.US_DOLLAR,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )

        StockTransaction.objects.create(
            ticker=self.STOCKS.BABA,
            amount=1,
            price=100,
            date=date(2021, 1, 1),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )

        result = self.service.get_portfolio_cash_balance(
            [self.PORTFOLIOS.main, self.PORTFOLIOS.other], date(2021, 1, 1)
        )

        self.assertEqual(result, CashBalanceSnapshot(USD=50))

    def test_stock_sell(self):
        """
        Sell a stock then transfer money out of the account.

        The result should be increased by the selling price.
        """

        StockTransaction.objects.create(
            ticker=self.STOCKS.BABA,
            amount=-2,
            price=100,
            date=date(2021, 1, 1),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )

        CashTransaction.objects.create(
            currency=Currency.US_DOLLAR,
            amount=-150,
            date=date(2021, 1, 1),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )

        result = self.service.get_portfolio_cash_balance(
            [self.PORTFOLIOS.main, self.PORTFOLIOS.other], date(2021, 1, 1)
        )

        self.assertEqual(result, CashBalanceSnapshot(USD=50))

    def test_dividend_payout(self):
        """
        Holding a stock when it pays dividend.

        The dividend amount should be added to the ending balance.
        """

        CashTransaction.objects.create(
            currency=Currency.HUNGARIAN_FORINT,
            amount=90_000,
            date=date(2021, 1, 1),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )

        ForexTransaction.objects.create(
            date=date(2021, 1, 1),
            amount=90_000,
            ratio=1 / 300,  # Exchange 45000 HUF to 150 USD.
            source_currency=Currency.HUNGARIAN_FORINT,
            target_currency=Currency.US_DOLLAR,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )

        StockTransaction.objects.create(
            ticker=self.STOCKS.MSFT,
            amount=2,
            price=90,
            date=date(2021, 1, 1),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )

        result = self.service.get_portfolio_cash_balance(
            [self.PORTFOLIOS.main, self.PORTFOLIOS.other], date(2021, 1, 1)
        )

        self.assertEqual(result, CashBalanceSnapshot(USD=126))


class TestGetInvestedCapita(TestCase):
    """Returns the amount of invested capital into the portfolio at a given time."""

    def setUp(self):
        self.service = CashService()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.USERS = data.USERS
        cls.PORTFOLIOS = data.PORTFOLIOS
        cls.STOCKS = data.STOCKS

    def test_empty_portfolio(self):
        self.assertEqual(
            self.service.get_invested_capital(
                [self.PORTFOLIOS.main],
                date(2021, 1, 1),
            ),
            CashBalanceSnapshot(USD=0, EUR=0, HUF=0),
        )

    def test_summarize_inflow(self):
        """
        Transfer money into the account twice in the same currency.

        They should be added up on the balance.
        """

        CashTransaction.objects.create(
            currency=Currency.HUNGARIAN_FORINT,
            amount=1_000,
            date=date(2021, 1, 1),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )
        CashTransaction.objects.create(
            currency=Currency.HUNGARIAN_FORINT,
            amount=2_000,
            date=date(2021, 1, 1),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )

        result = self.service.get_invested_capital(
            [self.PORTFOLIOS.main], date(2021, 1, 1)
        )

        self.assertEqual(result, CashBalanceSnapshot(HUF=3_000))

    def test_summarize_bidirectional_flows(self):
        """
        Transfer money into and out of the account in the same currency.

        They should be summed up on the balance.
        """

        CashTransaction.objects.create(
            currency=Currency.HUNGARIAN_FORINT,
            amount=3_000,
            date=date(2021, 1, 1),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )
        CashTransaction.objects.create(
            currency=Currency.HUNGARIAN_FORINT,
            amount=-1_000,
            date=date(2021, 1, 1),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )

        result = self.service.get_invested_capital(
            [self.PORTFOLIOS.main], date(2021, 1, 1)
        )

        self.assertEqual(result, CashBalanceSnapshot(HUF=2_000))

    def test_ignore_internal_transactions(self):
        """
        - transfer money into the account
        - exchange to a different currency
        - buy a stock and sell it with profit
        - reinvest the increased capital to a new stock
        - withdraw some of the return

        The result should only reflect the external capital flows.
        """

        CashTransaction.objects.create(
            currency=Currency.HUNGARIAN_FORINT,
            amount=45_000,
            date=date(2021, 1, 1),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )

        ForexTransaction.objects.create(
            date=date(2021, 1, 1),
            amount=45_000,
            ratio=1 / 300,  # Exchange 45000 HUF to 150 USD.
            source_currency=Currency.HUNGARIAN_FORINT,
            target_currency=Currency.US_DOLLAR,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )

        StockTransaction.objects.create(
            ticker=self.STOCKS.BABA,
            amount=1,
            price=100,
            date=date(2021, 1, 1),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )
        StockTransaction.objects.create(
            ticker=self.STOCKS.BABA,
            amount=1,
            price=200,
            date=date(2021, 1, 2),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )
        StockTransaction.objects.create(
            ticker=self.STOCKS.MSFT,
            amount=1,
            price=90,
            date=date(2021, 1, 2),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )

        ForexTransaction.objects.create(
            date=date(2021, 1, 2),
            amount=60,
            ratio=300 / 1,  # Exchange 60 USD to 18000 HUF.
            source_currency=Currency.US_DOLLAR,
            target_currency=Currency.HUNGARIAN_FORINT,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )

        CashTransaction.objects.create(
            currency=Currency.HUNGARIAN_FORINT,
            amount=-18_000,
            date=date(2021, 1, 2),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )

        result = self.service.get_invested_capital(
            [self.PORTFOLIOS.main, self.PORTFOLIOS.other], date(2021, 1, 2)
        )

        self.assertEqual(result, CashBalanceSnapshot(HUF=45_000 - 18_000))
