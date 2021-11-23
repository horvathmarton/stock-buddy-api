from datetime import date
from typing import List

from src.raw_data.models import StockDividend, StockPrice
from src.stocks.models import Stock, StockPortfolio
from src.transactions.models import StockTransaction

from ..dataclasses import StockPosition


class FinanceService:
    def rate_of_investment_return(self):
        pass

    def internal_rate_of_return(self):
        pass

    def present_value(self):
        pass

    def future_value(self):
        pass

    def net_present_value(self):
        pass

    def get_portfolio_snapshot(
        self, portfolio: StockPortfolio, at: date = date.today()
    ) -> List[StockPosition]:
        """
        Returns the snapshot of the portfolio at a given time.
        """

        # TODO: We don't account for stock splits currently this should be fixed in the future.

        transactions = StockTransaction.objects.all().filter(portfolio=portfolio)

        positions = {}
        for transaction in transactions:
            ticker = transaction.ticker.ticker

            if ticker not in positions:
                latest_price = self._get_latest_stock_price(ticker, at)
                latest_dividend = self._get_latest_dividend(ticker, at)

                # The dividend info is multiplied by 4 to project the latest quarterly
                # value to the next year.
                positions[ticker] = StockPosition(
                    stock=transaction.ticker,
                    shares=transaction.amount,
                    price=latest_price,
                    dividend=latest_dividend * 4,
                    purchase_price=transaction.price,
                    purchase_date=transaction.date,
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

                current_position.purchase_date = max(
                    current_position.purchase_date, transaction.date
                )
                current_position.shares += transaction.amount

                if current_position.shares == 0:
                    del positions[ticker]
                elif current_position.shares < 0:
                    raise Exception("Negative position size is not allowed.")

        return list(positions.values())

    def _get_latest_stock_price(self, ticker: Stock, at: date) -> float:
        latest_price_date = (
            StockPrice.objects.filter(ticker=ticker, date__lte=at).latest("date").date
        )

        return StockPrice.objects.filter(ticker=ticker, date=latest_price_date)[0].value

    def _get_latest_dividend(self, ticker: Stock, at: date) -> float:
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
