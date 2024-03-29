"""Define the URL schemes for the transactions route."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CashTransactionViewSet,
    ForexTransactionViewSet,
    StockTransactionViewSet,
)

router = DefaultRouter(trailing_slash=False)
router.register(r"cash", CashTransactionViewSet)
router.register(r"forex", ForexTransactionViewSet)
router.register(r"stocks", StockTransactionViewSet)


urlpatterns = [
    path("", include(router.urls)),
]
