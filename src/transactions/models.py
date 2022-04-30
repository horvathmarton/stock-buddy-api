"""Models related to the transactions schema."""

from django.contrib.auth.models import User
from django.db.models import (
    RESTRICT,
    CharField,
    DateField,
    DateTimeField,
    FloatField,
    ForeignKey,
    Model,
    TextField,
)

from ..stocks.models import Stock, StockPortfolio
from .enums import Currency


class CashTransaction(Model):
    """Represents a single transaction where the user deposits or withdraws money from the account."""

    currency: CharField = CharField(max_length=3, choices=Currency.choices)
    amount: FloatField = FloatField()
    date: DateField = DateField()

    owner: ForeignKey = ForeignKey(User, RESTRICT)
    portfolio: ForeignKey = ForeignKey(StockPortfolio, RESTRICT)
    created_at: DateTimeField = DateTimeField(auto_now_add=True)
    updated_at: DateTimeField = DateTimeField(auto_now=True)

    class Meta:
        db_table = '"transactions"."cash_transaction"'
        ordering = ["date"]


class ForexTransaction(Model):
    """Represents a single transaction where the user converts between currencies."""

    date: DateField = DateField()
    amount: FloatField = FloatField()
    ratio: FloatField = FloatField()
    source_currency: CharField = CharField(max_length=3, choices=Currency.choices)
    target_currency: CharField = CharField(max_length=3, choices=Currency.choices)

    owner: ForeignKey = ForeignKey(User, RESTRICT)
    portfolio: ForeignKey = ForeignKey(StockPortfolio, RESTRICT)
    created_at: DateTimeField = DateTimeField(auto_now_add=True)
    updated_at: DateTimeField = DateTimeField(auto_now=True)

    class Meta:
        db_table = '"transactions"."forex_transaction"'
        ordering = ["date"]


class StockTransaction(Model):
    """Represents a single transaction where the user buys or sells a stock."""

    ticker: ForeignKey = ForeignKey(Stock, on_delete=RESTRICT)
    amount: FloatField = FloatField()
    price: FloatField = FloatField()
    date: DateField = DateField()
    comment: TextField = TextField(null=True)

    owner: ForeignKey = ForeignKey(User, RESTRICT)
    portfolio: ForeignKey = ForeignKey(StockPortfolio, RESTRICT)
    created_at: DateTimeField = DateTimeField(auto_now_add=True)
    updated_at: DateTimeField = DateTimeField(auto_now=True)

    class Meta:
        db_table = '"transactions"."stock_transaction"'
        ordering = ["date"]
