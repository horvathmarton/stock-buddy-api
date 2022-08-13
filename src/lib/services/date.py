"""Service functions for date and time related operations."""

from datetime import date, timedelta

from ..dataclasses import Interval
from ..enums import Resolution


def get_resolution(interval: Interval) -> Resolution:
    """Suggest a sensible resolution to generate a timeseries for a given interval."""

    if interval.start_date > interval.end_date:
        raise Exception("Cannot process inverse interval.")

    elapsed_days = (interval.end_date - interval.start_date).days

    if elapsed_days < 30:
        return Resolution.DAY
    if elapsed_days < 90:
        return Resolution.WEEK
    if elapsed_days < 365:
        return Resolution.MONTH
    if elapsed_days < 365 * 3:
        return Resolution.QUARTER

    return Resolution.YEAR


def get_timeseries(interval: Interval, resolution: Resolution) -> list[date]:
    """
    Generate a timeseries within an interval with the provided resolution.

    start_date <= timeseries < end_date
    """

    if interval.start_date > interval.end_date:
        raise Exception("Cannot process inverse interval.")

    elapsed_days = (interval.end_date - interval.start_date).days

    return [
        interval.start_date + timedelta(days=days)
        for days in range(0, elapsed_days, resolution.value)
    ]
