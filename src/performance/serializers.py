"""Serializers for the performance payloads."""

from rest_framework.serializers import Serializer, DateField, FloatField


class PerformanceSnapshotSerializer(Serializer):
    """Serializer of a portfolio or position performance at a given time."""

    # pylint: disable=abstract-method

    date = DateField()
    base_size = FloatField()
    appreciation = FloatField()
    dividends = FloatField()
    cash_flow = FloatField()

    pnl = FloatField()
    capital_size = FloatField()
    total = FloatField()
    performance = FloatField()
