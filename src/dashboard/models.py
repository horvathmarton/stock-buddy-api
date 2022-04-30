"""Models related to the dashboard schema."""

from django.contrib.auth.models import User
from django.db.models import (
    CASCADE,
    RESTRICT,
    CharField,
    DateTimeField,
    FloatField,
    ForeignKey,
    Model,
    TextField,
)

from ..lib.enums import AssetType, Visibility


class Strategy(Model):
    """Represents global asset allocation plan defined by a user."""

    name: TextField = TextField()
    visibility: CharField = CharField(
        max_length=7, choices=Visibility.choices, default=Visibility.PRIVATE
    )

    owner: ForeignKey = ForeignKey(User, RESTRICT)
    created_at: DateTimeField = DateTimeField(auto_now_add=True)
    updated_at: DateTimeField = DateTimeField(auto_now=True)

    class Meta:
        db_table = '"dashboard"."strategy"'

    def __str__(self):
        return self.name


class StrategyItem(Model):
    """Represents an asset type in a user defined strategy."""

    name: CharField = CharField(max_length=11, choices=AssetType.choices)
    size: FloatField = FloatField()

    strategy: ForeignKey = ForeignKey(Strategy, CASCADE)
    created_at: DateTimeField = DateTimeField(auto_now_add=True)
    updated_at: DateTimeField = DateTimeField(auto_now=True)

    class Meta:
        db_table = '"dashboard"."strategy_item"'

    def __str__(self):
        return self.name


class UserStrategy(Model):
    """A one-to-one join table between the user and its selected target strategy."""

    user: ForeignKey = ForeignKey(User, RESTRICT, unique=True)
    strategy: ForeignKey = ForeignKey(Strategy, RESTRICT)

    class Meta:
        db_table = '"dashboard"."user_strategy"'
