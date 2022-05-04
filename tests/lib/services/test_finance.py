"""Test cases for finance service."""

from django.test import SimpleTestCase
from src.lib.services.finance import rri


class TestPresentValue(SimpleTestCase):
    pass


class TestFutureValue(SimpleTestCase):
    pass


class TestRateOfInvestmentReturn(SimpleTestCase):
    """
    Different scenarios to check RRI calculation.
    Reference values took from excel.
    """

    def test_one_year_period(self):
        self.assertEqual(rri(1, 100, 160), 0.6000)

    def test_multi_year_period(self):
        self.assertEqual(rri(3, 100, 160), 0.1696)

    def test_fractional_period(self):
        self.assertEqual(rri(0.3, 100, 160), 3.7907)

    def test_negative_return(self):
        self.assertEqual(rri(2, 100, 60), -0.2254)
