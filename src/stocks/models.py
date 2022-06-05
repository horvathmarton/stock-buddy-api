"""Models related to the stocks schema."""

from django.contrib.auth.models import User
from django.db.models import (
    CASCADE,
    RESTRICT,
    BooleanField,
    CharField,
    DateTimeField,
    ForeignKey,
    Model,
    TextField,
    UniqueConstraint,
    FloatField,
)

from .enums import Sector


class Stock(Model):
    """Represents a stock tracked by the application."""

    ticker: CharField = CharField(primary_key=True, max_length=8)
    name: TextField = TextField()
    description: TextField = TextField(null=True)
    sector: CharField = CharField(max_length=20, choices=Sector.choices)

    active: BooleanField = BooleanField(default=False)
    created_at: DateTimeField = DateTimeField(auto_now_add=True)
    updated_at: DateTimeField = DateTimeField(auto_now=True)

    class Meta:
        db_table = '"stocks"."stock"'

    def __str__(self):
        return self.name


class StockPortfolio(Model):
    """
    Represents an existing or imaginary portfolio of stocks where each stock has a share count associated to it.
    """

    name: TextField = TextField()
    description: TextField = TextField(null=True)

    owner: ForeignKey = ForeignKey(User, RESTRICT)
    created_at: DateTimeField = DateTimeField(auto_now_add=True)
    updated_at: DateTimeField = DateTimeField(auto_now=True)

    class Meta:
        db_table = '"stocks"."stock_portfolio"'

    def __str__(self):
        return self.name


class StockWatchlist(Model):
    """Represents a stock watchlist which is a list of stocks tracked by the user."""

    name: TextField = TextField()
    description: TextField = TextField(null=True)

    owner: ForeignKey = ForeignKey(User, RESTRICT)
    created_at: DateTimeField = DateTimeField(auto_now_add=True)
    updated_at: DateTimeField = DateTimeField(auto_now=True)

    class Meta:
        db_table = '"stocks"."stock_watchlist"'

    def __str__(self):
        return self.name


class StockWatchlistItem(Model):
    """Represents a monitored stock on a watchlist."""

    watchlist: ForeignKey = ForeignKey(StockWatchlist, CASCADE)
    stock: ForeignKey = ForeignKey(Stock, RESTRICT)

    created_at: DateTimeField = DateTimeField(auto_now_add=True)
    updated_at: DateTimeField = DateTimeField(auto_now=True)

    class Meta:
        db_table = '"stocks"."stock_watchlist_item"'
        constraints = [
            UniqueConstraint(fields=["watchlist", "stock"], name="unique item")
        ]

    def __str__(self):
        # pylint: disable=no-member

        return f"{self.watchlist.name} - {self.stock.ticker}"


class TargetPrice(Model):
    """Represents a set target price for a watchlist item."""

    name: TextField = TextField()
    price: FloatField = FloatField()
    watchlist_item: ForeignKey = ForeignKey(StockWatchlistItem, CASCADE)

    created_at: DateTimeField = DateTimeField(auto_now_add=True)
    updated_at: DateTimeField = DateTimeField(auto_now=True)

    class Meta:
        db_table = '"stocks"."target_price"'

    def __str__(self):
        return f"{self.watchlist_item} - {self.price}"


class PositionSize(Model):
    """Represents a set position size limit for a watchlist item."""

    name: TextField = TextField()
    size: FloatField = FloatField()
    at_cost: BooleanField = BooleanField(default=True)
    watchlist_item: ForeignKey = ForeignKey(StockWatchlistItem, CASCADE)

    created_at: DateTimeField = DateTimeField(auto_now_add=True)
    updated_at: DateTimeField = DateTimeField(auto_now=True)

    class Meta:
        db_table = '"stocks"."position_size"'

    def __str__(self):
        return f"{self.watchlist_item} - {self.size}"
