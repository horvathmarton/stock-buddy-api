"""Unit tests for the stocks module related helper functions."""

from django.test import TestCase
from src.stocks.dataclasses import WatchlistRow

from src.stocks.helpers import parse_watchlist_rows


class TestParseWatchlistRows(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.rows = [
            WatchlistRow(
                watchlist_id=1,
                watchlist_name="Watchlist name",
                stock_id="GOOGL",
                target_id=1,
                size=100.25,
                at_cost=False,
                item_type="position_size",
                price=None,
                watchlist_description=None,
                target_name="first target",
            ),
            WatchlistRow(
                watchlist_id=1,
                watchlist_name="Watchlist name",
                stock_id="GOOGL",
                target_id=2,
                size=200.15,
                at_cost=False,
                item_type="position_size",
                price=None,
                watchlist_description=None,
                target_name="second target",
            ),
            WatchlistRow(
                watchlist_id=1,
                watchlist_name="Watchlist name",
                stock_id="GOOGL",
                target_id=3,
                size=None,
                at_cost=None,
                item_type="target_price",
                price=42.1,
                watchlist_description=None,
                target_name="third target",
            ),
            WatchlistRow(
                watchlist_id=1,
                watchlist_name="Watchlist name",
                stock_id="AAPL",
                target_id=4,
                size=None,
                at_cost=None,
                item_type="target_price",
                price=1200.1,
                watchlist_description=None,
                target_name="fourth target",
            ),
        ]

    def test_empty(self):
        self.assertEqual(parse_watchlist_rows([]), [])

    def test_parse_rows(self):
        result = parse_watchlist_rows(self.rows)

        self.assertEqual(len(result), 1)

        watchlist = result[0]

        self.assertEqual(watchlist.name, "Watchlist name")
        self.assertEqual(len(watchlist.items), 2)

        googl = watchlist.items[0]

        self.assertEqual(len(googl.position_sizes), 2)
        self.assertEqual(len(googl.target_prices), 1)
