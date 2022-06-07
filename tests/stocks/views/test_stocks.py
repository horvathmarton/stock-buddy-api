"""Integration tests for the stocks API."""

from datetime import date

from django.test import TestCase
from rest_framework.test import APIClient
from src.auth.helpers import generate_token
from src.stocks.models import Stock, StockPortfolio
from src.transactions.models import StockTransaction

from ...seed import generate_test_data


class TestStockList(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.STOCKS = data.STOCKS

        cls.url = "/stocks"
        cls.token = generate_token(data.USERS.owner)

    def test_cannot_access_unauthenticated(self):
        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, 401)

    def test_list_active_stocks(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.get(self.url, follow=True)

        stocks_count = len(Stock.objects.filter(active=True))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), stocks_count)


class TestStockDetail(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.STOCKS = data.STOCKS

        cls.url = "/stocks/MSFT"
        cls.token = generate_token(data.USERS.owner)

    def test_cannot_access_unauthenticated(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_fetch_existing_stock(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["ticker"], "MSFT")
        self.assertEqual(response.data["name"], "Microsoft Corporation")
        self.assertEqual(response.data["sector"], "Software")

    def test_fetch_non_existent_stock(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.get("/stocks/KO")

        self.assertEqual(response.status_code, 404)


class TestStockPortfolioList(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.USERS = data.USERS
        cls.PORTFOLIOS = data.PORTFOLIOS

        cls.url = "/stocks/portfolios"
        cls.token = generate_token(data.USERS.owner)

    def test_cannot_access_unauthenticated(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_list_only_owned_portfolios(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.get(self.url)

        owned_portfolio_count = len(
            StockPortfolio.objects.filter(owner=self.USERS.owner)
        )
        other_users_portfolio = StockPortfolio.objects.get(
            pk=self.PORTFOLIOS.other_users.id
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), owned_portfolio_count)
        # We can't see other user's portfolio when listing.
        self.assertNotIn(
            other_users_portfolio.id,
            [portfolio["id"] for portfolio in response.data["results"]],
        )


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

        cls.url = f"/stocks/portfolios/{cls.PORTFOLIOS.main.id}"
        cls.token = generate_token(data.USERS.owner)

    def test_cannot_access_unauthenticated(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_fetch_portfolio_detail(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["owner"], self.USERS.owner.username)
        self.assertGreater(response.data["number_of_positions"], 0)

    def test_fetch_non_existent_portfolio(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.get("/stocks/portfolios/100")

        self.assertEqual(response.status_code, 404)

    def test_fetch_before_first_transaction(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.get(f"{self.url}?as_of=2020-12-31")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.data["detail"],
            "The portfolio has no transaction data before the selected date.",
        )

    def test_as_of_parameter(self):
        StockTransaction.objects.create(
            amount=2,
            date=date(2021, 1, 2),
            ticker=self.STOCKS.MSFT,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
            price=100.01,
        )

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.get(f"{self.url}?asOf=2021-01-01")

        self.assertEqual(response.status_code, 200)

    def test_cant_fetch_other_users_portfolio(self):
        StockTransaction.objects.create(
            amount=2,
            date=date(2021, 1, 1),
            ticker=self.STOCKS.PM,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.other_users,
            price=100.01,
        )

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.get(
            f"/stocks/portfolios/{self.PORTFOLIOS.other_users.id}"
        )

        self.assertEqual(response.status_code, 404)


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

        cls.url = "/stocks/portfolios/summary"
        cls.token = generate_token(data.USERS.owner)

    def test_cannot_access_unauthenticated(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_fetch_summary(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["owner"], self.USERS.owner.username)
        self.assertGreater(response.data["number_of_positions"], 0)

    def test_fetch_before_first_transaction_for_all_empty_portfolio(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.get(f"{self.url}?as_of=2020-12-30")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.data["detail"],
            "The portfolio has no transaction data before the selected date.",
        )

    def test_not_containing_other_users_portfolio(self):
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
            portfolio=self.PORTFOLIOS.other_users,
            price=100.01,
        )

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["number_of_positions"], 1)
        self.assertIn("MSFT", response.data["positions"])
        self.assertNotIn("PM", response.data["positions"])


class TestStockPortfolioCreate(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()

        cls.url = "/stocks/portfolios"
        cls.token = generate_token(data.USERS.owner)

    def test_cannot_access_unauthenticated(self):
        response = self.client.post(
            self.url,
            data={"name": "my-portfolio"},
            format="json",
        )

        self.assertEqual(response.status_code, 401)

    def test_cannot_post_malformed_payload(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.post(
            self.url,
            data={"hello": "my-portfolio"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_create_stock_portfolio(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.post(
            self.url,
            data={"name": "my-portfolio"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)


class TestStockPortfolioUpdate(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.PORTFOLIOS = data.PORTFOLIOS

        cls.url = f"/stocks/portfolios/{cls.PORTFOLIOS.main.id}"
        cls.token = generate_token(data.USERS.owner)

    def test_cannot_access_unauthenticated(self):
        response = self.client.patch(self.url)

        self.assertEqual(response.status_code, 401)

    def test_update_stock_portfolio_name(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.patch(
            self.url,
            data={"name": "my-portfolio-2"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)


class TestStockPortfolioDelete(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.PORTFOLIOS = data.PORTFOLIOS
        cls.STOCKS = data.STOCKS
        cls.USERS = data.USERS

        cls.url = f"/stocks/portfolios/{cls.PORTFOLIOS.main.id}"
        cls.token = generate_token(data.USERS.owner)

    def test_cannot_access_unauthenticated(self):
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 401)

    def test_cannot_delete_non_existent(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.delete("/stocks/portfolios/100")

        self.assertEqual(response.status_code, 404)

    def test_cannot_delete_other_users_portfolio(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.delete(
            f"/stocks/portfolios/{self.PORTFOLIOS.other_users.id}"
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_stock_portfolio(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 204)
