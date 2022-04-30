"""Configurations for the app."""

from django.apps import AppConfig


class RawDataConfig(AppConfig):
    """Config class for the app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "src.raw_data"
