"""Serializers for the cash payloads."""

from rest_framework import serializers


class CashBalanceSerializer(serializers.Serializer):
    """Serializer of the cash balance snapshot payload."""

    # pylint: disable=abstract-method

    usd = serializers.FloatField(source="USD")
    huf = serializers.FloatField(source="HUF")
    eur = serializers.FloatField(source="EUR")
