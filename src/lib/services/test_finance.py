from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from src.lib.enums import SyncStatus
from src.raw_data.models import (
    StockDividend,
    StockDividendSync,
    StockPrice,
    StockPriceSync,
)
from src.stocks.enums import Sector
from src.stocks.models import Stock, StockPortfolio
from src.transactions.models import StockTransaction

from ..dataclasses import StockPosition
from .finance import FinanceService


class TestFinanceGetPortfolioSnapshot(TestCase):
    """
    Returns the snapshot of the portfolio at a given time.
    """

    def setUp(self):
        self.service = FinanceService()

    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(
            "owner", "owner@stock-buddy.com", "password"
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

        cls.portfolio = StockPortfolio.objects.create(
            name="Example portfolio", owner=cls.owner
        )

        cls.price_sync = StockPriceSync.objects.create(
            owner=cls.owner, status=SyncStatus.FINISHED
        )
        cls.dividend_sync = StockDividendSync.objects.create(
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

        StockDividend.objects.create(
            ticker=cls.pm,
            amount=2,
            payout_date=date(2021, 1, 1),
            sync=cls.dividend_sync,
        )

    def test_empty_portfolio(self):
        self.assertEqual(
            self.service.get_portfolio_snapshot(self.portfolio, date(2021, 1, 3)), []
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

        result = self.service.get_portfolio_snapshot(self.portfolio, date(2021, 1, 3))

        self.assertEqual(len(result), 2)
        self.assertEqual(
            result[0],
            StockPosition(
                stock=self.msft,
                shares=2,
                price=90,
                dividend=0,
                purchase_price=100.01,
                purchase_date=date(2021, 1, 2),
            ),
        )
        self.assertEqual(
            result[1],
            StockPosition(
                stock=self.pm,
                shares=3,
                price=45,
                dividend=8.0,
                purchase_price=50.02,
                purchase_date=date(2021, 1, 2),
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

        result = self.service.get_portfolio_snapshot(self.portfolio, date(2021, 1, 3))

        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[0],
            StockPosition(
                stock=self.msft,
                shares=5,
                price=90,
                dividend=0,
                purchase_price=88.00,
                purchase_date=date(2021, 1, 2),
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

        result = self.service.get_portfolio_snapshot(self.portfolio, date(2021, 1, 3))

        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[0],
            StockPosition(
                stock=self.msft,
                shares=3,
                price=90,
                dividend=0,
                purchase_price=100.00,
                purchase_date=date(2021, 1, 2),
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

        result = self.service.get_portfolio_snapshot(self.portfolio, date(2021, 1, 3))

        self.assertEqual(result, [])
