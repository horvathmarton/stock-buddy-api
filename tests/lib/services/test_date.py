"""Test cases for the date service."""

from datetime import date

from django.test import TestCase
from src.lib.dataclasses import Interval
from src.lib.enums import Resolution
from src.lib.services.date import get_resolution, get_timeseries


class TestGetResolution(TestCase):
    def test_zero_interval(self):
        interval = Interval(start_date=date(2022, 1, 1), end_date=date(2022, 1, 1))

        self.assertEqual(get_resolution(interval), Resolution.DAY)

    def test_interval_generation(self):
        interval = Interval(start_date=date(2022, 1, 1), end_date=date(2022, 2, 5))

        self.assertEqual(get_resolution(interval), Resolution.MONTH)

    def test_inverse_interval(self):
        interval = Interval(start_date=date(2022, 2, 1), end_date=date(2022, 1, 1))

        with self.assertRaises(Exception):
            get_resolution(interval)


class TestGetTimeseries(TestCase):
    def test_zero_interval(self):
        interval = Interval(start_date=date(2022, 1, 1), end_date=date(2022, 1, 1))

        result = get_timeseries(interval, Resolution.DAY)

        self.assertEqual(result, [])

    def test_timeseries_generation(self):
        interval = Interval(start_date=date(2022, 1, 3), end_date=date(2022, 2, 1))

        result = get_timeseries(interval, Resolution.WEEK)

        self.assertEqual(
            result,
            [
                date(2022, 1, 3),
                date(2022, 1, 10),
                date(2022, 1, 17),
                date(2022, 1, 24),
                date(2022, 1, 31),
            ],
        )

    def test_inverse_interval(self):
        interval = Interval(start_date=date(2022, 2, 1), end_date=date(2022, 1, 1))

        with self.assertRaises(Exception):
            get_timeseries(interval, Resolution.WEEK)
