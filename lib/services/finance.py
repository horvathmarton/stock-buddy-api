"""
Basic financial calculation realted services and functions.
"""

from logging import getLogger


LOGGER = getLogger(__name__)


class FinanceService:
    """Implements some basic Excel finance functions and a portfolio snapshot generator."""

    @staticmethod
    def present_value(
        rate: float,
        periods: float,
        periodic_payment: float,
        future_value: float = 0,
        paid_at_period_start: bool = False,
    ) -> float:
        """Present value. Discounts the provided value to present."""

        raise NotImplementedError("This function has not been implemented yet.")

    @staticmethod
    def future_value(
        rate: float,
        periods: float,
        periodic_payment: float,
        present_value: float,
        paid_at_period_start: bool = False,
    ) -> float:
        """Future value. Compounds the provided value to future."""

        raise NotImplementedError("This function has not been implemented yet.")

    @staticmethod
    def rri(periods: float, present_value: float, future_value: float) -> float:
        """
        Rate of investment return.
        Calculate Compound Annual Growth Rate (CAGR).

        Rounding to four precision to avoid floating point math error.
        """

        LOGGER.debug("Calculating rate of investment return.")

        return round((future_value / present_value) ** (1 / periods) - 1, 4)

    def internal_rate_of_return(self) -> str:
        """Calculates the internal rate of return (IRR) from a list of cash flows."""

        raise NotImplementedError("This function has not been implemented yet.")

    def net_present_value(self):
        """Discounts the net present value form a list of cash flows at the discount rate."""

        raise NotImplementedError("This function has not been implemented yet.")
