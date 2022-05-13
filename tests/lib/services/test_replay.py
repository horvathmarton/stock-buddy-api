"""Test cases for the replay service."""

from datetime import date

from django.test import TestCase
from src.lib.services.replay import generate_snapshot_series
from tests.stubs import DateBoundStub, InitialStub


class TestGenerateSnapshotSeries(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.snapshot_date = date(2022, 1, 1)
        cls.initial = InitialStub(0)
        cls.actions = [
            DateBoundStub(3, date(2021, 1, 1)),
            DateBoundStub(2, date(2022, 1, 1)),
        ]

    def test_empty(self):
        self.assertEqual(
            generate_snapshot_series(
                None, [], [], lambda x, y: None, lambda x, y: None
            ),
            {},
        )

    def test_no_initial(self):
        result = generate_snapshot_series(
            None, self.actions, [self.snapshot_date], lambda x, y: x, lambda x, y: x
        )

        self.assertEqual(result[self.snapshot_date], None)

    def test_no_actions(self):
        result = generate_snapshot_series(
            self.initial, [], [self.snapshot_date], lambda x, y: x, lambda x, y: x
        )

        self.assertEqual(result[self.snapshot_date], self.initial)

    def test_no_series(self):
        result = generate_snapshot_series(
            self.initial, self.actions, [], lambda x, y: x, lambda x, y: x
        )

        self.assertEqual(result, {})

    def test_series_calculation(self):
        result = generate_snapshot_series(
            self.initial,
            self.actions,
            [self.snapshot_date],
            lambda x, y: InitialStub(x.value + y.value),
            lambda x, y: x,
        )

        self.assertEqual(result[self.snapshot_date], InitialStub(5))
