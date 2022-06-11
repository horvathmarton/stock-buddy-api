"""General helper functions for the stocks module."""

from itertools import groupby
from typing import cast

from .dataclasses import (
    PositionSize,
    TargetPrice,
    Watchlist,
    WatchlistItem,
    WatchlistRow,
)


def parse_watchlist_rows(rows: list[WatchlistRow]) -> list[Watchlist]:
    """Parse the result of the watchlist details query to a tree structure."""

    result = []
    for watchlist_id, group in groupby(rows, key=lambda x: x.watchlist_id):
        items = list(group)
        watchlist = Watchlist(
            id=watchlist_id,
            name=items[0].watchlist_name,
            description=items[0].watchlist_description,
            items=[],
        )

        for ticker, inner_group in groupby(items, key=lambda x: x.stock_id):
            if ticker:
                targets = list(inner_group)
                item = WatchlistItem(
                    ticker=ticker,
                    target_prices=[
                        TargetPrice(
                            cast(str, target.target_name), cast(float, target.price)
                        )
                        for target in targets
                        if target.item_type == "target_price"
                    ],
                    position_sizes=[
                        PositionSize(
                            cast(str, target.target_name),
                            cast(float, target.size),
                            cast(bool, target.at_cost),
                        )
                        for target in targets
                        if target.item_type == "position_size"
                    ],
                )

                watchlist.items.append(item)

        result.append(watchlist)

    return result
