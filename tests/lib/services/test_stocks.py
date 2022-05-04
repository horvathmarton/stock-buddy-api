"""Test cases for stocks service."""

from datetime import date

from django.test import TestCase
from src.lib.dataclasses import StockPortfolioSnapshot, StockPositionSnapshot
from src.lib.services.stocks import (
    get_all_stocks_since_inceptions,
    get_first_transaction,
    get_portfolio_snapshot,
)
from src.raw_data.models import StockPrice
from src.transactions.models import StockTransaction

from ...seed import generate_test_data


class TestGetPortfolioSnapshot(TestCase):
    """Returns the snapshot of the portfolio at a given time."""

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.USERS = data.USERS
        cls.STOCKS = data.STOCKS
        cls.PORTFOLIOS = data.PORTFOLIOS
        cls.SYNCS = data.STOCK_PRICE_SYNCS

    def test_empty_portfolio(self):
        self.assertEqual(
            get_portfolio_snapshot([self.PORTFOLIOS.main], date(2021, 1, 3)),
            StockPortfolioSnapshot(
                positions={}, owner=self.USERS.owner, snapshot_date=date(2021, 1, 3)
            ),
        )


class TestGetPortfolioSnapshotSeries(TestCase):
    """Returns a series of snapshots of the portfolio."""

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.USERS = data.USERS
        cls.STOCKS = data.STOCKS
        cls.PORTFOLIOS = data.PORTFOLIOS
        cls.SYNCS = data.STOCK_PRICE_SYNCS

    def test_empty_portfolios(self):
        self.assertEqual(
            get_portfolio_snapshot([self.PORTFOLIOS.main], date(2021, 1, 3)),
            StockPortfolioSnapshot(
                positions={}, owner=self.USERS.owner, snapshot_date=date(2021, 1, 3)
            ),
        )

    def test_summarize_distinct_buys(self):
        """
        Bought two distinct stocks. The portfolio should be the two of them.
        """

        StockTransaction.objects.create(
            amount=2,
            date=date(2021, 1, 2),
            ticker=self.STOCKS.MSFT,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
            price=100.01,
        )
        StockTransaction.objects.create(
            amount=3,
            date=date(2021, 1, 2),
            ticker=self.STOCKS.PM,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
            price=50.02,
        )

        result = get_portfolio_snapshot([self.PORTFOLIOS.main], date(2021, 1, 3))

        self.assertEqual(result.number_of_positions, 2)
        self.assertEqual(
            result.positions[self.STOCKS.MSFT.ticker],
            StockPositionSnapshot(
                stock=self.STOCKS.MSFT,
                shares=2,
                price=90,
                dividend=12.0,
                purchase_price=100.01,
                first_purchase_date=date(2021, 1, 2),
                latest_purchase_date=date(2021, 1, 2),
            ),
        )
        self.assertEqual(
            result.positions[self.STOCKS.PM.ticker],
            StockPositionSnapshot(
                stock=self.STOCKS.PM,
                shares=3,
                price=45,
                dividend=6.0,
                purchase_price=50.02,
                first_purchase_date=date(2021, 1, 2),
                latest_purchase_date=date(2021, 1, 2),
            ),
        )

    def test_summarize_position_increase(self):
        """
        Bought the same stock twice.
        The portfolio should be the sum in one position.
        """

        StockTransaction.objects.create(
            amount=2,
            date=date(2021, 1, 1),
            ticker=self.STOCKS.MSFT,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
            price=100.00,
        )
        StockTransaction.objects.create(
            amount=3,
            date=date(2021, 1, 2),
            ticker=self.STOCKS.MSFT,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
            price=80.00,
        )

        result = get_portfolio_snapshot([self.PORTFOLIOS.main], date(2021, 1, 3))

        self.assertEqual(result.number_of_positions, 1)
        self.assertEqual(
            result.positions[self.STOCKS.MSFT.ticker],
            StockPositionSnapshot(
                stock=self.STOCKS.MSFT,
                shares=5,
                price=90,
                dividend=12.0,
                purchase_price=88.0,
                first_purchase_date=date(2021, 1, 1),
                latest_purchase_date=date(2021, 1, 2),
            ),
        )

    def test_summarize_position_decrease(self):
        """
        Bought the stock and sold a part of the position.
        The portfolio should be the decreased amount.
        """

        StockTransaction.objects.create(
            amount=5,
            date=date(2021, 1, 1),
            ticker=self.STOCKS.MSFT,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
            price=100.00,
        )
        StockTransaction.objects.create(
            amount=-2,
            date=date(2021, 1, 2),
            ticker=self.STOCKS.MSFT,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
            price=80.00,
        )

        result = get_portfolio_snapshot([self.PORTFOLIOS.main], date(2021, 1, 3))

        self.assertEqual(result.number_of_positions, 1)
        self.assertEqual(
            result.positions[self.STOCKS.MSFT.ticker],
            StockPositionSnapshot(
                stock=self.STOCKS.MSFT,
                shares=3,
                price=90,
                dividend=12.0,
                purchase_price=100.00,
                first_purchase_date=date(2021, 1, 1),
                latest_purchase_date=date(2021, 1, 2),
            ),
        )

    def test_nullify_sold_position(self):
        """
        Bought a position and then sold out entirely.
        The portfolio should not contain the position.
        """

        StockTransaction.objects.create(
            amount=2,
            date=date(2021, 1, 1),
            ticker=self.STOCKS.MSFT,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
            price=100.00,
        )
        StockTransaction.objects.create(
            amount=3,
            date=date(2021, 1, 2),
            ticker=self.STOCKS.MSFT,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
            price=80.00,
        )
        StockTransaction.objects.create(
            amount=-5,
            date=date(2021, 1, 3),
            ticker=self.STOCKS.MSFT,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
            price=80.00,
        )

        result = get_portfolio_snapshot([self.PORTFOLIOS.main], date(2021, 1, 3))

        self.assertEqual(
            result,
            StockPortfolioSnapshot(
                positions={}, owner=self.USERS.owner, snapshot_date=date(2021, 1, 3)
            ),
        )

    def test_doesnt_contain_excluded_portfolios(self):
        """When requesting for one portfolio it shouldn't contain positions from other portfolios of the user."""

        StockTransaction.objects.create(
            amount=2,
            date=date(2021, 1, 2),
            ticker=self.STOCKS.MSFT,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
            price=100.01,
        )
        StockTransaction.objects.create(
            amount=3,
            date=date(2021, 1, 2),
            ticker=self.STOCKS.PM,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
            price=50.02,
        )
        StockTransaction.objects.create(
            amount=100,
            date=date(2021, 1, 2),
            ticker=self.STOCKS.MSFT,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.other,
            price=101,
        )
        StockTransaction.objects.create(
            amount=15,
            date=date(2021, 1, 2),
            ticker=self.STOCKS.BABA,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.other,
            price=133,
        )

        result = get_portfolio_snapshot([self.PORTFOLIOS.main], date(2021, 1, 3))

        self.assertEqual(result.number_of_positions, 2)
        self.assertEqual(
            result.positions[self.STOCKS.MSFT.ticker],
            StockPositionSnapshot(
                stock=self.STOCKS.MSFT,
                shares=2,
                price=90,
                dividend=12.0,
                purchase_price=100.01,
                first_purchase_date=date(2021, 1, 2),
                latest_purchase_date=date(2021, 1, 2),
            ),
        )
        self.assertEqual(
            result.positions[self.STOCKS.PM.ticker],
            StockPositionSnapshot(
                stock=self.STOCKS.PM,
                shares=3,
                price=45,
                dividend=6.0,
                purchase_price=50.02,
                first_purchase_date=date(2021, 1, 2),
                latest_purchase_date=date(2021, 1, 2),
            ),
        )
        self.assertNotIn(self.STOCKS.BABA, (p.stock for p in result.positions.values()))

    def test_doesnt_contain_other_users_portfolio(self):
        """When requesting for a user's portfolios it shouldn't contain positions from other user's portfolios."""

        StockTransaction.objects.create(
            amount=2,
            date=date(2021, 1, 2),
            ticker=self.STOCKS.MSFT,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
            price=100.01,
        )
        StockTransaction.objects.create(
            amount=3,
            date=date(2021, 1, 2),
            ticker=self.STOCKS.PM,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
            price=50.02,
        )
        StockTransaction.objects.create(
            amount=100,
            date=date(2021, 1, 2),
            ticker=self.STOCKS.MSFT,
            owner=self.USERS.other,
            portfolio=self.PORTFOLIOS.other_users,
            price=101,
        )
        StockTransaction.objects.create(
            amount=15,
            date=date(2021, 1, 2),
            ticker=self.STOCKS.BABA,
            owner=self.USERS.other,
            portfolio=self.PORTFOLIOS.other_users,
            price=133,
        )

        result = get_portfolio_snapshot([self.PORTFOLIOS.main], date(2021, 1, 3))

        self.assertEqual(result.number_of_positions, 2)
        self.assertEqual(
            result.positions[self.STOCKS.MSFT.ticker],
            StockPositionSnapshot(
                stock=self.STOCKS.MSFT,
                shares=2,
                price=90,
                dividend=12.0,
                purchase_price=100.01,
                first_purchase_date=date(2021, 1, 2),
                latest_purchase_date=date(2021, 1, 2),
            ),
        )
        self.assertEqual(
            result.positions[self.STOCKS.PM.ticker],
            StockPositionSnapshot(
                stock=self.STOCKS.PM,
                shares=3,
                price=45,
                dividend=6.0,
                purchase_price=50.02,
                first_purchase_date=date(2021, 1, 2),
                latest_purchase_date=date(2021, 1, 2),
            ),
        )
        self.assertNotIn(self.STOCKS.BABA, (p.stock for p in result.positions.values()))

    def test_could_handle_multiple_portfolios(self):
        """Request multiple portfolios. The result should be merged into a summary."""

        StockTransaction.objects.create(
            amount=2,
            date=date(2021, 1, 2),
            ticker=self.STOCKS.MSFT,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
            price=100.01,
        )
        StockTransaction.objects.create(
            amount=3,
            date=date(2021, 1, 2),
            ticker=self.STOCKS.PM,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
            price=50.02,
        )
        StockTransaction.objects.create(
            amount=100,
            date=date(2021, 1, 2),
            ticker=self.STOCKS.MSFT,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.other,
            price=101,
        )
        StockTransaction.objects.create(
            amount=15,
            date=date(2021, 1, 2),
            ticker=self.STOCKS.BABA,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.other,
            price=133,
        )

        result = get_portfolio_snapshot(
            [self.PORTFOLIOS.main, self.PORTFOLIOS.other], date(2021, 1, 3)
        )

        self.assertEqual(result.number_of_positions, 3)
        self.assertEqual(
            result.positions[self.STOCKS.MSFT.ticker],
            StockPositionSnapshot(
                stock=self.STOCKS.MSFT,
                shares=102,
                price=90,
                dividend=12.0,
                purchase_price=100.98,
                first_purchase_date=date(2021, 1, 2),
                latest_purchase_date=date(2021, 1, 2),
            ),
        )
        self.assertEqual(
            result.positions[self.STOCKS.PM.ticker],
            StockPositionSnapshot(
                stock=self.STOCKS.PM,
                shares=3,
                price=45,
                dividend=6.0,
                purchase_price=50.02,
                first_purchase_date=date(2021, 1, 2),
                latest_purchase_date=date(2021, 1, 2),
            ),
        )
        self.assertEqual(
            result.positions[self.STOCKS.BABA.ticker],
            StockPositionSnapshot(
                stock=self.STOCKS.BABA,
                shares=15,
                price=170,
                dividend=0.0,
                purchase_price=133.0,
                first_purchase_date=date(2021, 1, 2),
                latest_purchase_date=date(2021, 1, 2),
            ),
        )

    def test_at_parameter_works_properly(self):
        """Transactions executed later than the snapshot date should not be considered."""

        StockTransaction.objects.create(
            amount=2,
            date=date(2021, 1, 2),
            ticker=self.STOCKS.MSFT,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
            price=100.01,
        )
        StockTransaction.objects.create(
            amount=3,
            date=date(2021, 1, 2),
            ticker=self.STOCKS.PM,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
            price=50.02,
        )
        StockTransaction.objects.create(
            amount=100,
            date=date(2021, 1, 5),
            ticker=self.STOCKS.MSFT,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
            price=101,
        )
        StockTransaction.objects.create(
            amount=15,
            date=date(2021, 1, 6),
            ticker=self.STOCKS.BABA,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
            price=133,
        )

        result = get_portfolio_snapshot([self.PORTFOLIOS.main], date(2021, 1, 3))

        self.assertEqual(result.number_of_positions, 2)
        self.assertEqual(
            result.positions[self.STOCKS.MSFT.ticker],
            StockPositionSnapshot(
                stock=self.STOCKS.MSFT,
                shares=2,
                price=90,
                dividend=12.0,
                purchase_price=100.01,
                first_purchase_date=date(2021, 1, 2),
                latest_purchase_date=date(2021, 1, 2),
            ),
        )
        self.assertEqual(
            result.positions[self.STOCKS.PM.ticker],
            StockPositionSnapshot(
                stock=self.STOCKS.PM,
                shares=3,
                price=45,
                dividend=6.0,
                purchase_price=50.02,
                first_purchase_date=date(2021, 1, 2),
                latest_purchase_date=date(2021, 1, 2),
            ),
        )
        self.assertNotIn(self.STOCKS.BABA, (p.stock for p in result.positions.values()))

    def test_stock_splits_are_handled(self):
        """
        Initiate a position, then a stock split happens and then increase the position.

        The snapshot should represent the post split state if the snapshot date is after the split.
        (And ignore the split altogether if before.)
        """

        StockTransaction.objects.create(
            amount=2,
            date=date(2021, 1, 1),
            ticker=self.STOCKS.PM,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
            price=90.00,
        )
        StockTransaction.objects.create(
            amount=3,
            date=date(2021, 1, 10),
            ticker=self.STOCKS.PM,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
            price=50.00,
        )

        result = get_portfolio_snapshot([self.PORTFOLIOS.main], date(2021, 1, 10))

        self.assertEqual(result.number_of_positions, 1)
        self.assertEqual(
            result.positions[self.STOCKS.PM.ticker],
            StockPositionSnapshot(
                stock=self.STOCKS.PM,
                shares=7,
                price=45,
                dividend=3.0,
                purchase_price=47.14,  # (4 * 45 + 3 * 50) / (4 + 3)
                first_purchase_date=date(2021, 1, 1),
                latest_purchase_date=date(2021, 1, 10),
            ),
        )

    def test_selling_non_existent_position(self):
        """
        We sell a position from the portfolio that was non-existent.

        In this case we consider this a spinoff from another position and book the transaction,
        but consider it a non-existent position.
        """

        StockTransaction.objects.create(
            amount=-2,
            date=date(2021, 1, 1),
            ticker=self.STOCKS.PM,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
            price=90.0,
        )

        result = get_portfolio_snapshot([self.PORTFOLIOS.main], date(2021, 1, 2))

        self.assertEqual(result.number_of_positions, 0)

    def test_dividend_distribution_calculation(self):
        """
        Buy multiple stocks with dividend the snapshot should contain their dividend distribution.
        """

        StockTransaction.objects.create(
            amount=2,
            date=date(2021, 1, 2),
            ticker=self.STOCKS.MSFT,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
            price=100.01,
        )
        StockTransaction.objects.create(
            amount=3,
            date=date(2021, 1, 2),
            ticker=self.STOCKS.PM,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
            price=50.02,
        )

        result = get_portfolio_snapshot([self.PORTFOLIOS.main], date(2021, 1, 3))

        self.assertEqual(result.dividend, 42.0)
        self.assertEqual(result.dividend_distribution, {"MSFT": 0.5714, "PM": 0.4286})

    def test_annualized_pnl_calculation(self):
        """A snapshot contains annualized return calculation for each position."""

        StockTransaction.objects.create(
            amount=2,
            date=date(2010, 1, 1),
            ticker=self.STOCKS.MSFT,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
            price=28.18,
        )
        StockTransaction.objects.create(
            amount=3,
            date=date(2010, 1, 1),
            ticker=self.STOCKS.PM,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
            price=45.51,
        )

        StockPrice.objects.create(
            ticker=self.STOCKS.MSFT,
            date=date(2020, 1, 1),
            value=170.23,
            sync=self.SYNCS.main,
        )
        StockPrice.objects.create(
            ticker=self.STOCKS.PM,
            date=date(2020, 1, 1),
            value=82.70,
            sync=self.SYNCS.main,
        )

        result = get_portfolio_snapshot([self.PORTFOLIOS.main], date(2020, 1, 1))

        self.assertEqual(result.annualized_pnls, {"MSFT": 0.1970, "PM": 0.0615})

    def test_single_snapshot_date(self):
        StockTransaction.objects.create(
            amount=2,
            date=date(2021, 1, 1),
            ticker=self.STOCKS.MSFT,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
            price=100.01,
        )

        result = get_portfolio_snapshot([self.PORTFOLIOS.main], date(2021, 1, 3))

        self.assertEqual(date(2021, 1, 3), result.snapshot_date)


