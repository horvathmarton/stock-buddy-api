"""Business logic for the transactions module."""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from lib.permissions import IsOwnerOrAdmin

from .models import CashTransaction, ForexTransaction, StockTransaction
from .serializers import (
    CashTransactionSerializer,
    ForexTransactionSerializer,
    StockTransactionSerializer,
)


class CashTransactionViewSet(viewsets.ModelViewSet):
    """Business logic for the cash transaction API."""

    queryset = CashTransaction.objects.all()
    serializer_class = CashTransactionSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def filter_queryset(self, queryset):
        is_admin = self.request.user.groups.filter(name="Admins").exists()

        if is_admin:
            return queryset

        return queryset.filter(owner=self.request.user)


class ForexTransactionViewSet(viewsets.ModelViewSet):
    """Business logic for the forex transaction API."""

    queryset = ForexTransaction.objects.all()
    serializer_class = ForexTransactionSerializer
    permission_classes = [IsOwnerOrAdmin]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def filter_queryset(self, queryset):
        if self.request.user.groups.filter(name="Admins").exists():
            return queryset

        return queryset.filter(owner=self.request.user)


class StockTransactionViewSet(viewsets.ModelViewSet):
    """Business logic for the stock transaction API."""

    queryset = StockTransaction.objects.all()
    serializer_class = StockTransactionSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def filter_queryset(self, queryset):
        is_admin = self.request.user.groups.filter(name="Admins").exists()

        if is_admin:
            return queryset

        return queryset.filter(owner=self.request.user)
