"""Integration tests for the stocks API."""

from datetime import date

from django.test import TestCase
from rest_framework.test import APIClient
from core.test.seed import generate_test_data

from apps.stocks.models import Stock, StockPortfolio, StockWatchlist
from apps.transactions.models import StockTransaction


class TestStockList(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.STOCKS = data.STOCKS

        cls.url = "/stocks/"

    def test_cannot_access_unauthenticated(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_list_active_stocks(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.get(self.url)

        stocks_count = len(Stock.objects.filter(active=True))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), stocks_count)


class TestStockDetail(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.STOCKS = data.STOCKS

        cls.url = "/stocks/MSFT/"

    def test_cannot_access_unauthenticated(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_fetch_existing_stock(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["ticker"], "MSFT")
        self.assertEqual(response.data["name"], "Microsoft Corporation")
        self.assertEqual(response.data["sector"], "Software")

    def test_fetch_non_existent_stock(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.get("/stocks/KO/")

        self.assertEqual(response.status_code, 404)


class TestStockPortfolioList(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.USERS = data.USERS
        cls.PORTFOLIOS = data.PORTFOLIOS

        cls.url = "/stocks/portfolios/"

    def test_cannot_access_unauthenticated(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_list_only_owned_portfolios(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.get(self.url)

        owned_portfolio_count = len(
            StockPortfolio.objects.filter(owner=self.USERS.owner)
        )
        other_users_portfolio = StockPortfolio.objects.get(
            pk=self.PORTFOLIOS.other_users.id
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), owned_portfolio_count)
        # We can't see other user's portfolio when listing.
        self.assertNotIn(
            other_users_portfolio.id, [portfolio["id"] for portfolio in response.data]
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

        cls.url = f"/stocks/portfolios/{cls.PORTFOLIOS.main.id}/"

    def test_cannot_access_unauthenticated(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_fetch_portfolio_detail(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["owner"], self.USERS.owner.username)
        self.assertGreater(response.data["number_of_positions"], 0)

    def test_fetch_non_existent_portfolio(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.get("/stocks/portfolios/100/")

        self.assertEqual(response.status_code, 404)

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

    def test_cannot_access_unauthenticated(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_fetch_summary(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["owner"], self.USERS.owner.username)
        self.assertGreater(response.data["number_of_positions"], 0)

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


class TestStockWatchlistList(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.USERS = data.USERS
        cls.WATCHLISTS = data.WATCHLISTS

        cls.url = "/stocks/watchlists/"

    def test_cannot_access_unauthenticated(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_list_owned_watchlists(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.get(self.url)

        owned_watchlists_count = len(
            StockWatchlist.objects.filter(owner=self.USERS.owner)
        )
        other_users_watchlist = StockWatchlist.objects.get(
            pk=self.WATCHLISTS.other_users.id
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), owned_watchlists_count)
        self.assertNotIn(
            other_users_watchlist.id, [watchlist["id"] for watchlist in response.data]
        )


class TestStockWatchlistDetail(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.USERS = data.USERS
        cls.WATCHLISTS = data.WATCHLISTS

        cls.url = f"/stocks/watchlists/{cls.WATCHLISTS.main.id}/"

    def test_cannot_access_unauthenticated(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_fetch_watchlist_detail(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["owner"], self.USERS.owner.username)
        self.assertEqual(response.data["name"], "Example portfolio")

    def test_fetch_non_existent_portfolio(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.get("/stocks/watchlists/100/")

        self.assertEqual(response.status_code, 404)


class TestStockWatchlistCreate(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls) -> None:
        data = generate_test_data()
        cls.USERS = data.USERS
        cls.WATCHLISTS = data.WATCHLISTS

        cls.url = "/stocks/watchlists/"

    def test_cannot_access_unauthenticated(self):
        response = self.client.post(
            self.url,
            data={
                "name": "New portfolio",
                "description": "Description for the new portfolio.",
            },
        )

        self.assertEqual(response.status_code, 401)

    def test_create_new_watchlist(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        current_watchlists_count = len(
            StockWatchlist.objects.filter(owner=self.USERS.owner)
        )

        response = self.client.post(
            self.url,
            data={
                "name": "New portfolio",
                "description": "Description for the new portfolio.",
            },
        )

        updated_watchlists_count = len(
            StockWatchlist.objects.filter(owner=self.USERS.owner)
        )
        created_watchlist = StockWatchlist.objects.get(pk=response.data["id"])

        self.assertEqual(response.status_code, 201)
        self.assertEqual(updated_watchlists_count, current_watchlists_count + 1)
        self.assertEqual(created_watchlist.owner, self.USERS.owner)

    def test_malformed_payload(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        current_watchlists_count = len(
            StockWatchlist.objects.filter(owner=self.USERS.owner)
        )

        response = self.client.post(
            self.url,
            data={
                "description": "Description for the new portfolio.",
            },
        )

        updated_watchlists_count = len(
            StockWatchlist.objects.filter(owner=self.USERS.owner)
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(updated_watchlists_count, current_watchlists_count)


class TestStockWatchlistUpdate(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls) -> None:
        data = generate_test_data()
        cls.USERS = data.USERS
        cls.WATCHLISTS = data.WATCHLISTS

        cls.url = f"/stocks/watchlists/{cls.WATCHLISTS.main.id}/"

    def test_cannot_access_unauthenticated(self):
        response = self.client.put(
            self.url,
            data={
                "name": "Hello",
            },
        )

        self.assertEqual(response.status_code, 401)

    def test_update_watchlist(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.put(self.url, data={"name": "Hello"})

        self.assertEqual(response.status_code, 200)
        updated_watchlist = StockWatchlist.objects.get(pk=self.WATCHLISTS.main.id)
        self.assertEqual(updated_watchlist.name, "Hello")

    def test_cannot_update_other_users_watchlist(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        other_users_watchlist = StockWatchlist.objects.get(
            pk=self.WATCHLISTS.other_users.id
        )

        response = self.client.put(
            f"/stocks/watchlist/{other_users_watchlist.id}/", data={"name": "Hello"}
        )

        self.assertEqual(response.status_code, 404)
        other_users_updated_watchlist = StockWatchlist.objects.get(
            pk=self.WATCHLISTS.other_users.id
        )
        self.assertEqual(other_users_updated_watchlist.name, other_users_watchlist.name)

    def test_malformed_payload(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        watchlist = StockWatchlist.objects.get(pk=self.WATCHLISTS.main.id)

        response = self.client.put(self.url)

        self.assertEqual(response.status_code, 400)
        updated_watchlist = StockWatchlist.objects.get(pk=self.WATCHLISTS.main.id)
        self.assertEqual(updated_watchlist.name, watchlist.name)


class TestStockWatchlistDelete(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls) -> None:
        data = generate_test_data()
        cls.USERS = data.USERS
        cls.WATCHLISTS = data.WATCHLISTS

        cls.url = f"/stocks/watchlists/{cls.WATCHLISTS.main.id}/"

    def test_cannot_access_unauthenticated(self):
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 401)

    def test_delete_watchlist(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        current_watchlists_count = len(
            StockWatchlist.objects.filter(owner=self.USERS.owner)
        )

        response = self.client.delete(self.url)

        updated_watchlists_count = len(
            StockWatchlist.objects.filter(owner=self.USERS.owner)
        )

        self.assertEqual(response.status_code, 204)
        self.assertEqual(updated_watchlists_count, current_watchlists_count - 1)
        with self.assertRaises(StockWatchlist.DoesNotExist):
            StockWatchlist.objects.get(pk=self.WATCHLISTS.main.id)

    def test_delete_non_existent_watchlist(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.delete("/stocks/watchlists/100/")

        self.assertEqual(response.status_code, 404)

    def test_cannot_delete_other_users_watchlist(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        current_watchlists_count = len(
            StockWatchlist.objects.filter(owner=self.USERS.owner)
        )
        other_users_watchlist = StockWatchlist.objects.get(
            pk=self.WATCHLISTS.other_users.id
        )

        response = self.client.delete(f"/stocks/watchlist/{other_users_watchlist.id}/")

        updated_watchlists_count = len(
            StockWatchlist.objects.filter(owner=self.USERS.owner)
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(updated_watchlists_count, current_watchlists_count)
        other_users_updated_watchlist = StockWatchlist.objects.get(
            pk=self.WATCHLISTS.other_users.id
        )
        self.assertEqual(other_users_updated_watchlist.name, other_users_watchlist.name)
