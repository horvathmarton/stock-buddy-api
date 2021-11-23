from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CashTransactionViewSet,
    ForexTransactionViewSet,
    StockTransactionViewSet,
)

router = DefaultRouter()
router.register(r"cash", CashTransactionViewSet)
router.register(r"forex", ForexTransactionViewSet)
router.register(r"stocks", StockTransactionViewSet)


urlpatterns = [
    path("", include(router.urls)),
]
