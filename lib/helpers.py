"""General helper functions for the app."""

from datetime import date, datetime

from rest_framework.exceptions import ParseError
from rest_framework.request import Request


def parse_date_query_param(
    request: Request, param_name: str, required: bool = False
) -> date | None:
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
