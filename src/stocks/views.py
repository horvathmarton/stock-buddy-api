from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from src.lib.permissions import IsOwnerOrAdmin
from src.lib.services.finance import FinanceService

from .models import Stock, StockPortfolio, StockWatchlist
from .serializers import (
    StockPortfolioSerializer,
    StockPositionSerializer,
    StockSerializer,
    StockWatchlistSerializer,
)


class StockViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stock.objects.all().filter(active=True)
    serializer_class = StockSerializer


class StockPortfolioViewSet(viewsets.ModelViewSet):
    queryset = StockPortfolio.objects.all()
    serializer_class = StockPortfolioSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.finance_service = FinanceService()

    def retrieve(self, request: Request, pk: int = None) -> Response:
        portfolio = get_object_or_404(StockPortfolio, pk=pk)
        positions = self.finance_service.get_portfolio_snapshot([portfolio])

        serializer = StockPositionSerializer(positions, many=True)

        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def summary(self, request: Request) -> Response:
        """
        Returns a summary for every postion owned by the user.
        """

        portfolios = get_list_or_404(StockPortfolio, owner=request.user)
        positions = self.finance_service.get_portfolio_snapshot(portfolios)

        serializer = StockPositionSerializer(positions, many=True)

        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def filter_queryset(self, queryset):
        is_admin = self.request.user.groups.filter(name="Admins").exists()

        if is_admin:
            return queryset

        return queryset.filter(owner=self.request.user)


class StockWatchlistViewSet(viewsets.ModelViewSet):
    queryset = StockWatchlist.objects.all()
    serializer_class = StockWatchlistSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def filter_queryset(self, queryset):
        is_admin = self.request.user.groups.filter(name="Admins").exists()

        if is_admin:
            return queryset

        return queryset.filter(owner=self.request.user)
