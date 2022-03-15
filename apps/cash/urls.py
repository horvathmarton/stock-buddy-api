"""Define the URL schemes for the cash route."""

from django.urls import path, include

from rest_framework.routers import DefaultRouter
from apps.cash.views import CashBalanceViewSet

router = DefaultRouter()
router.register(r"", CashBalanceViewSet)

urlpatterns = [path("", include(router.urls))]
