from datetime import date
from typing import List

from src.raw_data.models import StockDividend, StockPrice
from src.stocks.models import Stock, StockPortfolio
from src.transactions.models import StockTransaction

from ..dataclasses import StockPosition


class FinanceService:
    @staticmethod
    def pv(
        rate: float,
        periods: float,
        periodic_payment: float,
        future_value: float = 0,
        paid_at_period_start: bool = False,
    ) -> float:
        """
        Present value. Discounts the provided value to present.
        """

        raise NotImplementedError("This function has not been implemented yet.")

    @staticmethod
    def fv(
        rate: float,
        periods: float,
        periodic_payment: float,
        present_value: float,
        paid_at_period_start: bool = False,
    ) -> float:
        """
        Future value. Compounds the provided value to future.
        """

        raise NotImplementedError("This function has not been implemented yet.")

    @staticmethod
    def rri(periods: float, present_value: float, future_value: float) -> float:
        """
        Rate of investment return.
        Calculate Compound Annual Growth Rate (CAGR).

        Rounding to four precision to avoid floating point math error.
        """

        return round((future_value / present_value) ** (1 / periods) - 1, 4)

    def internal_rate_of_return(self):
        raise NotImplementedError("This function has not been implemented yet.")

    def net_present_value(self):
        raise NotImplementedError("This function has not been implemented yet.")

    @classmethod
    def get_portfolio_snapshot(
        cls, portfolios: List[StockPortfolio], at: date = date.today()
    ) -> List[StockPosition]:
        """
        Returns the snapshot of the portfolio at a given time.
        """

        transactions = StockTransaction.objects.all().filter(portfolio__in=portfolios)

        positions = {}
        for transaction in transactions:
            ticker = transaction.ticker.ticker

            if ticker not in positions:
                latest_price = cls._get_latest_stock_price(ticker, at)
                latest_dividend = cls._get_latest_dividend(ticker, at)

                # The dividend info is multiplied by 4 to project the latest quarterly
                # value to the next year.
                positions[ticker] = StockPosition(
                    stock=transaction.ticker,
                    shares=transaction.amount,
                    price=latest_price,
                    dividend=latest_dividend * 4,
                    purchase_price=transaction.price,
                    first_purchase_date=transaction.date,
                    latest_purchase_date=transaction.date,
                )
            else:
                current_position = positions[ticker]

                # We only change the average price if we buy more stock.
                # We should keep the average untouched when selling.
                if transaction.amount >= 0:
                    current_position.purchase_price = (
                        current_position.size_of_position_at_cost
                        + (transaction.amount * transaction.price)
                    ) / (current_position.shares + transaction.amount)

                current_position.first_purchase_date = min(
                    current_position.first_purchase_date, transaction.date
                )
                current_position.latest_purchase_date = max(
                    current_position.latest_purchase_date, transaction.date
                )
                current_position.shares += transaction.amount

                if current_position.shares == 0:
                    del positions[ticker]
                elif current_position.shares < 0:
                    raise Exception("Negative position size is not allowed.")

        return list(positions.values())

    @staticmethod
    def _get_latest_stock_price(ticker: Stock, at: date) -> float:
        latest_price_date = (
            StockPrice.objects.filter(ticker=ticker, date__lte=at).latest("date").date
        )

        return StockPrice.objects.filter(ticker=ticker, date=latest_price_date)[0].value

    @staticmethod
    def _get_latest_dividend(ticker: Stock, at: date) -> float:
        try:
            latest_dividend_date = (
                StockDividend.objects.filter(ticker=ticker, payout_date__lte=at)
                .latest("payout_date")
                .payout_date
            )

            return StockDividend.objects.filter(
                ticker=ticker, payout_date=latest_dividend_date
            )[0].amount

        except StockDividend.DoesNotExist:
            # It is possible that the stock doesn't pay dividend
            # in that case we just return 0.
            return 0.0
