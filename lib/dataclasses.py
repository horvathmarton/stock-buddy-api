"""Dataclasses shared throughout the project."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict

from apps.stocks.models import Stock
from django.contrib.auth.models import User


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
    # TODO: Uncomment us!
    # ex_dividend_date: date
    # dividend_declaration_date: date

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, StockPositionSnapshot):
            return NotImplemented

        return (
            self.stock == o.stock
            and self.shares == o.shares
            and self.price == o.price
            and self.dividend == o.dividend
            and self.purchase_price == o.purchase_price
            and self.first_purchase_date == o.first_purchase_date
            and self.latest_purchase_date == o.latest_purchase_date
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
class StockPortfolioSnapshot:
    """
    Represents a portfolio at a given time.

    Contains a list of positions in the portfolio and the aggregate data.
    """

    # List of the summarized position in the current portfolio.
    positions: Dict[str, StockPositionSnapshot]
    owner: User

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, StockPortfolioSnapshot):
            return NotImplemented

        return self.positions == o.positions and self.owner == o.owner

    @property
    def assets_under_management(self) -> float:
        return sum((position.size for position in self.positions.values()))

    @property
    def capital_invested(self) -> float:
        return sum((position.size_at_cost for position in self.positions.values()))

    @property
    def dividend(self) -> float:
        return sum((position.dividend_income for position in self.positions.values()))

    @property
    def dividend_yield(self) -> float:
        return round(self.dividend / self.assets_under_management, 4)

    @property
    def number_of_positions(self) -> int:
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
            position.stock.ticker: round(position.dividend_income / self.dividend)
            for position in self.positions.values()
            if position.dividend_income > 0
        }
