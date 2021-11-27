"""Test cases for finance service."""

from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase, SimpleTestCase
from lib.enums import SyncStatus
from apps.raw_data.models import (
    StockDividend,
    StockDividendSync,
    StockPrice,
    StockPriceSync,
    StockSplit,
    StockSplitSync,
)
from apps.stocks.enums import Sector
from apps.stocks.models import Stock, StockPortfolio
from apps.transactions.models import StockTransaction

from ..dataclasses import StockPositionSnapshot, StockPortfolioSnapshot
from .finance import FinanceService


class TestPresentValue(SimpleTestCase):
    pass


class TestFutureValue(SimpleTestCase):
    pass


class TestRateOfInvestmentReturn(SimpleTestCase):
    """
    Different scenarios to check RRI calculation.
    Reference values took from excel.
    """

    def setUp(self):
        self.service = FinanceService()

    def test_one_year_period(self):
        self.assertEqual(self.service.rri(1, 100, 160), 0.6000)

    def test_multi_year_period(self):
        self.assertEqual(self.service.rri(3, 100, 160), 0.1696)

    def test_fractional_period(self):
        self.assertEqual(self.service.rri(0.3, 100, 160), 3.7907)

    def test_negative_return(self):
        self.assertEqual(self.service.rri(2, 100, 60), -0.2254)


