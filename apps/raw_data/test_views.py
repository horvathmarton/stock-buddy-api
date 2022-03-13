"""Integration tests for the raw data API."""

from django.test import TestCase
from rest_framework.test import APIClient
from core.test.seed import generate_test_data
from lib.enums import SyncStatus

from apps.raw_data.models import (
    StockDividend,
    StockDividendSync,
    StockPrice,
    StockPriceSync,
    StockSplit,
    StockSplitSync,
)


class TestStockPriceSync(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.STOCKS = data.STOCKS

        cls.url = "/raw-data/stocks/MSFT/stock-prices"
        cls.payload = {
            "data": [
                {"date": "2021-01-03", "value": 91},
                {"date": "2021-01-03", "value": 91},
                {"date": "2021-01-04", "value": 92},
                {"date": "2021-01-05", "value": 90},
            ]
        }

    def test_cannot_access_unauthenticated(self):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 401)

    def test_investor_cannot_upload(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 403)

    def test_admin_cannot_upload(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="admin", password="password"
        )

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 403)

    def test_cannot_upload_to_non_existent(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="bot", password="password"
        )

        response = self.client.post(
            "/raw-data/stocks/AB/stock-prices", self.payload, format="json"
        )

        self.assertEqual(response.status_code, 404)

    def test_cannot_upload_non_json(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="bot", password="password"
        )

        response = self.client.post(self.url, self.payload, format="multipart")

        self.assertEqual(response.status_code, 400)

    def test_upload(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="bot", password="password"
        )

        current_syncs_count = len(StockPriceSync.objects.all())
        current_prices_count = len(StockPrice.objects.filter(ticker="MSFT"))

        response = self.client.post(self.url, self.payload, format="json")

        updated_syncs_count = len(StockPriceSync.objects.all())
        updated_prices_count = len(StockPrice.objects.filter(ticker="MSFT"))
        sync = StockPriceSync.objects.last()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(updated_syncs_count, current_syncs_count + 1)
        self.assertEqual(sync.status, SyncStatus.FINISHED)
        self.assertEqual(updated_prices_count, current_prices_count + 4)


class TestStockDividendSync(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.STOCKS = data.STOCKS

        cls.url = "/raw-data/stocks/MSFT/stock-dividends"
        cls.payload = {
            "data": [
                {"payout_date": "2021-01-03", "amount": 2},
                {"payout_date": "2021-01-05", "amount": 3},
            ]
        }

    def test_cannot_access_unauthenticated(self):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 401)

    def test_investor_cannot_upload(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 403)

    def test_admin_cannot_upload(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="admin", password="password"
        )

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 403)

    def test_cannot_upload_to_non_existent(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="bot", password="password"
        )

        response = self.client.post(
            "/raw-data/stocks/AB/stock-dividends", self.payload, format="json"
        )

        self.assertEqual(response.status_code, 404)

    def test_cannot_upload_non_json(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="bot", password="password"
        )

        response = self.client.post(self.url, self.payload, format="multipart")

        self.assertEqual(response.status_code, 400)

    def test_upload(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="bot", password="password"
        )

        current_syncs_count = len(StockDividendSync.objects.all())
        current_dividends_count = len(StockDividend.objects.filter(ticker="MSFT"))

        response = self.client.post(self.url, self.payload, format="json")

        updated_syncs_count = len(StockDividendSync.objects.all())
        updated_dividends_count = len(StockDividend.objects.filter(ticker="MSFT"))
        sync = StockDividendSync.objects.last()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(updated_syncs_count, current_syncs_count + 1)
        self.assertEqual(sync.status, SyncStatus.FINISHED)
        self.assertEqual(updated_dividends_count, current_dividends_count + 2)


class TestStockSplitSync(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.STOCKS = data.STOCKS

        cls.url = "/raw-data/stocks/MSFT/stock-splits"
        cls.payload = {
            "data": [
                {"date": "2021-01-10", "ratio": "1:2"},
                {"date": "2021-01-15", "ratio": "1:5"},
            ]
        }

    def test_cannot_access_unauthenticated(self):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 401)

    def test_investor_cannot_upload(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 403)

    def test_admin_cannot_upload(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="admin", password="password"
        )

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 403)

    def test_cannot_upload_to_non_existent(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="bot", password="password"
        )

        response = self.client.post(
            "/raw-data/stocks/AB/stock-splits", self.payload, format="json"
        )

        self.assertEqual(response.status_code, 404)

    def test_cannot_upload_non_json(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="bot", password="password"
        )

        response = self.client.post(self.url, self.payload, format="multipart")

        self.assertEqual(response.status_code, 400)

    def test_upload(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="bot", password="password"
        )

        current_syncs_count = len(StockSplitSync.objects.all())
        current_splits_count = len(StockSplit.objects.filter(ticker="MSFT"))

        response = self.client.post(self.url, self.payload, format="json")

        updated_syncs_count = len(StockSplitSync.objects.all())
        updated_splits_count = len(StockSplit.objects.filter(ticker="MSFT"))
        sync = StockSplitSync.objects.last()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(updated_syncs_count, current_syncs_count + 1)
        self.assertEqual(sync.status, SyncStatus.FINISHED)
        self.assertEqual(updated_splits_count, current_splits_count + 2)


class TestStockPriceStats(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        generate_test_data()

    def test_fetch_price_stats(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.get("/raw-data/stocks/stock-prices")

        self.assertEqual(response.status_code, 200)


class TestStockDividendStats(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        generate_test_data()

    def test_fetch_dividend_stats(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.get("/raw-data/stocks/stock-dividends")

        self.assertEqual(response.status_code, 200)


class TestStockSplitStats(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        generate_test_data()

    def test_fetch_split_stats(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.get("/raw-data/stocks/stock-splits")

        self.assertEqual(response.status_code, 200)
