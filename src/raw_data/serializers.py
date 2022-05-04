"""Serializers for the raw data payloads."""

from rest_framework import serializers

from .models import StockPrice, StockDividend, StockSplit


class StockPriceSerializer(serializers.ModelSerializer):
    """Serializer of the stock price model."""

    class Meta:
        model = StockPrice
        fields = ["date", "value"]


class StockDividendSerializer(serializers.ModelSerializer):
    """Serializer of the stock dividend model."""

    class Meta:
        model = StockDividend
        fields = ["declaration_date", "ex_dividend_date", "date", "amount"]


class StockSplitSerializer(serializers.ModelSerializer):
    """Serializer of the stock split model."""

    class Meta:
        model = StockSplit
        fields = ["date", "ratio"]
