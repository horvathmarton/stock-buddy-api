"""Serializers for the stocks payloads."""

from rest_framework import serializers

from .models import Stock, StockPortfolio, StockWatchlist


class StockSerializer(serializers.ModelSerializer):
    """Serializer of the stock model."""

    class Meta:
        model = Stock
        fields = ("ticker", "name", "description", "sector")


class StockPortfolioSerializer(serializers.ModelSerializer):
    """Serializer of the stock portfolio model."""

    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = StockPortfolio
        fields = ("id", "name", "description", "owner")


class StockWatchlistSerializer(serializers.ModelSerializer):
    """Serializer of the stock watchlist model."""

    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = StockWatchlist
        fields = ("id", "name", "description", "owner")


class StockPositionSnapshotSerializer(serializers.Serializer):
    """Serializer of the stock position snapshot payload."""

    # pylint: disable=abstract-method

    ticker = serializers.ReadOnlyField(source="stock.ticker")
    name = serializers.ReadOnlyField(source="stock.name")
    sector = serializers.ReadOnlyField(source="stock.sector")
    price = serializers.FloatField()
    shares = serializers.IntegerField()
    dividend = serializers.FloatField()
    purchase_price = serializers.FloatField()
    first_purchase_date = serializers.DateField()
    latest_purchase_date = serializers.DateField()

    size = serializers.FloatField()
    size_at_cost = serializers.FloatField()
    dividend_yield = serializers.FloatField()
    dividend_yield_on_cost = serializers.FloatField()
    dividend_income = serializers.FloatField()
    pnl_percentage = serializers.FloatField()
    pnl = serializers.FloatField()


class StockPortfolioSnapshotSerializer(serializers.Serializer):
    """Serializer of the stock portfolio snapshot payload."""

    # pylint: disable=abstract-method

    positions = serializers.DictField(child=StockPositionSnapshotSerializer())
    sector_distribution = serializers.DictField(child=serializers.FloatField())
    size_distribution = serializers.DictField(child=serializers.FloatField())
    size_at_cost_distribution = serializers.DictField(child=serializers.FloatField())
    dividend_distribution = serializers.DictField(child=serializers.FloatField())

    assets_under_management = serializers.FloatField()
    capital_invested = serializers.FloatField()
    dividend = serializers.FloatField()
    dividend_yield = serializers.FloatField()
    number_of_positions = serializers.IntegerField()

    owner = serializers.ReadOnlyField(source="owner.username")
