"""Configurations for the app."""

from django.apps import AppConfig


class StocksConfig(AppConfig):
    """Config class for the app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.stocks"
