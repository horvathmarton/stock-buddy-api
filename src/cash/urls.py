"""Define the URL schemes for the cash route."""

from django.urls import path

from .views import CashBalanceDetailsView, CashBalanceSummaryView

urlpatterns = [
    path("<int:pk>", CashBalanceDetailsView.as_view()),
    path("summary", CashBalanceSummaryView.as_view()),
]