class TestGetAllStocksSinceInception(TestCase):
    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.USERS = data.USERS
        cls.STOCKS = data.STOCKS
        cls.PORTFOLIOS = data.PORTFOLIOS

    def test_empty_portfolios(self):
        result = get_all_stocks_since_inceptions(
            [self.PORTFOLIOS.main], date(2021, 1, 1)
        )

        self.assertEqual(len(result), 0)

    def test_single_transaction(self):
        StockTransaction.objects.create(
            amount=2,
            date=date(2021, 1, 1),
            ticker=self.STOCKS.MSFT,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
            price=100.01,
        )

        result = get_all_stocks_since_inceptions(
            [self.PORTFOLIOS.main], date(2021, 1, 1)
        )

        self.assertEqual(len(result), 1)
        self.assertEqual([stock["ticker"] for stock in result], ["MSFT"])

    def test_multiple_transactions(self):
        StockTransaction.objects.create(
            amount=2,
            date=date(2021, 1, 1),
            ticker=self.STOCKS.MSFT,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
            price=100.01,
        )
        StockTransaction.objects.create(
            amount=2,
            date=date(2021, 1, 1),
            ticker=self.STOCKS.PM,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
            price=100.01,
        )

        result = get_all_stocks_since_inceptions(
            [self.PORTFOLIOS.main], date(2021, 1, 1)
        )

        self.assertEqual(len(result), 2)
        self.assertEqual([stock["ticker"] for stock in result], ["MSFT", "PM"])

    def test_sold_stock(self):
        """The stock should remain in this list after sold."""

        StockTransaction.objects.create(
            amount=2,
            date=date(2021, 1, 1),
            ticker=self.STOCKS.MSFT,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
            price=100.01,
        )
        StockTransaction.objects.create(
            amount=2,
            date=date(2021, 1, 1),
            ticker=self.STOCKS.PM,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
            price=100.01,
        )
        StockTransaction.objects.create(
            amount=-2,
            date=date(2021, 1, 1),
            ticker=self.STOCKS.MSFT,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
            price=100.01,
        )

        result = get_all_stocks_since_inceptions(
            [self.PORTFOLIOS.main], date(2021, 1, 1)
        )

        self.assertEqual(len(result), 2)
        self.assertEqual([stock["ticker"] for stock in result], ["MSFT", "PM"])


class TestGetFirstTransaction(TestCase):
    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.USERS = data.USERS
        cls.STOCKS = data.STOCKS
        cls.PORTFOLIOS = data.PORTFOLIOS

    def test_no_transactions(self):
        self.assertEqual(get_first_transaction([self.PORTFOLIOS.main]), None)

    def test_single_transaction(self):
        transaction = StockTransaction.objects.create(
            amount=2,
            date=date(2021, 1, 1),
            ticker=self.STOCKS.MSFT,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
            price=100.01,
        )

        self.assertEqual(get_first_transaction([self.PORTFOLIOS.main]), transaction)

    def test_multiple_transactions(self):
        transaction = StockTransaction.objects.create(
            amount=2,
            date=date(2021, 1, 1),
            ticker=self.STOCKS.MSFT,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
            price=100.01,
        )
        StockTransaction.objects.create(
            amount=2,
            date=date(2021, 1, 2),
            ticker=self.STOCKS.MSFT,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
            price=100.01,
        )

        self.assertEqual(get_first_transaction([self.PORTFOLIOS.main]), transaction)
