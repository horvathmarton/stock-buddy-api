"""General helper functions for the stocks module."""

from itertools import groupby

from .dataclasses import (
    PositionSize,
    TargetPrice,
    Watchlist,
    WatchlistItem,
    WatchlistRow,
)


def parse_watchlist_rows(cursor):
    """Parse the result of the watchlist details query to a tree structure."""

    rows = [
        WatchlistRow(
            watchlist_id=i[0],
            stock_id=i[1],
            item_type=i[2],
            watchlist_name=i[3],
            watchlist_description=i[4],
            target_id=i[5],
            price=i[6],
            size=i[7],
            at_cost=i[8],
            target_description=i[9],
        )
        for i in cursor
    ]

    result = []
    for watchlist_id, watchlist in groupby(rows, key=lambda x: x.watchlist_id):
        items = list(watchlist)
        watchlist = Watchlist(
            id=watchlist_id,
            name=items[0].watchlist_name,
            description=items[0].watchlist_description,
            items=[],
        )

        for ticker, item in groupby(items, key=lambda x: x.stock_id):
            targets = list(item)
            item = WatchlistItem(
                ticker=ticker,
                target_prices=[
                    TargetPrice(target.price, target.target_description)
                    for target in targets
                    if target.item_type == "target_price"
                ],
                position_sizes=[
                    PositionSize(target.size, target.at_cost, target.target_description)
                    for target in targets
                    if target.item_type == "position_size"
                ],
            )

            watchlist.items.append(item)

        result.append(watchlist)

    return result
