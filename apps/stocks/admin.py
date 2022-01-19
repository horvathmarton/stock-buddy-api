"""Definition of the admin surface for the stocks module."""

from django.contrib import admin

from .models import Stock


class StockAdmin(admin.ModelAdmin):
    """Admin config for the stock resource."""

    list_display = ("ticker", "name", "sector", "active", "created_at", "updated_at")
    list_filter = ["sector", "active"]
    search_fields = ["name"]


admin.site.register(Stock, StockAdmin)
