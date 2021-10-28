from django.db import models


class Stock(models.Model):
    ticker = models.CharField(primary_key=True, max_length=16)
    name = models.TextField()

    class Meta:
        db_table = '"raw_data"."stock"'


class StockPrice(models.Model):
    ticker = models.ForeignKey(Stock, on_delete=models.RESTRICT)
    date = models.DateField()
    value = models.FloatField()

    class Meta:
        db_table = '"raw_data"."stock_price"'


class StockSplit(models.Model):
    ticker = models.ForeignKey(Stock, on_delete=models.RESTRICT)
    date = models.DateField()
    ratio = models.FloatField()

    class Meta:
        db_table = '"raw_data"."stock_split"'


class StockDividend(models.Model):
    ticker = models.ForeignKey(Stock, on_delete=models.RESTRICT)
    declaration_date = models.DateField()
    ex_dividend_date = models.DateField()
    payout_date = models.DateField()
    amount = models.FloatField()

    class Meta:
        db_table = '"raw_data"."stock_dividend"'


class StockFiling(models.Model):
    ticker = models.ForeignKey(Stock, on_delete=models.RESTRICT)
    date = models.DateField()
    filename = models.TextField()
    url = models.URLField()

    class Meta:
        db_table = '"raw_data"."stock_filing"'
