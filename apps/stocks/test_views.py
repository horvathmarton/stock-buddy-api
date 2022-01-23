"""Integration tests for the stocks API."""

from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from apps.raw_data.models import StockPrice, StockPriceSync
from apps.stocks.enums import Sector
from apps.stocks.models import Stock, StockPortfolio
from apps.transactions.models import StockTransaction
from lib.enums import SyncStatus


class TestStockPortfolioDetail(TestCase):
    def setUp(self):
        self.client = APIClient()

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

        cls.portfolio = StockPortfolio.objects.create(
            name="Example portfolio", owner=cls.owner
        )

        cls.price_sync = StockPriceSync.objects.create(
            owner=cls.owner, status=SyncStatus.FINISHED
        )

        StockPrice.objects.create(
            ticker=cls.msft, date=date(2021, 1, 1), value=89, sync=cls.price_sync
        )

        StockTransaction.objects.create(
            amount=2,
            date=date(2021, 1, 1),
            ticker=cls.msft,
            owner=cls.owner,
            portfolio=cls.portfolio,
            price=100.01,
        )

        cls.url = f"/stocks/portfolios/{cls.portfolio.id}/"

    def test_fetch_before_first_transaction(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner",
            password="password",
        )
        response = self.client.get(f"{self.url}?asOf=2020-12-31")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.data["detail"],
            "The portfolio has no transaction data before the selected date.",
        )


class TestStockPortfolioSummary(TestCase):
    def setUp(self):
        self.client = APIClient()

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

        cls.portfolio = StockPortfolio.objects.create(
            name="Example portfolio", owner=cls.owner
        )
        cls.other_portfolio = StockPortfolio.objects.create(
            name="Other portfolio", owner=cls.owner
        )

        cls.price_sync = StockPriceSync.objects.create(
            owner=cls.owner, status=SyncStatus.FINISHED
        )

        StockPrice.objects.create(
            ticker=cls.msft, date=date(2020, 12, 31), value=89, sync=cls.price_sync
        )
        StockPrice.objects.create(
            ticker=cls.msft, date=date(2021, 1, 1), value=89, sync=cls.price_sync
        )

        StockTransaction.objects.create(
            amount=2,
            date=date(2021, 1, 1),
            ticker=cls.msft,
            owner=cls.owner,
            portfolio=cls.portfolio,
            price=90.02,
        )
        StockTransaction.objects.create(
            amount=2,
            date=date(2020, 12, 31),
            ticker=cls.msft,
            owner=cls.owner,
            portfolio=cls.other_portfolio,
            price=100.01,
        )

        cls.url = "/stocks/portfolios/summary/"

    def test_fetch_before_first_transaction_for_all_empty_portfolio(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner",
            password="password",
        )
        response = self.client.get(f"{self.url}?asOf=2020-12-30")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.data["detail"],
            "The portfolio has no transaction data before the selected date.",
        )
