"""Integration tests for the performance API."""

from django.test import TestCase
from rest_framework.test import APIClient

from ..seed import generate_test_data


class TestPositionPerformance(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        generate_test_data()

        cls.url = "/performance/portfolios/1/MSFT"

    def test_cannot_access_unauthenticated(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)


class TestPortfolioPerformance(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        generate_test_data()

        cls.url = "/performance/portfolios/1"

    def test_cannot_access_unauthenticated(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)


class TestPortfolioSummaryPerformance(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        generate_test_data()

        cls.url = "/performance/portfolios/summary"

    def test_cannot_access_unauthenticated(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)
