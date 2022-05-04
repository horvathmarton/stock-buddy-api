"""
Basic financial calculation realted services and functions.
"""

from logging import getLogger


LOGGER = getLogger(__name__)


def rri(periods: float, present_value: float, future_value: float) -> float:
    """
    Rate of investment return.
    Calculate Compound Annual Growth Rate (CAGR).

    Rounding to four precision to avoid floating point math error.
    """

    LOGGER.debug("Calculating rate of investment return.")

    # We can't interpret zero period count.
    # In this case the return is 0.
    if not periods:
        return 0.0

    # We can't interpret zero starting capital.
    # In this case the return is 0.
    if not present_value:
        return 0.0

    return round((future_value / present_value) ** (1 / periods) - 1, 4)
