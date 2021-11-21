from django.urls import path
from django.urls.resolvers import URLPattern

from .views import CashTransactionsView

urlpatterns = [
    path('cash-transaction', CashTransactionsView.as_view())
]
