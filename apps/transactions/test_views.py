"""
Integration tests for the transactions API.

For now we only add authentication and smoke tests.
"""

from datetime import date
from django.test import TestCase
from rest_framework.test import APIClient
from apps.transactions.models import CashTransaction, ForexTransaction, StockTransaction

from core.test.seed import generate_test_data


class TestCashTransactionList(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()

        CashTransaction.objects.create(
            currency=12,
            amount=1,
            date=date(2021, 1, 1),
            owner=data.USERS.owner,
            portfolio=data.PORTFOLIOS.main,
        )

        cls.url = "/transactions/cash"

    def test_cannot_access_unauthenticated(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_list_cash_transactions(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)


class TestCashTransactionDetail(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()

        transaction = CashTransaction.objects.create(
            currency=12,
            amount=1,
            date=date(2021, 1, 1),
            owner=data.USERS.owner,
            portfolio=data.PORTFOLIOS.main,
        )

        cls.url = f"/transactions/cash/{transaction.id}"

    def test_cannot_access_unauthenticated(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_fetch_cash_transaction(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)


class TestCashTransactionCreate(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.PORTFOLIOS = data.PORTFOLIOS

        cls.url = "/transactions/cash"

    def test_cannot_access_unauthenticated(self):
        response = self.client.post(
            self.url,
            data={
                "currency": "HUF",
                "amount": 1_000,
                "date": date(2021, 1, 1),
                "portfolio": self.PORTFOLIOS.main.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 401)

    def test_create_cash_transaction(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.post(
            self.url,
            data={
                "currency": "HUF",
                "amount": 1_000,
                "date": date(2021, 1, 1),
                "portfolio": self.PORTFOLIOS.main.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)


class TestCashTransactionUpdate(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.PORTFOLIOS = data.PORTFOLIOS

        transaction = CashTransaction.objects.create(
            currency=12,
            amount=1,
            date=date(2021, 1, 1),
            owner=data.USERS.owner,
            portfolio=data.PORTFOLIOS.main,
        )

        cls.url = f"/transactions/cash/{transaction.id}"

    def test_cannot_access_unauthenticated(self):
        response = self.client.put(
            self.url,
            data={
                "currency": "HUF",
                "amount": 1_000,
                "date": date(2021, 1, 1),
                "portfolio": self.PORTFOLIOS.main.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 401)

    def test_update_cash_transaction(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.put(
            self.url,
            data={
                "currency": "HUF",
                "amount": 1_000,
                "date": date(2021, 1, 1),
                "portfolio": self.PORTFOLIOS.main.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)


class TestCashTransactionDelete(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.PORTFOLIOS = data.PORTFOLIOS

        transaction = CashTransaction.objects.create(
            currency=12,
            amount=1,
            date=date(2021, 1, 1),
            owner=data.USERS.owner,
            portfolio=data.PORTFOLIOS.main,
        )

        cls.url = f"/transactions/cash/{transaction.id}"

    def test_cannot_access_unauthenticated(self):
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 401)

    def test_delete_cash_transactions(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 204)


class TestForexTransactionList(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()

        ForexTransaction.objects.create(
            ratio=300,
            amount=10,
            source_currency="USD",
            target_currency="HUF",
            date=date(2021, 1, 1),
            owner=data.USERS.owner,
            portfolio=data.PORTFOLIOS.main,
        )

        cls.url = "/transactions/forex"

    def test_cannot_access_unauthenticated(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_list_forex_transactions(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)


class TestForexTransactionDetail(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()

        transaction = ForexTransaction.objects.create(
            ratio=300,
            amount=10,
            source_currency="USD",
            target_currency="HUF",
            date=date(2021, 1, 1),
            owner=data.USERS.owner,
            portfolio=data.PORTFOLIOS.main,
        )

        cls.url = f"/transactions/forex/{transaction.id}"

    def test_cannot_access_unauthenticated(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_fetch_forex_transaction(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)


class TestForexTransactionCreate(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.PORTFOLIOS = data.PORTFOLIOS

        cls.url = "/transactions/forex"

    def test_cannot_access_unauthenticated(self):
        response = self.client.post(
            self.url,
            data={
                "ratio": 300,
                "source_currency": "USD",
                "target_currency": "HUF",
                "amount": 10,
                "date": date(2021, 1, 1),
                "portfolio": self.PORTFOLIOS.main.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 401)

    def test_fetch_forex_transaction(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.post(
            self.url,
            data={
                "ratio": 300,
                "source_currency": "USD",
                "target_currency": "HUF",
                "amount": 10,
                "date": date(2021, 1, 1),
                "portfolio": self.PORTFOLIOS.main.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)


class TestForexTransactionUpdate(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.PORTFOLIOS = data.PORTFOLIOS

        transaction = ForexTransaction.objects.create(
            ratio=300,
            amount=10,
            source_currency="USD",
            target_currency="HUF",
            date=date(2021, 1, 1),
            owner=data.USERS.owner,
            portfolio=data.PORTFOLIOS.main,
        )

        cls.url = f"/transactions/forex/{transaction.id}"

    def test_cannot_access_unauthenticated(self):
        response = self.client.put(
            self.url,
            data={
                "ratio": 300,
                "source_currency": "USD",
                "target_currency": "HUF",
                "amount": 15,
                "date": date(2021, 1, 1),
                "portfolio": self.PORTFOLIOS.main.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 401)

    def test_update_forex_transaction(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.put(
            self.url,
            data={
                "ratio": 300,
                "source_currency": "USD",
                "target_currency": "HUF",
                "amount": 15,
                "date": date(2021, 1, 1),
                "portfolio": self.PORTFOLIOS.main.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)


class TestForexTransactionDelete(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.PORTFOLIOS = data.PORTFOLIOS

        transaction = ForexTransaction.objects.create(
            ratio=300,
            amount=10,
            source_currency="USD",
            target_currency="HUF",
            date=date(2021, 1, 1),
            owner=data.USERS.owner,
            portfolio=data.PORTFOLIOS.main,
        )

        cls.url = f"/transactions/forex/{transaction.id}"

    def test_cannot_access_unauthenticated(self):
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 401)

    def test_delete_forex_transactions(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 204)


class TestStocksTransactionList(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()

        StockTransaction.objects.create(
            ticker=data.STOCKS.MSFT,
            amount=1,
            price=100,
            date=date(2021, 1, 1),
            owner=data.USERS.owner,
            portfolio=data.PORTFOLIOS.main,
        )

        cls.url = "/transactions/stocks"

    def test_cannot_access_unauthenticated(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_list_stock_transactions(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)


class TestStocksTransactionDetail(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()

        transaction = StockTransaction.objects.create(
            ticker=data.STOCKS.MSFT,
            amount=1,
            price=100,
            date=date(2021, 1, 1),
            owner=data.USERS.owner,
            portfolio=data.PORTFOLIOS.main,
        )

        cls.url = f"/transactions/stocks/{transaction.id}"

    def test_cannot_access_unauthenticated(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_fetch_stock_transaction(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)


class TestStocksTransactionCreate(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.PORTFOLIOS = data.PORTFOLIOS

        cls.url = "/transactions/stocks"

    def test_cannot_access_unauthenticated(self):
        response = self.client.post(
            self.url,
            data={
                "ticker": "MSFT",
                "amount": 1,
                "price": 100,
                "date": date(2021, 1, 1),
                "portfolio": self.PORTFOLIOS.main.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 401)

    def test_fetch_stock_transaction(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.post(
            self.url,
            data={
                "ticker": "MSFT",
                "amount": 1,
                "price": 100,
                "date": date(2021, 1, 1),
                "portfolio": self.PORTFOLIOS.main.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)


class TestStocksTransactionUpdate(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.PORTFOLIOS = data.PORTFOLIOS

        transaction = StockTransaction.objects.create(
            ticker=data.STOCKS.MSFT,
            amount=1,
            price=100,
            date=date(2021, 1, 1),
            owner=data.USERS.owner,
            portfolio=data.PORTFOLIOS.main,
        )

        cls.url = f"/transactions/stocks/{transaction.id}"

    def test_cannot_access_unauthenticated(self):
        response = self.client.put(
            self.url,
            data={
                "ticker": "MSFT",
                "amount": 1,
                "price": 100,
                "date": date(2021, 1, 1),
                "portfolio": self.PORTFOLIOS.main.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 401)

    def test_update_stock_transaction(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.put(
            self.url,
            data={
                "ticker": "MSFT",
                "amount": 1,
                "price": 100,
                "date": date(2021, 1, 1),
                "portfolio": self.PORTFOLIOS.main.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)


class TestStocksTransactionDelete(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.PORTFOLIOS = data.PORTFOLIOS

        transaction = StockTransaction.objects.create(
            ticker=data.STOCKS.MSFT,
            amount=1,
            price=100,
            date=date(2021, 1, 1),
            owner=data.USERS.owner,
            portfolio=data.PORTFOLIOS.main,
        )

        cls.url = f"/transactions/stocks/{transaction.id}"

    def test_cannot_access_unauthenticated(self):
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 401)

    def test_delete_stock_transactions(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 204)
