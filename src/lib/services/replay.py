from copy import deepcopy
from datetime import date
from typing import TypeVar, Callable

T = TypeVar("T")
U = TypeVar("U")


def generate_snapshot_series(
    initial: T,
    actions: list[U],
    series: list[date],
    operation: Callable[[T, U], T],
    take_snapshot: Callable[[T, date], T],
) -> dict[date, T]:
    if not series:
        return {}

    series = sorted(series)
    current_state = deepcopy(initial)

    snapshot_series = {}
    for action in actions:
        # Take a snapshot if the next action would not affect the next snapshot date.
        while series and action.date > series[0]:
            snapshot_date = series.pop()
            snapshot_series[snapshot_date] = take_snapshot(current_state, snapshot_date)

        current_state = operation(current_state, action)

    # When we are done with the replay we take all the snapshots after the last action.
    while series:
        snapshot_date = series.pop()
        snapshot_series[snapshot_date] = take_snapshot(current_state, snapshot_date)

    return snapshot_series
