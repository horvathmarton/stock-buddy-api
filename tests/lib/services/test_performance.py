"""Test cases for the performance service."""

from datetime import date

from django.test import TestCase
from src.lib.dataclasses import (
    PerformanceSnapshot,
    StockPortfolioSnapshot,
    StockPositionSnapshot,
)
from src.lib.services.performance import (
    get_portfolio_performance,
    get_position_performance,
    time_weighted_return,
)
from src.raw_data.models import StockDividend, StockPrice
from src.transactions.enums import Currency
from src.transactions.models import CashTransaction

from ...seed import generate_test_data


class TestGetPositionPerformance(TestCase):
    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.USERS = data.USERS
        cls.PORTFOLIOS = data.PORTFOLIOS
        cls.STOCKS = data.STOCKS

        cls.snapshot_date = date(2022, 1, 1)
        cls.snapshots = {
            cls.snapshot_date: StockPortfolioSnapshot(
                positions={
                    "PM": StockPositionSnapshot(
                        stock=cls.STOCKS.PM,
                        shares=2,
                        price=100.0,
                        dividend=2.5,
                        purchase_price=10.0,
                        first_purchase_date=date(2021, 1, 1),
                        latest_purchase_date=date(2021, 6, 1),
                    )
                },
                date=cls.snapshot_date,
                owner=cls.USERS.owner,
            )
        }
        cls.price_info = [
            StockPrice(ticker=cls.STOCKS.PM, date=cls.snapshot_date, value=100),
            StockPrice(ticker=cls.STOCKS.PM, date=cls.snapshot_date, value=105),
            StockPrice(ticker=cls.STOCKS.PM, date=cls.snapshot_date, value=102),
        ]
        cls.dividends = [
            StockDividend(ticker=cls.STOCKS.PM, date=date(2022, 1, 1), amount=10.0)
        ]
        cls.transactions = []

    def test_empty(self):
        self.assertEqual(get_position_performance({}, [], [], [], []), {})

    def test_no_snapshots(self):
        self.assertEqual(
            get_position_performance(
                {},
                self.price_info,
                self.dividends,
                self.transactions,
                [self.snapshot_date],
            ),
            {},
        )

    def test_no_price_info(self):
        result = get_position_performance(
            self.snapshots, [], self.dividends, self.transactions, [self.snapshot_date]
        )

        self.assertEqual(
            result[self.snapshot_date],
            PerformanceSnapshot(self.snapshot_date, base_size=200, dividends=20),
        )

    def test_no_dividends(self):
        result = get_position_performance(
            self.snapshots, self.price_info, [], self.transactions, [self.snapshot_date]
        )

        self.assertEqual(
            result[self.snapshot_date],
            PerformanceSnapshot(self.snapshot_date, base_size=200, appreciation=4),
        )

    def test_no_transactions(self):
        result = get_position_performance(
            self.snapshots, self.price_info, self.dividends, [], [self.snapshot_date]
        )

        self.assertEqual(
            result[self.snapshot_date],
            PerformanceSnapshot(
                self.snapshot_date, base_size=200, appreciation=4, dividends=20
            ),
        )

    def test_no_series(self):
        self.assertEqual(
            get_position_performance(
                self.snapshots, self.price_info, self.dividends, self.transactions, []
            ),
            {},
        )

    def test_performance_calculation(self):
        result = get_position_performance(
            self.snapshots,
            self.price_info,
            self.dividends,
            self.transactions,
            [self.snapshot_date],
        )

        self.assertEqual(
            result[self.snapshot_date],
            PerformanceSnapshot(
                self.snapshot_date, base_size=200, appreciation=4, dividends=20
            ),
        )


class TestGetPortfolioPerformance(TestCase):
    @classmethod
    def setUpTestData(cls):
        data = generate_test_data()
        cls.USERS = data.USERS
        cls.PORTFOLIOS = data.PORTFOLIOS
        cls.STOCKS = data.STOCKS

        cls.snapshot_date = date(2022, 1, 1)
        cls.snapshots = {
            cls.snapshot_date: StockPortfolioSnapshot(
                positions={
                    "PM": StockPositionSnapshot(
                        stock=cls.STOCKS.PM,
                        shares=2,
                        price=100.0,
                        dividend=2.5,
                        purchase_price=10.0,
                        first_purchase_date=date(2021, 1, 1),
                        latest_purchase_date=date(2021, 6, 1),
                    )
                },
                date=cls.snapshot_date,
                owner=cls.USERS.owner,
            )
        }
        cls.dividends = [
            StockDividend(ticker=cls.STOCKS.PM, date=date(2022, 1, 1), amount=10.0)
        ]
        cls.transactions = [
            CashTransaction(
                currency=Currency.HUNGARIAN_FORINT,
                amount=3_000.0,
                date=date(2021, 1, 1),
                owner=cls.USERS.owner,
                portfolio=cls.PORTFOLIOS.main,
            ),
            CashTransaction(
                currency=Currency.HUNGARIAN_FORINT,
                amount=-1_000.0,
                date=date(2021, 1, 1),
                owner=cls.USERS.owner,
                portfolio=cls.PORTFOLIOS.main,
            ),
        ]

    def test_empty(self):
        self.assertEqual(get_portfolio_performance({}, [], [], []), {})

    def test_no_snapshots(self):
        self.assertEqual(
            get_portfolio_performance(
                {}, self.dividends, self.transactions, [self.snapshot_date]
            ),
            {},
        )

    def test_no_dividends(self):
        result = get_portfolio_performance(
            self.snapshots, [], self.transactions, [self.snapshot_date]
        )

        self.assertEqual(
            result[self.snapshot_date],
            PerformanceSnapshot(
                date=self.snapshot_date, base_size=200, cash_flow=6.666666666666666
            ),
        )

    def test_no_transactions(self):
        result = get_portfolio_performance(
            self.snapshots, self.dividends, [], [self.snapshot_date]
        )

        self.assertEqual(
            result[self.snapshot_date],
            PerformanceSnapshot(date=self.snapshot_date, base_size=200, dividends=20),
        )

    def test_no_series(self):
        self.assertEqual(
            get_portfolio_performance(
                self.snapshots, self.dividends, self.transactions, []
            ),
            {},
        )

    def test_performance_calculation(self):
        result = get_portfolio_performance(
            self.snapshots, self.dividends, self.transactions, [self.snapshot_date]
        )

        self.assertEqual(
            result[self.snapshot_date],
            PerformanceSnapshot(
                date=self.snapshot_date,
                base_size=200,
                dividends=20,
                cash_flow=6.666666666666666,
            ),
        )


class TestTimeWeightedReturn(TestCase):
    def test_empty_snapshots(self):
        self.assertEqual(time_weighted_return([]), 0)

    def test_weighted_return_calculation(self):
        snapshots = [
            PerformanceSnapshot(date(2021, 1, 1), 100, 10),
            PerformanceSnapshot(date(2022, 1, 1), 110, 10),
            PerformanceSnapshot(date(2023, 1, 1), 120, 10),
        ]

        self.assertEqual(round(time_weighted_return(snapshots), 2), 0.3)
