"""Test cases for cash service."""

from datetime import date
from os import environ

from django.test import TestCase
from src.lib.dataclasses import (
    CashBalanceSnapshot,
    StockPortfolioSnapshot,
    StockPositionSnapshot,
)
from src.lib.services.cash import (
    balance_to_usd,
    get_invested_capital,
    get_invested_capital_snapshot,
    get_portfolio_cash_balance,
    get_portfolio_cash_balance_snapshot,
    transaction_to_usd,
)
from src.raw_data.models import StockDividend
from src.transactions.enums import Currency
from src.transactions.models import CashTransaction, ForexTransaction, StockTransaction

from ...seed import generate_test_data


class TestGetPortfolioCashBalance(TestCase):
    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.USERS = data.USERS
        cls.PORTFOLIOS = data.PORTFOLIOS
        cls.STOCKS = data.STOCKS

        cls.snapshot_date = date(2022, 1, 1)
        cls.dividends = [
            StockDividend(ticker=cls.STOCKS.PM, date=date(2022, 1, 1), amount=10.0)
        ]
        cls.snapshots = {
            cls.snapshot_date: StockPortfolioSnapshot(
                positions={
                    "PM": StockPositionSnapshot(
                        stock=cls.STOCKS.PM,
                        shares=2,
                        price=100.0,
                        dividend=2.5,
                        purchase_price=10.0,
                        first_purchase_date=date(2021, 1, 1),
                        latest_purchase_date=date(2021, 6, 1),
                    )
                },
                date=cls.snapshot_date,
                owner=cls.USERS.owner,
            )
        }

    def test_empty(self):
        self.assertEqual(
            get_portfolio_cash_balance([], [], CashBalanceSnapshot(), {}), {}
        )

    def test_no_payouts(self):
        result = get_portfolio_cash_balance(
            [], [self.snapshot_date], CashBalanceSnapshot(), self.snapshots
        )

        self.assertEqual(result[self.snapshot_date], CashBalanceSnapshot())

    def test_no_series(self):
        result = get_portfolio_cash_balance(
            self.dividends, [], CashBalanceSnapshot(), self.snapshots
        )

        self.assertEqual(result, {})

    def test_generate_balance_series(self):

        result = get_portfolio_cash_balance(
            self.dividends, [self.snapshot_date], CashBalanceSnapshot(), self.snapshots
        )

        self.assertEqual(result[self.snapshot_date], CashBalanceSnapshot(USD=20.0))

    def test_use_initial(self):
        result = get_portfolio_cash_balance(
            self.dividends,
            [self.snapshot_date],
            CashBalanceSnapshot(USD=5.0),
            self.snapshots,
        )

        self.assertEqual(result[self.snapshot_date], CashBalanceSnapshot(USD=25.0))


