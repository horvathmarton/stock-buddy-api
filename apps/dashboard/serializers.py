"""Serializers for the stocks payloads."""

from logging import getLogger

from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer, ReadOnlyField
from lib.enums import Visibility

from apps.dashboard.models import Strategy, StrategyItem


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

    def create(self, validated_data) -> Strategy:
        items = validated_data.pop("strategyitem_set")
        owner = self.context["request"].user

        LOGGER.debug(
            "Inserting a new strategy named %s for %s.", validated_data["name"], owner
        )
        # We only allow for the user to create private strategies for now to avoid spamming each other.
        # Public strategies will be added by administrators.
        strategy = Strategy.objects.create(
            **validated_data,
            owner=owner,
            visibility=Visibility.PRIVATE,
        )

        LOGGER.debug(
            "Inserting %s strategy items for %s strategy.",
            len(items),
            strategy.name,
        )
        StrategyItem.objects.bulk_create(
            [StrategyItem(strategy=strategy, **item) for item in items]
        )

        return strategy

    def update(self, instance, validated_data) -> Strategy:
        items = validated_data.pop("strategyitem_set")

        # Remove the old strategy items.
        LOGGER.debug("Remove existing strategy items from %s.", instance.name)
        StrategyItem.objects.filter(strategy=instance).delete()

        LOGGER.debug(
            "Inserting %s new strategy items for %s strategy.",
            len(items),
            instance.name,
        )
        StrategyItem.objects.bulk_create(
            [StrategyItem(strategy=instance, **item) for item in items]
        )

        return instance

    class Meta:
        model = Strategy
        fields = ("id", "name", "owner", "items")
        depth = 1
