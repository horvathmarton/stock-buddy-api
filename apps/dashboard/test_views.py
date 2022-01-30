"""Integration tests for the dashboard API."""

from datetime import date
from django.db.models import Q
from django.test import TestCase
from rest_framework.test import APIClient
from apps.transactions.models import StockTransaction
from core.test.seed import generate_test_data

from apps.dashboard.models import Strategy, UserStrategy
from lib.enums import Visibility


class TestStrategyList(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls) -> None:
        data = generate_test_data()
        cls.USERS = data.USERS

        cls.url = "/dashboard/strategies/"

    def test_cannot_access_unauthenticated(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_list_owned_strategies(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.get(self.url)

        strategies_count = len(
            Strategy.objects.filter(
                Q(owner=self.USERS.owner) | Q(visibility=Visibility.PUBLIC)
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), strategies_count)


class TestStrategyDetail(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls) -> None:
        data = generate_test_data()
        cls.USERS = data.USERS
        cls.STRATEGIES = data.STRATEGIES

        cls.url = f"/dashboard/strategies/{cls.STRATEGIES.main.id}/"

    def test_cannot_access_unauthenticated(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_fetch_existing_strategy(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Main strategy")

    def test_fetch_non_existent_strategy(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.get("/dashboard/strategies/100/")

        self.assertEqual(response.status_code, 404)

    def test_fetch_other_users_strategy(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.get(
            f"/dashboard/strategies/{self.STRATEGIES.other_users.id}/"
        )

        self.assertEqual(response.status_code, 404)


class TestCurrentStrategy(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls) -> None:
        data = generate_test_data()
        cls.USERS = data.USERS
        cls.STRATEGIES = data.STRATEGIES

        cls.url = "/dashboard/strategies/me/"

    def test_cannot_access_unauthenticated(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_fetch_current_strategy(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["current"])
        self.assertTrue(response.data["target"])


class TestStrategySelection(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls) -> None:
        data = generate_test_data()
        cls.USERS = data.USERS
        cls.STRATEGIES = data.STRATEGIES

        cls.url = "/dashboard/strategies/select_strategy/"

    def test_cannot_access_unauthenticated(self):
        response = self.client.post(
            self.url,
            data={"strategy": self.STRATEGIES.public.id},
            format="json",
        )

        self.assertEqual(response.status_code, 401)

    def test_select_target_strategy(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.post(
            self.url,
            data={"strategy": self.STRATEGIES.public.id},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        target_strategy = UserStrategy.objects.get(user=self.USERS.owner)
        self.assertEqual(target_strategy.strategy, self.STRATEGIES.public)


class TestStrategyCreate(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls) -> None:
        data = generate_test_data()
        cls.USERS = data.USERS

        cls.url = "/dashboard/strategies/"

    def test_cannot_access_unauthenticated(self):
        response = self.client.post(
            self.url,
            data={
                "name": "New strategy",
                "items": [
                    {"name": "stock", "size": 0.4},
                    {"name": "real-estate", "size": 0.6},
                ],
            },
        )

        self.assertEqual(response.status_code, 401)

    def test_create_new_strategy(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        current_strategy_count = len(
            Strategy.objects.filter(
                Q(owner=self.USERS.owner) | Q(visibility=Visibility.PUBLIC)
            )
        )

        response = self.client.post(
            self.url,
            data={
                "name": "New strategy",
                "items": [
                    {"name": "stock", "size": 0.4},
                    {"name": "real-estate", "size": 0.6},
                ],
            },
            format="json",
        )

        updated_strategy_count = len(
            Strategy.objects.filter(
                Q(owner=self.USERS.owner) | Q(visibility=Visibility.PUBLIC)
            )
        )
        created_strategy = Strategy.objects.get(pk=response.data["id"])

        self.assertEqual(response.status_code, 201)
        self.assertEqual(updated_strategy_count, current_strategy_count + 1)
        self.assertEqual(created_strategy.owner, self.USERS.owner)

    def test_malformed_payload(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        current_strategy_count = len(
            Strategy.objects.filter(
                Q(owner=self.USERS.owner) | Q(visibility=Visibility.PUBLIC)
            )
        )

        response = self.client.post(
            self.url,
            data={
                "items": [
                    {"name": "stock", "size": 0.4},
                    {"name": "real-estate", "size": 0.6},
                ],
            },
            format="json",
        )

        updated_strategy_count = len(
            Strategy.objects.filter(
                Q(owner=self.USERS.owner) | Q(visibility=Visibility.PUBLIC)
            )
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(updated_strategy_count, current_strategy_count)

    def test_create_incomplete_strategy(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        current_strategy_count = len(
            Strategy.objects.filter(
                Q(owner=self.USERS.owner) | Q(visibility=Visibility.PUBLIC)
            )
        )

        response = self.client.post(
            self.url,
            data={
                "name": "New strategy",
                "items": [
                    {"name": "stock", "size": 0.4},
                    {"name": "real-estate", "size": 0.5},
                ],
            },
            format="json",
        )

        updated_strategy_count = len(
            Strategy.objects.filter(
                Q(owner=self.USERS.owner) | Q(visibility=Visibility.PUBLIC)
            )
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(updated_strategy_count, current_strategy_count)


class TestStrategyUpdate(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls) -> None:
        data = generate_test_data()
        cls.USERS = data.USERS
        cls.STRATEGIES = data.STRATEGIES

        cls.url = f"/dashboard/strategies/{cls.STRATEGIES.main.id}/"

    def test_cannot_access_unauthenticated(self):
        response = self.client.put(
            self.url,
            data={
                "name": "New strategy",
                "items": [
                    {"name": "stock", "size": 0.4},
                    {"name": "real-estate", "size": 0.6},
                ],
            },
        )

        self.assertEqual(response.status_code, 401)

    def test_update_strategy(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.put(
            self.url,
            data={
                "name": "New strategy",
                "items": [
                    {"name": "stock", "size": 0.4},
                    {"name": "real-estate", "size": 0.6},
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        strategy = Strategy.objects.get(pk=self.STRATEGIES.main.id)
        self.assertEqual(strategy.name, "Main strategy")

    def test_rename_strategy(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.patch(self.url, data={"name": "New name"}, format="json")

        self.assertEqual(response.status_code, 200)
        strategy = Strategy.objects.get(pk=self.STRATEGIES.main.id)
        self.assertEqual(strategy.name, "New name")

    def test_update_non_existing_strategy(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.put(
            "/dashboard/strategies/100/",
            data={
                "items": [
                    {"name": "stock", "size": 0.4},
                    {"name": "real-estate", "size": 0.6},
                ],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 404)

    def test_malformed_payload(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        current_strategy_count = len(
            Strategy.objects.filter(
                Q(owner=self.USERS.owner) | Q(visibility=Visibility.PUBLIC)
            )
        )

        response = self.client.put(
            self.url,
            data={
                "items": [
                    {"name": "stock", "size": 0.4},
                    {"name": "real-estate", "size": 0.6},
                ],
            },
            format="json",
        )

        updated_strategy_count = len(
            Strategy.objects.filter(
                Q(owner=self.USERS.owner) | Q(visibility=Visibility.PUBLIC)
            )
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(updated_strategy_count, current_strategy_count)

    def test_update_with_incomplete_strategy(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        current_strategy_count = len(
            Strategy.objects.filter(
                Q(owner=self.USERS.owner) | Q(visibility=Visibility.PUBLIC)
            )
        )

        response = self.client.put(
            self.url,
            data={
                "name": "New strategy",
                "items": [
                    {"name": "stock", "size": 0.4},
                    {"name": "real-estate", "size": 0.5},
                ],
            },
            format="json",
        )

        updated_strategy_count = len(
            Strategy.objects.filter(
                Q(owner=self.USERS.owner) | Q(visibility=Visibility.PUBLIC)
            )
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(updated_strategy_count, current_strategy_count)


class TestStrategyDelete(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls) -> None:
        data = generate_test_data()
        cls.USERS = data.USERS
        cls.STRATEGIES = data.STRATEGIES

        cls.url = f"/dashboard/strategies/{cls.STRATEGIES.main.id}/"

    def test_cannot_access_unauthenticated(self):
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 401)

    def test_delete_is_disallowed(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 405)
        self.assertTrue(Strategy.objects.get(pk=self.STRATEGIES.main.id))


class TestPortfolioIndicators(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls) -> None:
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
            price=100.01,
        )

        cls.url = "/dashboard/portfolio-indicators"

    def test_cannot_access_unauthenticated(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_fetch_portfolio_indicators(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
