"""Serializers for the stocks payloads."""

from rest_framework.serializers import (
    BooleanField,
    CharField,
    DateField,
    DictField,
    FloatField,
    IntegerField,
    ModelSerializer,
    ReadOnlyField,
    Serializer,
)

from .models import Stock, StockPortfolio, StockWatchlist


class StockSerializer(ModelSerializer):
    """Serializer of the stock model."""

    class Meta:
        model = Stock
        fields = ("ticker", "name", "description", "sector")


class StockPortfolioSerializer(ModelSerializer):
    """Serializer of the stock portfolio model."""

    owner = ReadOnlyField(source="owner.username")

    class Meta:
        model = StockPortfolio
        fields = ("id", "name", "description", "owner")


class StockWatchlistSerializer(ModelSerializer):
    """Serializer of the stock watchlist model."""

    owner = ReadOnlyField(source="owner.username")

    class Meta:
        model = StockWatchlist
        fields = ("id", "name", "description", "owner")


class StockPositionSnapshotSerializer(Serializer):
    """Serializer of the stock position snapshot payload."""

    # pylint: disable=abstract-method

    ticker = ReadOnlyField(source="stock.ticker")
    name = ReadOnlyField(source="stock.name")
    sector = ReadOnlyField(source="stock.sector")
    price = FloatField()
    shares = IntegerField()
    dividend = FloatField()
    purchase_price = FloatField()
    first_purchase_date = DateField()
    latest_purchase_date = DateField()

    size = FloatField()
    size_at_cost = FloatField()
    dividend_yield = FloatField()
    dividend_yield_on_cost = FloatField()
    dividend_income = FloatField()
    pnl_percentage = FloatField()
    pnl = FloatField()


class StockPortfolioSnapshotSerializer(Serializer):
    """Serializer of the stock portfolio snapshot payload."""

    # pylint: disable=abstract-method

    positions = DictField(child=StockPositionSnapshotSerializer())
    sector_distribution = DictField(child=FloatField())
    size_distribution = DictField(child=FloatField())
    size_at_cost_distribution = DictField(child=FloatField())
    dividend_distribution = DictField(child=FloatField())
    annualized_pnls = DictField(child=FloatField())

    assets_under_management = FloatField()
    capital_invested = FloatField()
    dividend = FloatField()
    dividend_yield = FloatField()
    number_of_positions = IntegerField()

    owner = ReadOnlyField(source="owner.username")


class TargetPriceSerializer(Serializer):
    """Serializer of the target price payload."""

    # pylint: disable=abstract-method

    id = IntegerField(read_only=True)

    name = CharField()
    price = FloatField()


class PositionSizeSerializer(Serializer):
    """Serializer of the position size payload."""

    # pylint: disable=abstract-method

    id = IntegerField(read_only=True)

    name = CharField()
    size = FloatField()
    at_cost = BooleanField(required=False)


class StockWatchlistItemSerializer(Serializer):
    """Serializer of the stock watchlist item payload."""

    # pylint: disable=abstract-method

    ticker = CharField(read_only=True)

    target_prices = TargetPriceSerializer(many=True)
    position_sizes = PositionSizeSerializer(many=True)


class StockWatchlistDetailsSerializer(Serializer):
    """Serializer of the watchlist details tree payload."""

    # pylint: disable=abstract-method

    id = IntegerField()
    name = CharField()
    description = CharField(required=False)
    items = StockWatchlistItemSerializer(many=True)
