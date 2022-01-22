"""Serializers for the stocks payloads."""

from rest_framework.serializers import ModelSerializer, ReadOnlyField
from rest_framework.exceptions import ValidationError

from apps.dashboard.models import Strategy, StrategyItem
from lib.enums import Visibility


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

        items_sum = sum([item["size"] for item in attrs["strategyitem_set"]])
        if items_sum != 1:
            raise ValidationError("The sum of item sizes must be exactly 100%.")

        return super().validate(attrs)

    def create(self, validated_data) -> Strategy:
        items = validated_data.pop("strategyitem_set")
        # We only allow for the user to create private strategies for now to avoid spamming each other.
        # Public strategies will be added by administrators.
        strategy = Strategy.objects.create(
            **validated_data,
            owner=self.context["request"].user,
            visibility=Visibility.PRIVATE,
        )
        StrategyItem.objects.bulk_create(
            [StrategyItem(strategy=strategy, **item) for item in items]
        )

        return strategy

    def update(self, instance, validated_data) -> Strategy:
        items = validated_data.pop("strategyitem_set")

        # Remove the old strategy items.
        StrategyItem.objects.filter(strategy=instance).delete()

        StrategyItem.objects.bulk_create(
            [StrategyItem(strategy=instance, **item) for item in items]
        )

        return instance

    class Meta:
        model = Strategy
        fields = ("id", "name", "owner", "items")
        depth = 1
