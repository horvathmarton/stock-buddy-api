from django.contrib.auth.models import User
from django.db import models

from .enums import Sector

class Stock(models.Model):
    ticker = models.CharField(primary_key=True, max_length=8)
    name = models.TextField()
    description = models.TextField(null=True)
    sector = models.CharField(max_length=20, choices=Sector.choices)

    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = '"stocks"."stock"'

    def __str__(self):
        return self.name


class StockPortfolio(models.Model):
    name = models.TextField()
    description = models.TextField(null=True)

    owner = models.ForeignKey(User, models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = '"stocks"."stock_portfolio"'

    def __str__(self):
        return self.name


class StockWatchlist(models.Model):
    name = models.TextField()
    description = models.TextField(null=True)

    owner = models.ForeignKey(User, models.RESTRICT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = '"stocks"."stock_watchlist"'

    def __str__(self):
        return self.name
