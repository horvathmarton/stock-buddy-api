"""Define the URL schemes for the stocks route."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from src.stocks.views.watchlists import (
    PositionSizeDetailsView,
    PositionSizeView,
    TargetPriceDetailsView,
    TargetPriceView,
)

from .views import (
    StockPortfolioViewSet,
    StockViewSet,
    StockWatchlistManagementView,
    StockWatchlistViewSet,
)

router = DefaultRouter(trailing_slash=False)
router.register(r"portfolios", StockPortfolioViewSet)
router.register(r"watchlists", StockWatchlistViewSet)
router.register(r"", StockViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "watchlists/<int:pk>/stocks/<slug:ticker>",
        StockWatchlistManagementView.as_view(),
    ),
    path(
        "watchlists/<int:watchlist_id>/stocks/<slug:ticker>/target-prices",
        TargetPriceView.as_view(),
    ),
    path(
        "watchlists/<int:watchlist_id>/stocks/<slug:ticker>/target-prices/<int:pk>",
        TargetPriceDetailsView.as_view(),
    ),
    path(
        "watchlists/<int:watchlist_id>/stocks/<slug:ticker>/position-sizes",
        PositionSizeView.as_view(),
    ),
    path(
        "watchlists/<int:watchlist_id>/stocks/<slug:ticker>/position-sizes/<int:pk>",
        PositionSizeDetailsView.as_view(),
    ),
]
