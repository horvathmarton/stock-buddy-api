"""Integration tests for the dashboard API."""

from datetime import date
from os import environ

from django.db.models import Q
from django.test import TestCase
from rest_framework.test import APIClient
from core.test.seed import generate_test_data
from lib.enums import Visibility

from apps.dashboard.models import Strategy, UserStrategy
from apps.raw_data.models import StockPrice
from apps.transactions.models import CashTransaction, ForexTransaction, StockTransaction


class TestStrategyList(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
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
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
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
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
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
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.USERS = data.USERS
        cls.STRATEGIES = data.STRATEGIES

        cls.url = "/dashboard/strategies/select-strategy"

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
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
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
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
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
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
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
            amount=3,
            date=date(2020, 1, 1),
            ticker=cls.STOCKS.MSFT,
            owner=cls.USERS.owner,
            portfolio=cls.PORTFOLIOS.main,
            price=100.0,
        )

        cls.url = "/dashboard/portfolio-indicators"

    def test_cannot_access_unauthenticated(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_fetch_portfolio_indicators(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        environ["EUR_USD_FX_RATE"] = "1.10"
        environ["USD_HUF_FX_RATE"] = "300.00"

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_roic_should_only_consider_invested_capital(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        environ["USD_HUF_FX_RATE"] = "300.00"

        CashTransaction.objects.create(
            currency="HUF",
            amount=90_000,
            date=date(2020, 1, 1),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )

        ForexTransaction.objects.create(
            source_currency="HUF",
            target_currency="USD",
            amount=90_000,
            ratio=1 / 300,
            date=date(2020, 1, 1),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )

        StockTransaction.objects.create(
            amount=-2,
            date=date(2022, 1, 1),
            ticker=self.STOCKS.MSFT,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
            price=150.0,
        )
        StockTransaction.objects.create(
            amount=1,
            date=date(2021, 1, 1),
            ticker=self.STOCKS.BABA,
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
            price=100.0,
        )

        StockPrice.objects.create(
            ticker=self.STOCKS.MSFT,
            date=date(2022, 1, 1),
            value=200,
            sync=self.SYNCS.main,
        )
        StockPrice.objects.create(
            ticker=self.STOCKS.MSFT,
            date=date(2022, 1, 1),
            value=150,
            sync=self.SYNCS.main,
        )

        ForexTransaction.objects.create(
            source_currency="USD",
            target_currency="HUF",
            amount=100,
            ratio=300 / 1,
            date=date(2022, 1, 1),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )

        CashTransaction.objects.create(
            currency="HUF",
            amount=-15_000,
            date=date(2022, 1, 1),
            owner=self.USERS.owner,
            portfolio=self.PORTFOLIOS.main,
        )

        # Bad
        # Invested capital: MSFT 100 USD + BABA 100 USD = 200 USD
        # Portfolio value: MSFT 200 USD + BABA 150 USD = 350 USD
        # Cash: MSFT (200 - 100) * 2 = 200 USD
        # Total ROIC: (550 / 200) - 1 = 175%
        # Annualized ROIC: 66%

        # Good
        # Invested capital: 90_000 - 15_000 = 75_000
        # Portfolio value: 100 USD
        # Cash: 75_000 HUF -> 250 USD
        # Total ROIC: (350 / 250) - 1 = 48% in 2 years
        # Annualized ROIC: 21.65%

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertAlmostEqual(response.data["totalInvestedCapital"], 250)
        self.assertAlmostEqual(response.data["totalAum"], 370)
        self.assertAlmostEqual(response.data["totalFloatingPnl"], 120)
        self.assertEqual(round(response.data["grossCapitalDeployed"], 4), 0.3640)
        self.assertEqual(round(response.data["roicSinceInception"], 4), 0.48)
        self.assertEqual(round(response.data["annualizedRoic"], 4), 0.2166)

        self.assertEqual(round(response.data["largetsSectorExposure"], 4), 0.5405)
        self.assertEqual(round(response.data["largestPositionExposure"], 4), 0.5405)
