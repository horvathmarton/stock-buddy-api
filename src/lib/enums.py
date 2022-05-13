"""Shared enums used in multiple modules."""

from enum import Enum
from django.db import models


class SyncStatus(models.TextChoices):
    """Enum indicating the status of a sync operation."""

    STARTED = "started"
    FINISHED = "finished"
    FAILED = "failed"
    ABORTED = "aborted"


class Visibility(models.TextChoices):
    """Enum indicating the visibility level of a resource."""

    PUBLIC = "public"
    PRIVATE = "private"


class AssetType(models.TextChoices):
    """Enum for the supported asset types by the app."""

    STOCK = "stock"
    BOND = "bond"
    REAL_ESTATE = "real-estate"
    CRYPTO = "crypto"
    GOLD = "gold"
    COMMODITY = "commodity"
    CASH = "cash"


class Resolution(Enum):
    """Enum for time resolutions supported by the app."""

    DAY = 1
    WEEK = 7
    MONTH = 30
    QUARTER = 90
    YEAR = 365