class TestGetPortfolioSnapshot(TestCase):
    """Returns the snapshot of the portfolio at a given time."""

    def setUp(self):
        self.service = FinanceService()

    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(
            "owner", "owner@stock-buddy.com", "password"
        )
        cls.other_user = User.objects.create_user(
            "other", "other@stock-buddy.com", "password"
        )

        cls.msft = Stock.objects.create(
            active=True,
            name="Microsoft Corporation",
            ticker="MSFT",
            sector=Sector.SOFTWARE,
        )
        cls.pm = Stock.objects.create(
            active=True,
            name="Philip Morris International Inc.",
            ticker="PM",
            sector=Sector.CONSUMER_GOODS,
        )
        cls.baba = Stock.objects.create(
            active=True,
            name="Alibaba Group Holdings",
            ticker="BABA",
            sector=Sector.CONSUMER_SERVICES,
        )

        cls.portfolio = StockPortfolio.objects.create(
            name="Example portfolio", owner=cls.owner
        )
        cls.seconds_portfolio = StockPortfolio.objects.create(
            name="Second owned portfolio", owner=cls.owner
        )
        cls.other_users_portfolio = StockPortfolio.objects.create(
            name="Other user's portfolio", owner=cls.other_user
        )

        cls.price_sync = StockPriceSync.objects.create(
            owner=cls.owner, status=SyncStatus.FINISHED
        )
        cls.dividend_sync = StockDividendSync.objects.create(
            owner=cls.owner, status=SyncStatus.FINISHED
        )
        cls.split_sync = StockSplitSync.objects.create(
            owner=cls.owner, status=SyncStatus.FINISHED
        )

        StockPrice.objects.create(
            ticker=cls.msft, date=date(2021, 1, 1), value=89, sync=cls.price_sync
        )
        StockPrice.objects.create(
            ticker=cls.msft, date=date(2021, 1, 2), value=90, sync=cls.price_sync
        )
        StockPrice.objects.create(
            ticker=cls.pm, date=date(2021, 1, 1), value=46, sync=cls.price_sync
        )
        StockPrice.objects.create(
            ticker=cls.pm, date=date(2021, 1, 2), value=45, sync=cls.price_sync
        )
        StockPrice.objects.create(
            ticker=cls.baba, date=date(2021, 1, 1), value=150, sync=cls.price_sync
        )
        StockPrice.objects.create(
            ticker=cls.baba, date=date(2021, 1, 2), value=170, sync=cls.price_sync
        )

        StockDividend.objects.create(
            ticker=cls.pm,
            amount=2,
            payout_date=date(2021, 1, 1),
            sync=cls.dividend_sync,
        )

        StockSplit.objects.create(
            ticker=cls.pm,
            date=date(2021, 1, 9),
            ratio=2,
            sync=cls.split_sync,
        )

    def test_empty_portfolio(self):
        self.assertEqual(
            self.service.get_portfolio_snapshot([self.portfolio], date(2021, 1, 3)),
            StockPortfolioSnapshot(positions={}),
        )

    def test_summarize_distinct_buys(self):
        """
        Bought two distinct stocks. The portfolio should be the two of them.
        """

        StockTransaction.objects.create(
            amount=2,
            date=date(2021, 1, 2),
            ticker=self.msft,
            owner=self.owner,
            portfolio=self.portfolio,
            price=100.01,
        )
        StockTransaction.objects.create(
            amount=3,
            date=date(2021, 1, 2),
            ticker=self.pm,
            owner=self.owner,
            portfolio=self.portfolio,
            price=50.02,
        )

        result = self.service.get_portfolio_snapshot([self.portfolio], date(2021, 1, 3))

        self.assertEqual(result.number_of_positions, 2)
        self.assertEqual(
            result.positions[self.msft.ticker],
            StockPositionSnapshot(
                stock=self.msft,
                shares=2,
                price=90,
                dividend=0,
                purchase_price=100.01,
                first_purchase_date=date(2021, 1, 2),
                latest_purchase_date=date(2021, 1, 2),
            ),
        )
        self.assertEqual(
            result.positions[self.pm.ticker],
            StockPositionSnapshot(
                stock=self.pm,
                shares=3,
                price=45,
                dividend=8.0,
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
            ticker=self.msft,
            owner=self.owner,
            portfolio=self.portfolio,
            price=100.00,
        )
        StockTransaction.objects.create(
            amount=3,
            date=date(2021, 1, 2),
            ticker=self.msft,
            owner=self.owner,
            portfolio=self.portfolio,
            price=80.00,
        )

        result = self.service.get_portfolio_snapshot([self.portfolio], date(2021, 1, 3))

        self.assertEqual(result.number_of_positions, 1)
        self.assertEqual(
            result.positions[self.msft.ticker],
            StockPositionSnapshot(
                stock=self.msft,
                shares=5,
                price=90,
                dividend=0,
                purchase_price=88.00,
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
            ticker=self.msft,
            owner=self.owner,
            portfolio=self.portfolio,
            price=100.00,
        )
        StockTransaction.objects.create(
            amount=-2,
            date=date(2021, 1, 2),
            ticker=self.msft,
            owner=self.owner,
            portfolio=self.portfolio,
            price=80.00,
        )

        result = self.service.get_portfolio_snapshot([self.portfolio], date(2021, 1, 3))

        self.assertEqual(result.number_of_positions, 1)
        self.assertEqual(
            result.positions[self.msft.ticker],
            StockPositionSnapshot(
                stock=self.msft,
                shares=3,
                price=90,
                dividend=0,
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
            ticker=self.msft,
            owner=self.owner,
            portfolio=self.portfolio,
            price=100.00,
        )
        StockTransaction.objects.create(
            amount=3,
            date=date(2021, 1, 2),
            ticker=self.msft,
            owner=self.owner,
            portfolio=self.portfolio,
            price=80.00,
        )
        StockTransaction.objects.create(
            amount=-5,
            date=date(2021, 1, 3),
            ticker=self.msft,
            owner=self.owner,
            portfolio=self.portfolio,
            price=80.00,
        )

        result = self.service.get_portfolio_snapshot([self.portfolio], date(2021, 1, 3))

        self.assertEqual(result, StockPortfolioSnapshot(positions={}))

    def test_doesnt_contain_excluded_portfolios(self):
        """When requesting for one portfolio it shouldn't contain positions from other portfolios from the user."""

        StockTransaction.objects.create(
            amount=2,
            date=date(2021, 1, 2),
            ticker=self.msft,
            owner=self.owner,
            portfolio=self.portfolio,
            price=100.01,
        )
        StockTransaction.objects.create(
            amount=3,
            date=date(2021, 1, 2),
            ticker=self.pm,
            owner=self.owner,
            portfolio=self.portfolio,
            price=50.02,
        )
        StockTransaction.objects.create(
            amount=100,
            date=date(2021, 1, 2),
            ticker=self.msft,
            owner=self.owner,
            portfolio=self.seconds_portfolio,
            price=101,
        )
        StockTransaction.objects.create(
            amount=15,
            date=date(2021, 1, 2),
            ticker=self.baba,
            owner=self.owner,
            portfolio=self.seconds_portfolio,
            price=133,
        )

        result = self.service.get_portfolio_snapshot([self.portfolio], date(2021, 1, 3))

        self.assertEqual(result.number_of_positions, 2)
        self.assertEqual(
            result.positions[self.msft.ticker],
            StockPositionSnapshot(
                stock=self.msft,
                shares=2,
                price=90,
                dividend=0,
                purchase_price=100.01,
                first_purchase_date=date(2021, 1, 2),
                latest_purchase_date=date(2021, 1, 2),
            ),
        )
        self.assertEqual(
            result.positions[self.pm.ticker],
            StockPositionSnapshot(
                stock=self.pm,
                shares=3,
                price=45,
                dividend=8.0,
                purchase_price=50.02,
                first_purchase_date=date(2021, 1, 2),
                latest_purchase_date=date(2021, 1, 2),
            ),
        )
        self.assertNotIn(self.baba, (p.stock for p in result.positions.values()))

    def test_doesnt_containt_other_users_portfolio(self):
        """When requesting for a user's portfolios it shouldn't contain positions from other user's portfolios."""

        StockTransaction.objects.create(
            amount=2,
            date=date(2021, 1, 2),
            ticker=self.msft,
            owner=self.owner,
            portfolio=self.portfolio,
            price=100.01,
        )
        StockTransaction.objects.create(
            amount=3,
            date=date(2021, 1, 2),
            ticker=self.pm,
            owner=self.owner,
            portfolio=self.portfolio,
            price=50.02,
        )
        StockTransaction.objects.create(
            amount=100,
            date=date(2021, 1, 2),
            ticker=self.msft,
            owner=self.other_user,
            portfolio=self.other_users_portfolio,
            price=101,
        )
        StockTransaction.objects.create(
            amount=15,
            date=date(2021, 1, 2),
            ticker=self.baba,
            owner=self.other_user,
            portfolio=self.other_users_portfolio,
            price=133,
        )

        result = self.service.get_portfolio_snapshot([self.portfolio], date(2021, 1, 3))

        self.assertEqual(result.number_of_positions, 2)
        self.assertEqual(
            result.positions[self.msft.ticker],
            StockPositionSnapshot(
                stock=self.msft,
                shares=2,
                price=90,
                dividend=0,
                purchase_price=100.01,
                first_purchase_date=date(2021, 1, 2),
                latest_purchase_date=date(2021, 1, 2),
            ),
        )
        self.assertEqual(
            result.positions[self.pm.ticker],
            StockPositionSnapshot(
                stock=self.pm,
                shares=3,
                price=45,
                dividend=8.0,
                purchase_price=50.02,
                first_purchase_date=date(2021, 1, 2),
                latest_purchase_date=date(2021, 1, 2),
            ),
        )
        self.assertNotIn(self.baba, (p.stock for p in result.positions.values()))

    def test_could_handle_multiple_portfolios(self):
        """Request multiple portfolios. The result should be merged into a summary."""

        StockTransaction.objects.create(
            amount=2,
            date=date(2021, 1, 2),
            ticker=self.msft,
            owner=self.owner,
            portfolio=self.portfolio,
            price=100.01,
        )
        StockTransaction.objects.create(
            amount=3,
            date=date(2021, 1, 2),
            ticker=self.pm,
            owner=self.owner,
            portfolio=self.portfolio,
            price=50.02,
        )
        StockTransaction.objects.create(
            amount=100,
            date=date(2021, 1, 2),
            ticker=self.msft,
            owner=self.owner,
            portfolio=self.seconds_portfolio,
            price=101,
        )
        StockTransaction.objects.create(
            amount=15,
            date=date(2021, 1, 2),
            ticker=self.baba,
            owner=self.owner,
            portfolio=self.seconds_portfolio,
            price=133,
        )

        result = self.service.get_portfolio_snapshot(
            [self.portfolio, self.seconds_portfolio], date(2021, 1, 3)
        )

        self.assertEqual(result.number_of_positions, 3)
        self.assertEqual(
            result.positions[self.msft.ticker],
            StockPositionSnapshot(
                stock=self.msft,
                shares=102,
                price=90,
                dividend=0,
                purchase_price=100.98,
                first_purchase_date=date(2021, 1, 2),
                latest_purchase_date=date(2021, 1, 2),
            ),
        )
        self.assertEqual(
            result.positions[self.pm.ticker],
            StockPositionSnapshot(
                stock=self.pm,
                shares=3,
                price=45,
                dividend=8.0,
                purchase_price=50.02,
                first_purchase_date=date(2021, 1, 2),
                latest_purchase_date=date(2021, 1, 2),
            ),
        )
        self.assertEqual(
            result.positions[self.baba.ticker],
            StockPositionSnapshot(
                stock=self.baba,
                shares=15,
                price=170,
                dividend=0.0,
                purchase_price=133.0,
                first_purchase_date=date(2021, 1, 2),
                latest_purchase_date=date(2021, 1, 2),
            ),
        )

    def test_at_parameter_works_properly(self):
        """Transactions executed later that the snapshot date should not be considered."""

        StockTransaction.objects.create(
            amount=2,
            date=date(2021, 1, 2),
            ticker=self.msft,
            owner=self.owner,
            portfolio=self.portfolio,
            price=100.01,
        )
        StockTransaction.objects.create(
            amount=3,
            date=date(2021, 1, 2),
            ticker=self.pm,
            owner=self.owner,
            portfolio=self.portfolio,
            price=50.02,
        )
        StockTransaction.objects.create(
            amount=100,
            date=date(2021, 1, 5),
            ticker=self.msft,
            owner=self.owner,
            portfolio=self.portfolio,
            price=101,
        )
        StockTransaction.objects.create(
            amount=15,
            date=date(2021, 1, 6),
            ticker=self.baba,
            owner=self.owner,
            portfolio=self.portfolio,
            price=133,
        )

        result = self.service.get_portfolio_snapshot([self.portfolio], date(2021, 1, 3))

        self.assertEqual(result.number_of_positions, 2)
        self.assertEqual(
            result.positions[self.msft.ticker],
            StockPositionSnapshot(
                stock=self.msft,
                shares=2,
                price=90,
                dividend=0,
                purchase_price=100.01,
                first_purchase_date=date(2021, 1, 2),
                latest_purchase_date=date(2021, 1, 2),
            ),
        )
        self.assertEqual(
            result.positions[self.pm.ticker],
            StockPositionSnapshot(
                stock=self.pm,
                shares=3,
                price=45,
                dividend=8.0,
                purchase_price=50.02,
                first_purchase_date=date(2021, 1, 2),
                latest_purchase_date=date(2021, 1, 2),
            ),
        )
        self.assertNotIn(self.baba, (p.stock for p in result.positions.values()))

    def test_stock_splits_are_handled(self):
        """
        Initiate a position, then a stock split happens and then increase the position.

        The snapshot should represent the post split state if the snapshot date is after the split.
        (And ignore the split altogether if before.)
        """

        StockTransaction.objects.create(
            amount=2,
            date=date(2021, 1, 1),
            ticker=self.pm,
            owner=self.owner,
            portfolio=self.portfolio,
            price=90.00,
        )
        StockTransaction.objects.create(
            amount=3,
            date=date(2021, 1, 10),
            ticker=self.pm,
            owner=self.owner,
            portfolio=self.portfolio,
            price=50.00,
        )

        result = self.service.get_portfolio_snapshot(
            [self.portfolio], date(2021, 1, 10)
        )

        self.assertEqual(result.number_of_positions, 1)
        self.assertEqual(
            result.positions[self.pm.ticker],
            StockPositionSnapshot(
                stock=self.pm,
                shares=7,
                price=45,
                dividend=4.0,
                purchase_price=47.14,  # (4 * 45 + 3 * 50) / (4 + 3)
                first_purchase_date=date(2021, 1, 1),
                latest_purchase_date=date(2021, 1, 10),
            ),
        )
