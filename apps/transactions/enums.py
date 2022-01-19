"""Enums related to the stock module."""

from django.db import models


class Currency(models.TextChoices):
    """Supported currencies in the application."""

    HUNGARIAN_FORINT = "HUF"
    US_DOLLAR = "USD"
    EURO = "EUR"
