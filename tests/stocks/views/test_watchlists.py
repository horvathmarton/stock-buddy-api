"""Integration tests for the watchlists API."""

from django.test import TestCase
from rest_framework.test import APIClient
from src.auth.helpers import generate_token
from src.stocks.models import StockWatchlist

from ...seed import generate_test_data


class TestStockWatchlistList(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.USERS = data.USERS
        cls.WATCHLISTS = data.WATCHLISTS

        cls.url = "/stocks/watchlists"
        cls.token = generate_token(data.USERS.owner)

    def test_cannot_access_unauthenticated(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_list_owned_watchlists(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

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
        cls.STOCKS = data.STOCKS

        cls.url = f"/stocks/watchlists/{cls.WATCHLISTS.main.id}"
        cls.token = generate_token(data.USERS.owner)

    def test_cannot_access_unauthenticated(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_fetch_watchlist_detail(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Example portfolio")
        self.assertEqual(len(response.data["items"]), 2)

        google = next(
            item
            for item in response.data["items"]
            if item["ticker"] == self.STOCKS.GOOGL.ticker
        )

        self.assertEqual(len(google["target_prices"]), 2)
        self.assertEqual(len(google["position_sizes"]), 2)

        apple = next(
            item
            for item in response.data["items"]
            if item["ticker"] == self.STOCKS.AAPL.ticker
        )

        self.assertEqual(len(apple["target_prices"]), 1)
        self.assertEqual(len(apple["position_sizes"]), 1)

    def test_fetch_non_existent_portfolio(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.get("/stocks/watchlists/100")

        self.assertEqual(response.status_code, 404)


class TestStockWatchlistCreate(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.USERS = data.USERS
        cls.WATCHLISTS = data.WATCHLISTS

        cls.url = "/stocks/watchlists"
        cls.token = generate_token(data.USERS.owner)

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
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

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
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

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
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.USERS = data.USERS
        cls.WATCHLISTS = data.WATCHLISTS

        cls.url = f"/stocks/watchlists/{cls.WATCHLISTS.main.id}"
        cls.token = generate_token(data.USERS.owner)

    def test_cannot_access_unauthenticated(self):
        response = self.client.put(
            self.url,
            data={
                "name": "Hello",
            },
        )

        self.assertEqual(response.status_code, 401)

    def test_update_watchlist(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.put(self.url, data={"name": "Hello"})

        self.assertEqual(response.status_code, 200)
        updated_watchlist = StockWatchlist.objects.get(pk=self.WATCHLISTS.main.id)
        self.assertEqual(updated_watchlist.name, "Hello")

    def test_cannot_update_other_users_watchlist(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        other_users_watchlist = StockWatchlist.objects.get(
            pk=self.WATCHLISTS.other_users.id
        )

        response = self.client.put(
            f"/stocks/watchlist/{other_users_watchlist.id}", data={"name": "Hello"}
        )

        self.assertEqual(response.status_code, 404)
        other_users_updated_watchlist = StockWatchlist.objects.get(
            pk=self.WATCHLISTS.other_users.id
        )
        self.assertEqual(other_users_updated_watchlist.name, other_users_watchlist.name)

    def test_malformed_payload(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        watchlist = StockWatchlist.objects.get(pk=self.WATCHLISTS.main.id)

        response = self.client.put(self.url)

        self.assertEqual(response.status_code, 400)
        updated_watchlist = StockWatchlist.objects.get(pk=self.WATCHLISTS.main.id)
        self.assertEqual(updated_watchlist.name, watchlist.name)


class TestStockWatchlistDelete(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.USERS = data.USERS
        cls.WATCHLISTS = data.WATCHLISTS

        cls.url = f"/stocks/watchlists/{cls.WATCHLISTS.main.id}"
        cls.token = generate_token(data.USERS.owner)

    def test_cannot_access_unauthenticated(self):
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 401)

    def test_delete_watchlist(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

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
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.delete("/stocks/watchlists/100")

        self.assertEqual(response.status_code, 404)

    def test_cannot_delete_other_users_watchlist(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        current_watchlists_count = len(
            StockWatchlist.objects.filter(owner=self.USERS.owner)
        )
        other_users_watchlist = StockWatchlist.objects.get(
            pk=self.WATCHLISTS.other_users.id
        )

        response = self.client.delete(f"/stocks/watchlist/{other_users_watchlist.id}")

        updated_watchlists_count = len(
            StockWatchlist.objects.filter(owner=self.USERS.owner)
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(updated_watchlists_count, current_watchlists_count)
        other_users_updated_watchlist = StockWatchlist.objects.get(
            pk=self.WATCHLISTS.other_users.id
        )
        self.assertEqual(other_users_updated_watchlist.name, other_users_watchlist.name)


class TestStockWatchlistManagementCreate(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.USERS = data.USERS
        cls.WATCHLISTS = data.WATCHLISTS
        cls.STOCKS = data.STOCKS

        cls.url = f"/stocks/watchlists/{cls.WATCHLISTS.main.id}/stocks/{cls.STOCKS.BABA.ticker}"
        cls.token = generate_token(data.USERS.owner)

    def test_cannot_access_unauthenticated(self):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 401)

    def test_add_new_stock(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.STOCKS.BABA.ticker, response.data["stocks"])

    def test_cannot_add_duplicate(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.post(
            f"/stocks/watchlists/{self.WATCHLISTS.main.id}/stocks/{self.STOCKS.GOOGL.ticker}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.STOCKS.GOOGL.ticker, response.data["stocks"])
        self.assertEqual(response.data["stocks"].count(self.STOCKS.GOOGL.ticker), 1)

    def test_cannot_add_to_another_users_watchlist(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.post(
            f"/stocks/watchlists/{self.WATCHLISTS.other_users.id}/stocks/{self.STOCKS.GOOGL.ticker}"
        )

        self.assertEqual(response.status_code, 403)


class TestStockWatchlistManagementDelete(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.USERS = data.USERS
        cls.WATCHLISTS = data.WATCHLISTS
        cls.STOCKS = data.STOCKS

        cls.url = f"/stocks/watchlists/{cls.WATCHLISTS.main.id}/stocks/{cls.STOCKS.GOOGL.ticker}"
        cls.token = generate_token(data.USERS.owner)

    def test_cannot_access_unauthenticated(self):
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 401)

    def test_delete_item(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.STOCKS.GOOGL.ticker, response.data["stocks"])

    def test_cannot_delete_non_existent(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.delete(
            f"/stocks/watchlists/{self.WATCHLISTS.main.id}/stocks/{self.STOCKS.BABA.ticker}"
        )

        self.assertEqual(response.status_code, 404)

    def test_cannot_delete_from_another_users_watchlist(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.delete(
            f"/stocks/watchlists/{self.WATCHLISTS.other_users.id}/stocks/{self.STOCKS.GOOGL.ticker}"
        )

        self.assertEqual(response.status_code, 403)


class TestTargetPriceCreate(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.USERS = data.USERS
        cls.WATCHLISTS = data.WATCHLISTS
        cls.STOCKS = data.STOCKS

        cls.url = f"/stocks/watchlists/{cls.WATCHLISTS.main.id}/stocks/{cls.STOCKS.GOOGL.ticker}/target-prices"
        cls.token = generate_token(data.USERS.owner)
        cls.payload = {"price": 2_000, "description": "My description"}

    def test_cannot_access_unauthenticated(self):
        response = self.client.post(self.url, self.payload)

        self.assertEqual(response.status_code, 401)

    def test_add_target_price(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.post(self.url, self.payload)

        self.assertEqual(response.status_code, 201)

    def test_cannot_add_to_another_users_watchlist_item(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.post(
            f"/stocks/watchlists/{self.WATCHLISTS.other_users.id}/stocks/{self.STOCKS.GOOGL.ticker}/target-prices",
            self.payload,
        )

        self.assertEqual(response.status_code, 403)


class TestTargetPriceDelete(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.USERS = data.USERS
        cls.WATCHLISTS = data.WATCHLISTS
        cls.STOCKS = data.STOCKS
        cls.TARGET_PRICES = data.TARGET_PRICES

        cls.url = f"""/stocks/watchlists/{cls.WATCHLISTS.main.id}/stocks/{cls.STOCKS.GOOGL.ticker}/target-prices/{
            cls.TARGET_PRICES.google_first.id}"""
        cls.token = generate_token(data.USERS.owner)

    def test_cannot_access_unauthenticated(self):
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 401)

    def test_remove_target_price(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 204)

    def test_cannot_remote_from_another_users_watchlist_item(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.delete(
            f"""/stocks/watchlists/{self.WATCHLISTS.other_users.id}/stocks/{self.STOCKS.GOOGL.ticker}/target-prices/{
                self.TARGET_PRICES.google_first.id}"""
        )

        self.assertEqual(response.status_code, 403)


class TestPositionSizeCreate(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.USERS = data.USERS
        cls.WATCHLISTS = data.WATCHLISTS
        cls.STOCKS = data.STOCKS

        cls.url = f"/stocks/watchlists/{cls.WATCHLISTS.main.id}/stocks/{cls.STOCKS.GOOGL.ticker}/position-sizes"
        cls.token = generate_token(data.USERS.owner)
        cls.payload = {"size": 20_000, "at_cost": True}

    def test_cannot_access_unauthenticated(self):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 401)

    def test_add_position_size(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.post(self.url, self.payload)

        self.assertEqual(response.status_code, 201)

    def test_cannot_add_to_another_users_watchlist_item(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.post(
            f"/stocks/watchlists/{self.WATCHLISTS.other_users.id}/stocks/{self.STOCKS.GOOGL.ticker}/position-sizes",
            self.payload,
        )

        self.assertEqual(response.status_code, 403)


class TestPositionSizeDelete(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.USERS = data.USERS
        cls.WATCHLISTS = data.WATCHLISTS
        cls.STOCKS = data.STOCKS
        cls.POSITION_SIZES = data.POSITION_SIZES

        cls.url = f"""/stocks/watchlists/{cls.WATCHLISTS.main.id}/stocks/{cls.STOCKS.GOOGL.ticker}/position-sizes/{
            cls.POSITION_SIZES.google_at_cost.id}"""
        cls.token = generate_token(data.USERS.owner)

    def test_cannot_access_unauthenticated(self):
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 401)

    def test_remove_position_size(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 204)

    def test_cannot_remote_from_another_users_watchlist_item(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        response = self.client.delete(
            f"""/stocks/watchlists/{self.WATCHLISTS.other_users.id}/stocks/{self.STOCKS.GOOGL.ticker}/position-sizes/{
                self.POSITION_SIZES.google_at_cost.id}"""
        )

        self.assertEqual(response.status_code, 403)
