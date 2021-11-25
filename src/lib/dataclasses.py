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
    # Date when the position was initiated.
    first_purchase_date: date
    # Latest date when the position was changed.
    latest_purchase_date: date

    def __init__(
        self,
        *,
        stock: Stock,
        shares: int,
        price: float,
        dividend: float,
        purchase_price: float,
        first_purchase_date: date,
        latest_purchase_date: date,
    ):
        self.stock = stock
        self.shares = shares
        self.price = price
        self.dividend = dividend
        self.purchase_price = purchase_price
        self.first_purchase_date = first_purchase_date
        self.latest_purchase_date = latest_purchase_date

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, StockPosition):
            return NotImplemented

        return (
            self.stock == o.stock
            and self.shares == o.shares
            and self.price == o.price
            and self.dividend == o.dividend
            and self.purchase_price == o.purchase_price
            and self.first_purchase_date == o.first_purchase_date
            and self.latest_purchase_date == o.latest_purchase_date
        )

    # Position size at the current price in USD.
    @property
    def size_of_position(self) -> float:
        return round(self.shares * self.price, 2)

    # Position size at the purchase price in USD.
    @property
    def size_of_position_at_cost(self) -> float:
        return round(self.shares * self.purchase_price, 2)

    # Dividend yield in percentage (e.g.: 0.12 means 12%).
    @property
    def dividend_yield(self) -> float:
        return round(self.dividend / self.price, 4)

    # Dividend yield in percentage based on the purchase price (e.g.: 0.12 means 12%).
    @property
    def dividend_yield_on_cost(self) -> float:
        return round(self.dividend / self.purchase_price, 4)

    # Yearly dividend income from the position in USD (forward looking)
    @property
    def dividend_income(self) -> float:
        return round(self.shares * self.dividend, 2)

    # Percentage change from the purchase price (e.g.: 0.12 means 12%)
    @property
    def pnl_percentage(self) -> float:
        return round((self.price - self.purchase_price) / self.purchase_price, 4)

    # Amount of PnL of the entire position in USD.
    @property
    def pnl(self) -> float:
        return round(self.shares * (self.price - self.purchase_price), 2)
