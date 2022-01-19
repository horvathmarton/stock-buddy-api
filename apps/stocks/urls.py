"""Define the URL schemes for the stocks route."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import StockPortfolioViewSet, StockViewSet, StockWatchlistViewSet

router = DefaultRouter()
router.register(r"portfolios", StockPortfolioViewSet)
router.register(r"watchlists", StockWatchlistViewSet)
router.register(r"", StockViewSet)

urlpatterns = [path("", include(router.urls))]
