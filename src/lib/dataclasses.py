from dataclasses import dataclass
from datetime import date

from src.stocks.models import Stock


@dataclass
class StockPosition:
    """
    Represents a position at a given time.
    """

    stock: Stock
    shares: int
    # Current price of one stock in USD.
    price: float
    # Current dividend of one stock for a full year in USD (forward looking).
    dividend: float
    # Averate purchase price of one stock in USD.
    purchase_price: float
    # Latest date when the position was changed.
    purchase_date: date

    def __init__(
        self,
        *,
        stock: Stock,
        shares: int,
        price: float,
        dividend: float,
        purchase_price: float,
        purchase_date: date
    ):
        self.stock = stock
        self.shares = shares
        self.price = price
        self.dividend = dividend
        self.purchase_price = purchase_price
        self.purchase_date = purchase_date

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, StockPosition):
            return NotImplemented

        return (
            self.stock == o.stock
            and self.shares == o.shares
            and self.price == o.price
            and self.dividend == o.dividend
            and self.purchase_price == o.purchase_price
            and self.purchase_date == o.purchase_date
        )

    # Position size at the current price in USD.
    @property
    def size_of_position(self) -> float:
        return self.shares * self.price

    # Position size at the purchase price in USD.
    @property
    def size_of_position_at_cost(self) -> float:
        return self.shares * self.purchase_price

    # Dividend yield in percentage (e.g.: 0.12 means 12%).
    @property
    def dividend_yield(self) -> float:
        return self.dividend / self.price

    # Dividend yield in percentage based on the purchase price (e.g.: 0.12 means 12%).
    @property
    def dividend_yield_on_cost(self) -> float:
        return self.dividend / self.purchase_price

    # Yearly dividend income from the position in USD (forward looking)
    @property
    def dividend_income(self) -> float:
        return self.shares * self.dividend

    # Percentage change from the purchase price (e.g.: 0.12 means 12%)
    @property
    def pnl_percentage(self) -> float:
        return (self.price - self.purchase_price) / self.purchase_price

    # Amount of PnL of the entire position in USD.
    @property
    def pnl(self) -> float:
        return self.shares * (self.price - self.purchase_price)
