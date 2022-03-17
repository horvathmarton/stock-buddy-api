"""Complex and/or shared queries."""

from datetime import date
from django.db import connection
from apps.stocks.models import StockPortfolio


def sum_cash_transactions(portfolios: list[StockPortfolio], snapshot_date: date):
    """
    Calculate the cash balance of the given protfolios by summarizing the cash transactions as inflows,
    forex transactions as exchanges and stock transactions as outflows.
    """
    params = {
        "portfolio_ids": tuple(
            portfolio.id for portfolio in portfolios  # type: ignore
        ),
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
