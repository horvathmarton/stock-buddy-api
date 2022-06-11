"""Dataclasses related to the stocks module."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class StockListItemRow:
    """Represents a row from the latest stock prices query result."""

    ticker: str
    name: str
    sector: str
    date: str
    price: float
    last_updated: datetime


@dataclass
class WatchlistRow:
    """Represents a row from the watchlist details query result."""

    # pylint: disable=too-many-instance-attributes

    watchlist_id: int
    watchlist_name: str
    stock_id: Optional[str]
    item_type: Optional[str]
    watchlist_description: Optional[str]
    target_id: Optional[int]
    target_name: Optional[str]
    price: Optional[float]
    size: Optional[float]
    at_cost: Optional[bool]


@dataclass
class TargetPrice:
    """Represents a target price item in the app."""

    name: str
    price: float


@dataclass
class PositionSize:
    """Represents a position size item in the app."""

    name: str
    size: float
    at_cost: bool


@dataclass
class WatchlistItem:
    """Represents a monitored item from a watchlist."""

    ticker: str
    target_prices: list[TargetPrice]
    position_sizes: list[PositionSize]


@dataclass
class Watchlist:
    """Represents a watchlist with its details."""

    # pylint: disable=invalid-name

    id: int
    name: str
    description: Optional[str]
    items: list[WatchlistItem]
