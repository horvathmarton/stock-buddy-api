"""Unit tests for the shared helper functions."""

from datetime import date, datetime, timedelta
from typing import cast

from django.test import TestCase
from rest_framework.request import Request

from src.lib.dataclasses import Interval
from src.lib.helpers import get_range

from ..stubs import RequestStub


class TestGetRange(TestCase):
    def test_empty(self):
        request = RequestStub()
        today = datetime.today().date()
        year_ago = today - timedelta(days=365)

        self.assertEqual(
            get_range(cast(Request, request)),
            Interval(year_ago, today),
        )

    def test_invalid_input(self):
        request = RequestStub(query_params={"from": "test", "to": "test"})

        with self.assertRaises(ValueError):
            get_range(cast(Request, request))

    def test_range_parsing(self):
        request = RequestStub(query_params={"from": "2022-02-14", "to": "2022-05-17"})

        self.assertEqual(
            get_range(cast(Request, request)),
            Interval(date(2022, 2, 14), date(2022, 5, 17)),
        )

    def test_missing_to_param(self):
        request = RequestStub(query_params={"from": "2022-02-14"})
        today = datetime.today().date()

        self.assertEqual(
            get_range(cast(Request, request)),
            Interval(date(2022, 2, 14), today),
        )
