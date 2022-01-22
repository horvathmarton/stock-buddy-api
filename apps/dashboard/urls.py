"""Define the URL schemes for the dashboard route."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.dashboard.views import PortfolioIndicatorView, StrategyView

router = DefaultRouter()
router.register(r"strategies", StrategyView)

urlpatterns = [
    path("portfolio-indicators", PortfolioIndicatorView.as_view()),
    path("", include(router.urls)),
]
