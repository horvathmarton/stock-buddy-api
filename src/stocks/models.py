from django.db import models


class Stock(models.Model):
    ticker = models.CharField(primary_key=True, max_length=8)
    name = models.TextField()
    description = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = '"stocks"."stock"'

    def __str__(self):
        return self.name


class StockPortfolio(models.Model):
    name = models.TextField()
    description = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = '"stocks"."stock_portfolio"'
