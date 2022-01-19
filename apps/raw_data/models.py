"""Models related to the raw data schema."""

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
    URLField,
)
from lib.enums import SyncStatus
from apps.stocks.models import Stock


class StockPriceSync(Model):
    """Represents a sync action for stock prices."""

    status: CharField = CharField(
        max_length=8, choices=SyncStatus.choices, default=SyncStatus.STARTED
    )
    owner: ForeignKey = ForeignKey(User, RESTRICT)
    created_at: DateTimeField = DateTimeField(auto_now_add=True)
    updated_at: DateTimeField = DateTimeField(auto_now=True)

    class Meta:
        db_table = '"raw_data"."stock_price_sync"'


class StockPrice(Model):
    """Represents a stock price on a given date."""

    ticker: ForeignKey = ForeignKey(Stock, on_delete=RESTRICT)
    date: DateField = DateField()
    value: FloatField = FloatField()
    sync: ForeignKey = ForeignKey(StockPriceSync, RESTRICT)

    class Meta:
        db_table = '"raw_data"."stock_price"'
        ordering = ["date"]


class StockSplitSync(Model):
    """Represents a sync action for stock splits."""

    status: CharField = CharField(
        max_length=8, choices=SyncStatus.choices, default=SyncStatus.STARTED
    )
    owner: ForeignKey = ForeignKey(User, RESTRICT)
    created_at: DateTimeField = DateTimeField(auto_now_add=True)
    updated_at: DateTimeField = DateTimeField(auto_now=True)

    class Meta:
        db_table = '"raw_data"."stock_split_sync"'


class StockSplit(Model):
    """Represents a stock split."""

    ticker: ForeignKey = ForeignKey(Stock, on_delete=RESTRICT)
    date: DateField = DateField()
    ratio: FloatField = FloatField()
    sync: ForeignKey = ForeignKey(StockSplitSync, RESTRICT)

    class Meta:
        db_table = '"raw_data"."stock_split"'
        ordering = ["date"]


class StockDividendSync(Model):
    """Represents a sync action for stock dividends."""

    status: CharField = CharField(
        max_length=8, choices=SyncStatus.choices, default=SyncStatus.STARTED
    )
    owner: ForeignKey = ForeignKey(User, RESTRICT)
    created_at: DateTimeField = DateTimeField(auto_now_add=True)
    updated_at: DateTimeField = DateTimeField(auto_now=True)

    class Meta:
        db_table = '"raw_data"."stock_dividend_sync"'


class StockDividend(Model):
    """Represents a stock dividend."""

    ticker: ForeignKey = ForeignKey(Stock, on_delete=RESTRICT)
    declaration_date: DateField = DateField(null=True)
    ex_dividend_date: DateField = DateField(null=True)
    payout_date: DateField = DateField()
    amount: FloatField = FloatField()
    sync: ForeignKey = ForeignKey(StockDividendSync, RESTRICT)

    class Meta:
        db_table = '"raw_data"."stock_dividend"'
        ordering = ["payout_date"]


class StockFiling(Model):
    """Represents a stock filing."""

    ticker: ForeignKey = ForeignKey(Stock, on_delete=RESTRICT)
    date: DateField = DateField()
    filename: TextField = TextField()
    url: URLField = URLField()
    created_at: DateTimeField = DateTimeField(auto_now_add=True)
    updated_at: DateTimeField = DateTimeField(auto_now=True)

    class Meta:
        db_table = '"raw_data"."stock_filing"'
