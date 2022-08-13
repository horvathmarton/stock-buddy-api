"""Define the URL schemes for the performance route."""

from django.urls import path

from .views import (
    PositionPerformanceView,
    PortfolioPerformanceView,
    PortfolioSummaryPerformanceView,
)

urlpatterns = [
    path("portfolios/<int:pk>/<slug:ticker>", PositionPerformanceView.as_view()),
    path("portfolios/<int:pk>", PortfolioPerformanceView.as_view()),
    path("portfolios/summary", PortfolioSummaryPerformanceView.as_view()),
]
