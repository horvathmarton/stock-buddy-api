"""Define the URL schemes for the dashboard route."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PortfolioIndicatorView, SelectStrategyView, StrategyView

router = DefaultRouter(trailing_slash=False)
router.register(r"strategies", StrategyView)

urlpatterns = [
    path("portfolio-indicators", PortfolioIndicatorView.as_view()),
    path("strategies/select-strategy", SelectStrategyView.as_view()),
    path("", include(router.urls)),
]
