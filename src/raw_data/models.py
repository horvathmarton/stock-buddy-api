from django.contrib.auth.models import User
from django.db import models
from src.lib.enums import SyncStatus
from src.stocks.models import Stock


class StockPriceSync(models.Model):
    status = models.CharField(max_length=8,
                              choices=SyncStatus.choices, default=SyncStatus.STARTED)
    owner = models.ForeignKey(User, models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = '"raw_data"."stock_price_sync"'


class StockPrice(models.Model):
    ticker = models.ForeignKey(Stock, on_delete=models.RESTRICT)
    date = models.DateField()
    value = models.FloatField()
    sync = models.ForeignKey(StockPriceSync, models.RESTRICT)

    class Meta:
        db_table = '"raw_data"."stock_price"'


class StockSplitSync(models.Model):
    status = models.CharField(max_length=8,
                              choices=SyncStatus.choices, default=SyncStatus.STARTED)
    owner = models.ForeignKey(User, models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = '"raw_data"."stock_split_sync"'


class StockSplit(models.Model):
    ticker = models.ForeignKey(Stock, on_delete=models.RESTRICT)
    date = models.DateField()
    ratio = models.FloatField()
    sync = models.ForeignKey(StockSplitSync, models.RESTRICT)

    class Meta:
        db_table = '"raw_data"."stock_split"'


class StockDividendSync(models.Model):
    status = models.CharField(max_length=8,
                              choices=SyncStatus.choices, default=SyncStatus.STARTED)
    owner = models.ForeignKey(User, models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = '"raw_data"."stock_dividend_sync"'


class StockDividend(models.Model):
    ticker = models.ForeignKey(Stock, on_delete=models.RESTRICT)
    declaration_date = models.DateField(null=True)
    ex_dividend_date = models.DateField(null=True)
    payout_date = models.DateField()
    amount = models.FloatField()
    sync = models.ForeignKey(StockDividendSync, models.RESTRICT)

    class Meta:
        db_table = '"raw_data"."stock_dividend"'


class StockFiling(models.Model):
    ticker = models.ForeignKey(Stock, on_delete=models.RESTRICT)
    date = models.DateField()
    filename = models.TextField()
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = '"raw_data"."stock_filing"'
