"""Complex and/or shared queries."""

from datetime import date

from django.db import connection

from ..stocks.models import StockPortfolio


def sum_cash_transactions(portfolios: list[StockPortfolio], snapshot_date: date):
    """
    Calculate the cash balance of the given protfolios by summarizing the cash transactions as inflows,
    forex transactions as exchanges and stock transactions as outflows.
    """
    params = {
        "portfolio_ids": tuple(portfolio.id for portfolio in portfolios)  # type: ignore
        if portfolios
        else (None,),
        "as_of": snapshot_date,
    }

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            SUM(usd) AS usd, SUM(eur) AS eur, SUM(huf) AS huf
        FROM (
        SELECT
            -1 * amount * price AS usd, 0 AS eur, 0 AS huf
        FROM
            transactions.stock_transaction
        WHERE
            portfolio_id IN %(portfolio_ids)s
            AND date <= %(as_of)s
        UNION
        SELECT
            SUM(amount) FILTER(WHERE currency = 'USD') AS usd,
            SUM(amount) FILTER(WHERE currency = 'EUR') AS eur,
            SUM(amount) FILTER(WHERE currency = 'HUF') AS huf
        FROM
            transactions.cash_transaction
        WHERE
            portfolio_id IN %(portfolio_ids)s
            AND date <= %(as_of)s
        UNION
        SELECT
            COALESCE(SUM(ratio * amount) FILTER(WHERE target_currency = 'USD'), 0)
            - COALESCE(SUM(amount) FILTER(WHERE source_currency = 'USD'), 0) AS usd,
            COALESCE(SUM(ratio * amount) FILTER(WHERE target_currency = 'EUR'), 0)
            - COALESCE(SUM(amount) FILTER(WHERE source_currency = 'EUR'), 0) AS eur,
            COALESCE(SUM(ratio * amount) FILTER(WHERE target_currency = 'HUF'), 0)
            - COALESCE(SUM(amount) FILTER(WHERE source_currency = 'HUF'), 0) AS huf
        FROM
            transactions.forex_transaction
        WHERE
            portfolio_id IN %(portfolio_ids)s
            AND date <= %(as_of)s) AS partials;
        """,
        params=params,  # type: ignore
    )

    return cursor.fetchone()


def fetch_watchlist_tree(watchlist_id: int):
    """
    Calculate a full details tree for a watchlist containing each child.

    Watchlist
    -> Items
        -> Target prices
        -> Position sizes
    """

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            watchlist.id,
            items.stock_id,
            items.type,
            watchlist.name,
            watchlist.description,
            items.target_id,
            items.price,
            items.size,
            items.at_cost,
            items.description
        FROM
            stocks.stock_watchlist AS watchlist
            LEFT JOIN (
                SELECT
                    items.stock_id,
                    items.watchlist_id,
                    targets.id AS target_id,
                    targets.price AS price,
                    targets.size AS size,
                    targets.at_cost AS at_cost,
                    targets.description AS description,
                    targets.type AS type
                FROM
                    stocks.stock_watchlist_item AS items
                    LEFT JOIN (
                        SELECT
                            id,
                            price,
                            NULL AS size,
                            NULL AS at_cost,
                            description,
                            watchlist_item_id,
                            'target_price' AS type
                        FROM
                            stocks.target_price
                    UNION
                    SELECT
                        id,
                        NULL,
                        size,
                        at_cost,
                        description,
                        watchlist_item_id,
                        'position_size' AS type
                    FROM
                        stocks.position_size) AS targets ON targets.watchlist_item_id = items.id) AS items
                        ON items.watchlist_id = watchlist.id
        WHERE
            watchlist.id = %(watchlist_id)s
        ORDER BY watchlist.id ASC, items.stock_id ASC, items.type ASC;
    """,
        params={"watchlist_id": watchlist_id},
    )

    return cursor
