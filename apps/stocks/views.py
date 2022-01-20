"""Business logic for the stocks module."""

from datetime import date

import dateutil
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from lib.permissions import IsOwnerOrAdmin
from lib.services.finance import FinanceService

from .models import Stock, StockPortfolio, StockWatchlist
from .serializers import (
    StockPortfolioSerializer,
    StockPortfolioSnapshotSerializer,
    StockSerializer,
    StockWatchlistSerializer,
)


class StockViewSet(viewsets.ReadOnlyModelViewSet):
    """Business logic for the stock API."""

    queryset = Stock.objects.all().filter(active=True)
    serializer_class = StockSerializer


class StockPortfolioViewSet(viewsets.ReadOnlyModelViewSet):
    """Business logic for the stock portfolio API."""

    queryset = StockPortfolio.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.finance_service = FinanceService()

    def retrieve(self, request: Request, *args, pk: int = None, **kwargs) -> Response:
        # pylint: disable=arguments-differ, disable=invalid-name
        as_of = request.query_params.get("asOf")
        parsed_as_of = None

        if as_of:
            try:
                parsed_as_of = dateutil.parser.parse(as_of)
            except dateutil.parser.ParserError:
                return Response(
                    {"error": "Invalid date in asOf query param"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        portfolio = get_object_or_404(StockPortfolio, pk=pk)

        portfolio = self.finance_service.get_portfolio_snapshot(
            [portfolio], snapshot_date=parsed_as_of or date.today()
        )
        serializer = StockPortfolioSnapshotSerializer(portfolio)

        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def summary(self, request: Request) -> Response:
        """
        Returns a summary for every postion owned by the user.
        """
        as_of = request.query_params.get("asOf")
        parsed_as_of = None

        if as_of:
            try:
                parsed_as_of = dateutil.parser.parse(as_of)
            except dateutil.parser.ParserError:
                return Response(
                    {"error": "Invalid date in asOf query param"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        portfolios = get_list_or_404(StockPortfolio, owner=request.user)
        portfolio = self.finance_service.get_portfolio_snapshot(
            portfolios, snapshot_date=parsed_as_of or date.today()
        )

        serializer = StockPortfolioSnapshotSerializer(portfolio)

        return Response(serializer.data)

    def perform_create(self, serializer):
        """We have to redefine the saving process to use the serializer."""

        serializer.save(owner=self.request.user)

    def filter_queryset(self, queryset):
        is_admin = self.request.user.groups.filter(name="Admins").exists()

        if is_admin:
            return queryset

        return queryset.filter(owner=self.request.user)

    def get_serializer_class(self):
        if self.action in ("retrieve", "summary"):
            return StockPortfolioSnapshotSerializer
        return StockPortfolioSerializer


class StockWatchlistViewSet(viewsets.ModelViewSet):
    """Business logic for the stock watchlist API."""

    queryset = StockWatchlist.objects.all()
    serializer_class = StockWatchlistSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def filter_queryset(self, queryset):
        if self.request.user.groups.filter(name="Admins").exists():
            return queryset

        return queryset.filter(owner=self.request.user)
