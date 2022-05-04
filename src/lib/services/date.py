from datetime import date, timedelta

from ..dataclasses import Interval
from ..enums import Resolution


def get_resolution(interval: Interval) -> Resolution:
    elapsed_days = (interval.end_date - interval.start_date).days

    if elapsed_days < 7:
        return Resolution.DAY
    elif elapsed_days < 30:
        return Resolution.WEEK
    elif elapsed_days < 90:
        return Resolution.MONTH
    elif elapsed_days < 365:
        return Resolution.QUARTER
    else:
        return Resolution.YEAR


def get_timeseries(interval: Interval) -> list[date]:
    resolution = get_resolution(interval)
    elapsed_days = (interval.end_date - interval.start_date).days

    return [
        interval.start_date + timedelta(days=days)
        for days in range(0, elapsed_days, resolution.value)
    ]
