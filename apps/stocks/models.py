from django.contrib.auth.models import User
from django.db.models import (
    RESTRICT,
    BooleanField,
    CharField,
    DateTimeField,
    ForeignKey,
    Model,
    TextField,
)

from .enums import Sector


class Stock(Model):
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
    name: TextField = TextField()
    description: TextField = TextField(null=True)

    owner: ForeignKey = ForeignKey(User, RESTRICT)
    created_at: DateTimeField = DateTimeField(auto_now_add=True)
    updated_at: DateTimeField = DateTimeField(auto_now=True)

    class Meta:
        db_table = '"stocks"."stock_watchlist"'

    def __str__(self):
        return self.name
