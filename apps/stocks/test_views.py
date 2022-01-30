"""Integration tests for the stocks API."""

from datetime import date

from django.test import TestCase
from rest_framework.test import APIClient
from core.test.seed import generate_test_data

from apps.transactions.models import StockTransaction


class TestStockPortfolioDetail(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.USERS = data.USERS
        cls.STOCKS = data.STOCKS
        cls.PORTFOLIOS = data.PORTFOLIOS
        cls.SYNCS = data.STOCK_PRICE_SYNCS

        StockTransaction.objects.create(
            amount=2,
            date=date(2021, 1, 1),
            ticker=cls.STOCKS.MSFT,
            owner=cls.USERS.owner,
            portfolio=cls.PORTFOLIOS.main,
            price=100.01,
        )

        cls.url = f"/stocks/portfolios/{cls.PORTFOLIOS.main.id}/"

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
        data = generate_test_data()
        cls.USERS = data.USERS
        cls.STOCKS = data.STOCKS
        cls.PORTFOLIOS = data.PORTFOLIOS

        StockTransaction.objects.create(
            amount=2,
            date=date(2021, 1, 1),
            ticker=cls.STOCKS.MSFT,
            owner=cls.USERS.owner,
            portfolio=cls.PORTFOLIOS.main,
            price=90.02,
        )
        StockTransaction.objects.create(
            amount=2,
            date=date(2020, 12, 31),
            ticker=cls.STOCKS.MSFT,
            owner=cls.USERS.owner,
            portfolio=cls.PORTFOLIOS.other,
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
