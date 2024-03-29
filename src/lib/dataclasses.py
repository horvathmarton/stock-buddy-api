"""Dataclasses shared throughout the project."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict

from django.contrib.auth.models import User

from ..stocks.models import Stock
from ..transactions.enums import Currency
from .protocols import DateBound
from .services.finance import rri


@dataclass(frozen=True)
class Interval:
    """Represents a time interval with a start and end date. Start is inclusive, end is exclusive."""

    start_date: date
    end_date: date


@dataclass
class StockPositionSnapshot:
    """Represents a position at a given time."""

    stock: Stock
    shares: int
    # Current price of one stock in USD.
    price: float
    # Current dividend of one stock for a full year in USD (forward looking).
    dividend: float
    # Averate purchase price of one stock in USD.
    purchase_price: float
    # Date when the position was initiated.
    first_purchase_date: date
    # Latest date when the position was changed.
    latest_purchase_date: date
    # ex_dividend_date: date
    # dividend_declaration_date: date

    def __repr__(self) -> str:
        # pylint: disable=missing-function-docstring

        return f"""{self.stock.ticker} (p={self.price}, s={self.shares}, pp={
            self.purchase_price
        }, d={self.dividend}, fp={self.first_purchase_date}, lp={self.latest_purchase_date})"""

    def __eq__(self, other: object) -> bool:
        # pylint: disable=missing-function-docstring

        if not isinstance(other, StockPositionSnapshot):
            return NotImplemented

        return (
            self.stock == other.stock
            and self.shares == other.shares
            and self.price == other.price
            and self.dividend == other.dividend
            and self.purchase_price == other.purchase_price
            and self.first_purchase_date == other.first_purchase_date
            and self.latest_purchase_date == other.latest_purchase_date
        )

    @property
    def size(self) -> float:
        """Position size at the current price in USD."""

        return round(self.shares * self.price, 2)

    @property
    def size_at_cost(self) -> float:
        """Position size at the purchase price in USD."""

        return round(self.shares * self.purchase_price, 2)

    @property
    def dividend_yield(self) -> float:
        """Dividend yield in percentage (e.g.: 0.12 means 12%)."""

        return round(self.dividend / self.price, 4)

    @property
    def dividend_yield_on_cost(self) -> float:
        """Dividend yield in percentage based on the purchase price (e.g.: 0.12 means 12%)."""

        return round(self.dividend / self.purchase_price, 4)

    @property
    def dividend_income(self) -> float:
        """Yearly dividend income from the position in USD (forward looking)."""

        return round(self.shares * self.dividend, 2)

    @property
    def pnl_percentage(self) -> float:
        """Percentage change from the purchase price (e.g.: 0.12 means 12%)."""

        return round((self.price - self.purchase_price) / self.purchase_price, 4)

    @property
    def pnl(self) -> float:
        """Amount of PnL of the entire position in USD."""

        return round(self.shares * (self.price - self.purchase_price), 2)


@dataclass
class StockPortfolioSnapshot(DateBound):
    """
    Represents a portfolio at a given time.

    Contains a list of positions in the portfolio and the aggregate data.
    """

    # List of the summarized position in the current portfolio.
    positions: Dict[str, StockPositionSnapshot]
    date: date
    owner: User

    def __eq__(self, other: object) -> bool:
        # pylint: disable=missing-function-docstring

        if not isinstance(other, StockPortfolioSnapshot):
            return NotImplemented

        return (
            self.positions == other.positions
            and self.owner == other.owner
            and self.date == other.date
        )

    @property
    def assets_under_management(self) -> float:
        """Property to calculate the total assets under the management of the portfolio."""

        return sum((position.size for position in self.positions.values()))

    @property
    def capital_invested(self) -> float:
        """Property to calculate the total invested capital into the portfolio."""

        return sum((position.size_at_cost for position in self.positions.values()))

    @property
    def dividend(self) -> float:
        """Property to calculate the total dividend income from the portfolio."""

        return sum((position.dividend_income for position in self.positions.values()))

    @property
    def dividend_yield(self) -> float:
        """Property to calculate the aggregated dividend yield in the portfolio."""

        return round(self.dividend / self.assets_under_management, 4)

    @property
    def number_of_positions(self) -> int:
        """Property to calculate the number of position in the portfolio."""

        return len(self.positions)

    @property
    def sector_distribution(self) -> Dict[str, float]:
        """Mapping with the sector name as key and the portfolio percentage as value (e.g.: 0.12 means 12%)."""

        sectors = {}

        for position in self.positions.values():
            sector = position.stock.sector
            size_in_portfolio = round(position.size / self.assets_under_management, 4)

            if sector not in sectors:
                sectors[sector] = size_in_portfolio
            else:
                sectors[sector] += size_in_portfolio

        return sectors

    @property
    def size_distribution(self) -> Dict[str, float]:
        """Maps each ticker in the portfolio to its size in percentage (e.g.: 0.12 means 12%)."""

        return {
            position.stock.ticker: round(
                position.size / self.assets_under_management, 4
            )
            for position in self.positions.values()
        }

    @property
    def size_at_cost_distribution(self) -> Dict[str, float]:
        """Maps each ticker in the portfolio to its size @ cost in percentage (e.g.: 0.12 means 12%)."""

        return {
            position.stock.ticker: round(
                position.size_at_cost / self.capital_invested, 4
            )
            for position in self.positions.values()
        }

    @property
    def dividend_distribution(self) -> Dict[str, float]:
        """Maps each ticker in the portfolio to its dividend size in percentage (e.g.: 0.12 means 12%)."""

        return {
            position.stock.ticker: round(position.dividend_income / self.dividend, 4)
            for position in self.positions.values()
            if position.dividend_income > 0
        }

    @property
    def annualized_pnls(self) -> Dict[str, float]:
        """
        Maps each ticker in the portfolio to its annualized return in percentage on a daily base
        (e.g.: 0.12 means 12%).
        """

        mapping = {}
        for position in self.positions.values():
            periods = round((self.date - position.first_purchase_date).days / 365, 1)
            mapping[position.stock.ticker] = rri(
                periods, position.size_at_cost, position.size
            )

        return mapping


@dataclass
class CashBalanceSnapshot:
    # pylint: disable=invalid-name

    """Represents the cash balance in a portfolio at a given time in different currencies."""

    USD: float = 0
    EUR: float = 0
    HUF: float = 0

    def __eq__(self, o: object) -> bool:
        # pylint: disable=missing-function-docstring

        if not isinstance(o, CashBalanceSnapshot):
            return NotImplemented

        return self.USD == o.USD and self.EUR == o.EUR and self.HUF == o.HUF

    def __getitem__(self, item) -> float:
        """Index properties dynamically."""

        if item == Currency.EURO:
            return self.EUR

        if item == Currency.HUNGARIAN_FORINT:
            return self.HUF

        if item == Currency.US_DOLLAR:
            return self.USD

        raise Exception("Not a valid currency.")

    def __setitem__(self, item, value) -> None:
        """Assign to properties dynamically."""

        if not isinstance(value, float):
            raise Exception("Only float could be assigned.")

        if item == Currency.EURO:
            self.EUR = value
        elif item == Currency.HUNGARIAN_FORINT:
            self.HUF = value
        elif item == Currency.US_DOLLAR:
            self.USD = value
        else:
            raise Exception("Not a valid currency.")


@dataclass
class PerformanceSnapshot:
    """Represents a performance snapshot of a security position or a portfolio."""

    # Date when the snapshot was taken.
    date: date
    # Base size of the position.
    base_size: float = 0
    # Increment of the position size in dollar amount.
    appreciation: float = 0
    # Dividends paid by the position in dollar amount.
    dividends: float = 0
    # Capital size change in the given period. Positive means inflow.
    cash_flow: float = 0

    @property
    def pnl(self) -> float:
        """PnL of the position or portfolio."""

        return self.appreciation + self.dividends

    @property
    def capital_size(self) -> float:
        """Current size of the position or portfolio at the snapshot date."""

        return self.base_size + self.appreciation + self.cash_flow

    @property
    def total(self) -> float:
        """Total size of the position or portfolio (capital and dividends)."""

        return self.base_size + self.pnl

    @property
    def performance(self) -> float:
        """Capital weighted performance of the snapshot."""

        if not self.base_size:
            return 0

        return (self.total / (self.base_size + self.cash_flow)) - 1