class TestGetPortfolioCashBalanceSnapshot(TestCase):
    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.USERS = data.USERS
        cls.PORTFOLIOS = data.PORTFOLIOS
        cls.STOCKS = data.STOCKS

    def test_no_portfolios(self):
        self.assertEqual(
            get_portfolio_cash_balance_snapshot([], date(2021, 1, 1)),
            CashBalanceSnapshot(USD=0, EUR=0, HUF=0),
        )

    def test_empty_portfolio(self):
        self.assertEqual(
            get_portfolio_cash_balance_snapshot(
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

        result = get_portfolio_cash_balance_snapshot(
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

        result = get_portfolio_cash_balance_snapshot(
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

        result = get_portfolio_cash_balance_snapshot(
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

        result = get_portfolio_cash_balance_snapshot(
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

        result = get_portfolio_cash_balance_snapshot(
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

        result = get_portfolio_cash_balance_snapshot(
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

        result = get_portfolio_cash_balance_snapshot(
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

        result = get_portfolio_cash_balance_snapshot(
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

        result = get_portfolio_cash_balance_snapshot(
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

        result = get_portfolio_cash_balance_snapshot(
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
            ratio=1 / 300,  # Exchange 90000 HUF to 300 USD.
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

        result = get_portfolio_cash_balance_snapshot(
            [self.PORTFOLIOS.main, self.PORTFOLIOS.other], date(2021, 1, 1)
        )

        self.assertEqual(result, CashBalanceSnapshot(USD=126))


class TestGetInvestedCapital(TestCase):
    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.USERS = data.USERS
        cls.PORTFOLIOS = data.PORTFOLIOS
        cls.STOCKS = data.STOCKS

        cls.snapshot_date = date(2021, 1, 1)
        cls.transactions = [
            CashTransaction(
                currency=Currency.HUNGARIAN_FORINT,
                amount=1_000.0,
                date=date(2021, 1, 1),
                owner=cls.USERS.owner,
                portfolio=cls.PORTFOLIOS.main,
            ),
            CashTransaction(
                currency=Currency.HUNGARIAN_FORINT,
                amount=2_000.0,
                date=date(2021, 1, 1),
                owner=cls.USERS.owner,
                portfolio=cls.PORTFOLIOS.main,
            ),
        ]

    def test_empty_transactions(self):
        result = get_invested_capital([], [self.snapshot_date])

        self.assertEqual(
            result[self.snapshot_date], CashBalanceSnapshot(USD=0, EUR=0, HUF=0)
        )

    def test_empty_series(self):
        self.assertEqual(get_invested_capital(self.transactions, []), {})

    def test_summarize_inflow(self):
        """
        Transfer money into the account twice in the same currency.

        They should be added up on the balance.
        """

        result = get_invested_capital(self.transactions, [self.snapshot_date])

        self.assertEqual(result[self.snapshot_date], CashBalanceSnapshot(HUF=3_000))

    def test_summarize_bidirectional_flows(self):
        """
        Transfer money into and out of the account in the same currency.

        They should be summed up on the balance.
        """

        self.transactions = [
            CashTransaction(
                currency=Currency.HUNGARIAN_FORINT,
                amount=3_000.0,
                date=date(2021, 1, 1),
                owner=self.USERS.owner,
                portfolio=self.PORTFOLIOS.main,
            ),
            CashTransaction(
                currency=Currency.HUNGARIAN_FORINT,
                amount=-1_000.0,
                date=date(2021, 1, 1),
                owner=self.USERS.owner,
                portfolio=self.PORTFOLIOS.main,
            ),
        ]

        result = get_invested_capital(self.transactions, [self.snapshot_date])

        self.assertEqual(result[self.snapshot_date], CashBalanceSnapshot(HUF=2_000))


class TestGetInvestedCapitalSnapshot(TestCase):
    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.USERS = data.USERS
        cls.PORTFOLIOS = data.PORTFOLIOS
        cls.STOCKS = data.STOCKS

    def test_no_portfolios(self):
        self.assertEqual(
            get_invested_capital_snapshot([], date(2021, 1, 1)),
            CashBalanceSnapshot(USD=0, EUR=0, HUF=0),
        )

    def test_empty_portfolio(self):
        self.assertEqual(
            get_invested_capital_snapshot(
                [self.PORTFOLIOS.main],
                date(2021, 1, 1),
            ),
            CashBalanceSnapshot(USD=0, EUR=0, HUF=0),
        )

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

        result = get_invested_capital_snapshot([self.PORTFOLIOS.main], date(2021, 1, 1))

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

        result = get_invested_capital_snapshot(
            [self.PORTFOLIOS.main, self.PORTFOLIOS.other], date(2021, 1, 2)
        )

        self.assertEqual(result, CashBalanceSnapshot(HUF=45_000 - 18_000))


class TestBalanceToUsd(TestCase):
    def test_conversion(self):
        environ["USD_HUF_FX_RATE"] = "300"
        environ["EUR_USD_FX_RATE"] = "1.2"

        balance = CashBalanceSnapshot(USD=12, EUR=15, HUF=1500)

        self.assertEqual(balance_to_usd(balance), 35)


class TestTransactionToUsd(TestCase):
    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.USERS = data.USERS
        cls.PORTFOLIOS = data.PORTFOLIOS

    def test_convert_usd(self):
        transaction = CashTransaction(
            currency=Currency.US_DOLLAR,
            amount=100,
            date=date(2022, 1, 1),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )

        result = transaction_to_usd(transaction)

        self.assertEqual(result.currency, Currency.US_DOLLAR)
        self.assertEqual(result.amount, 100)

    def test_convert_eur(self):
        environ["EUR_USD_FX_RATE"] = "1.2"

        transaction = CashTransaction(
            currency=Currency.EURO,
            amount=10,
            date=date(2022, 1, 1),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )

        result = transaction_to_usd(transaction)

        self.assertEqual(result.currency, Currency.US_DOLLAR)
        self.assertEqual(result.amount, 12)

    def test_convert_huf(self):
        environ["USD_HUF_FX_RATE"] = "300"

        transaction = CashTransaction(
            currency=Currency.HUNGARIAN_FORINT,
            amount=3_000,
            date=date(2022, 1, 1),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )

        result = transaction_to_usd(transaction)

        self.assertEqual(result.currency, Currency.US_DOLLAR)
        self.assertEqual(result.amount, 10)
