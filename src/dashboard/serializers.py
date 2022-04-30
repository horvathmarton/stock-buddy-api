"""Serializers for the stocks payloads."""

from logging import getLogger

from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer, ReadOnlyField

from .models import Strategy, StrategyItem


LOGGER = getLogger(__name__)


class StrategyItemSerializer(ModelSerializer):
    """Serializer of the strategy item model."""

    class Meta:
        model = StrategyItem
        fields = ("name", "size")


class StrategySerializer(ModelSerializer):
    """Serializer of the strategy model."""

    owner = ReadOnlyField(source="owner.username")
    items = StrategyItemSerializer(source="strategyitem_set", many=True)

    def validate(self, attrs):
        """Custom check to make sure that the items contained by the strategy adds up to 100%."""

        LOGGER.debug("Validate strategy items if they add up to 100%.")
        items_sum = sum([item["size"] for item in attrs["strategyitem_set"]])
        if items_sum != 1:
            raise ValidationError("The sum of item sizes must be exactly 100%.")

        return super().validate(attrs)

    class Meta:
        model = Strategy
        fields = ("id", "name", "owner", "items")
        depth = 1
