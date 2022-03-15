"""Integration tests for the cash API."""

from django.test import TestCase
from rest_framework.test import APIClient

from core.test.seed import generate_test_data


class TestCashBalanceDetail(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.PORTFOLIOS = data.PORTFOLIOS

        cls.url = f"/cash/{cls.PORTFOLIOS.main.id}/"

    def test_cannot_access_unauthenticated(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_fetch_balance(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_fetch_non_existent_portfolio(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.get("/cash/100/")

        self.assertEqual(response.status_code, 404)


class TestCashBalanceSummary(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.PORTFOLIOS = data.PORTFOLIOS

        cls.url = "/cash/summary/"

    def test_cannot_access_unauthenticated(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_fetch_summary(self):
        self.client.login(  # nosec - Password hardcoded intentionally in test.
            username="owner", password="password"
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
