"""General helper functions for the app."""

from datetime import date, datetime, timedelta
from typing import Optional

from dateutil import parser
from rest_framework.exceptions import ParseError
from rest_framework.request import Request

from .dataclasses import Interval, StockPortfolioSnapshot


def parse_date_query_param(
    request: Request, param_name: str, required: bool = False
) -> Optional[date]:
    """
    Plucks the param name from the request and tries to parse as date.

    Throws 400 if required and not provided or malformed.
    """

    query_param = request.query_params.get(param_name, None)

    if not query_param and required:
        raise ParseError(f"{param_name} query param is required")

    if not query_param:
        return None

    try:
        return datetime.strptime(query_param, "%Y-%m-%d").date()
    except ValueError as error:
        raise ParseError(f"Invalid date in {param_name} query param") from error


def get_latest_snapshot(
    target_date: date, snapshots: dict[date, StockPortfolioSnapshot]
) -> Optional[StockPortfolioSnapshot]:
    """Returns latest snapshot from a series that was taken before the target date."""

    sorted_snapshots = sorted(
        (
            (date, snapshot)
            for date, snapshot in snapshots.items()
            if date <= target_date
        ),
        key=lambda x: x[0],
    )

    return sorted_snapshots[0][1] if sorted_snapshots else None


def get_range(request: Request) -> Interval:
    """Parses the range query params or add fallback to an interval."""

    from_param = request.query_params.get("from")
    to_param = request.query_params.get("to")

    start_date = (
        parser.parse(from_param).date()
        if from_param
        else datetime.today().date() - timedelta(days=365)
    )
    end_date = parser.parse(to_param).date() if to_param else datetime.today().date()

    return Interval(
        start_date=start_date,
        end_date=end_date,
    )
