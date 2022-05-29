"""Dataclasses related to the stocks module."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class WatchlistRow:
    """Represents a row from the watchlist details query result."""

    # pylint: disable=too-many-instance-attributes

    watchlist_id: int
    stock_id: str
    item_type: str
    watchlist_name: str
    watchlist_description: Optional[str]
    target_id: int
    price: float
    size: float
    at_cost: bool
    target_description: Optional[str]


@dataclass
class TargetPrice:
    """Represents a target price item in the app."""

    price: float
    description: Optional[str]


@dataclass
class PositionSize:
    """Represents a position size item in the app."""

    size: float
    at_cost: bool
    description: Optional[str]


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
