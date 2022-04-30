"""Serializers for the transaction payloads."""

from rest_framework import serializers

from .models import CashTransaction, ForexTransaction, StockTransaction


class CashTransactionSerializer(serializers.ModelSerializer):
    """Serializer of the cash transaction model."""

    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = CashTransaction
        fields = ("currency", "amount", "date", "owner", "portfolio")


class ForexTransactionSerializer(serializers.ModelSerializer):
    """Serializer of the forex transaction model."""

    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = ForexTransaction
        fields = (
            "date",
            "amount",
            "ratio",
            "source_currency",
            "target_currency",
            "owner",
            "portfolio",
        )


class StockTransactionSerializer(serializers.ModelSerializer):
    """Serializer of the stock transaction model."""

    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = StockTransaction
        fields = ("ticker", "amount", "price", "date", "comment", "owner", "portfolio")
