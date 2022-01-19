"""Enums related to the stock module."""

from django.db import models


class Sector(models.TextChoices):
    """Supported stock sectors in the application."""

    SOFTWARE = ("Software",)
    HARDWARE = ("Hardware",)
    MEDIA = ("Media",)
    TELECOMMUNICATION = ("Telecommunication",)
    HEALTH_CARE_SERVICES = ("Health care services",)
    CONSUMER_SERVICES = ("Consumer services",)
    BUSINESS_SERVICES = ("Business services",)
    FINANCIAL_SERVICES = ("Financial services",)
    CONSUMER_GOODS = ("Consumer goods",)
    INDUSTRIAL_MATERIALS = ("Industrial materials",)
    ENERGY = ("Energy",)
    UTILITIES = ("Utilities",)
    REAL_ESTATE = ("Real estate",)
    ETF = ("ETF",)
