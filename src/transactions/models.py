from django.db import models
from src.stocks.models import Stock
from django.contrib.auth.models import User
from .enums import Currency

class CashTransaction(models.Model):
    currency = models.CharField(max_length=3, choices=Currency.choices)
    amount = models.FloatField()
    date = models.DateField()
    owner = models.ForeignKey(User, models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = '"transactions"."cash_transaction"'


class ForexTransaction(models.Model):
    date = models.DateField()
    amount = models.FloatField()
    ratio = models.FloatField()
    source_currency = models.CharField(max_length=3, choices=Currency.choices)
    target_currency = models.CharField(max_length=3, choices=Currency.choices)
    owner = models.ForeignKey(User, models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = '"transactions"."forex_transaction"'


class StockTransaction(models.Model):
    ticker = models.ForeignKey(Stock, on_delete=models.RESTRICT)
    amount = models.FloatField()
    price = models.FloatField()
    date = models.DateField()
    owner = models.ForeignKey(User, models.RESTRICT)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = '"transactions"."stock_transaction"'
