"""Protocol definitions for the app."""

from datetime import date
from typing import Protocol


class DateBound(Protocol):
    """Represents any entity that belongs to a specific date."""

    # pylint: disable=too-few-public-methods

    date: date
