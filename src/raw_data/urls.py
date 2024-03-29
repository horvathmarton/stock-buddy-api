"""Define the URL schemes for the raw data route."""

from django.urls import path

from .views import (
    StockDividendStatsView,
    StockDividendView,
    StockPriceStatsView,
    StockPriceView,
    StockSplitStatsView,
    StockSplitView,
)

urlpatterns = [
    path("stocks/stock-prices", StockPriceStatsView.as_view()),
    path("stocks/<slug:ticker>/stock-prices", StockPriceView.as_view()),
    path("stocks/stock-dividends", StockDividendStatsView.as_view()),
    path("stocks/<slug:ticker>/stock-dividends", StockDividendView.as_view()),
    path("stocks/stock-splits", StockSplitStatsView.as_view()),
    path("stocks/<slug:ticker>/stock-splits", StockSplitView.as_view()),
]
