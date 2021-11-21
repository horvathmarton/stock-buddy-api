from django.db import models


class Currency(models.TextChoices):
    HUNGARIAN_FORINT = 'HUF'
    US_DOLLAR = 'USD'
    EURO = 'EUR'
