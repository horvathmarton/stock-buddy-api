from datetime import date

from dateutil import parser
from dateutil.parser._parser import ParserError
from django.shortcuts import get_list_or_404, get_object_or_404
from lib.permissions import IsOwnerOrAdmin
from lib.services.finance import FinanceService
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .models import Stock, StockPortfolio, StockWatchlist
from .serializers import (
    StockPortfolioSerializer,
    StockPortfolioSnapshotSerializer,
    StockSerializer,
    StockWatchlistSerializer,
)


class StockViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stock.objects.all().filter(active=True)
    serializer_class = StockSerializer


class StockPortfolioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StockPortfolio.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.finance_service = FinanceService()

    def retrieve(self, request: Request, pk: int = None, *args, **kwargs) -> Response:
        asOf = request.query_params.get("asOf")
        if asOf:
            try:
                asOf = parser.parse(asOf)
            except ParserError:
                return Response(
                    {"error": "Invalid date in asOf query param"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        portfolio = get_object_or_404(StockPortfolio, pk=pk)

        portfolio = self.finance_service.get_portfolio_snapshot(
            [portfolio], snapshot_date=asOf or date.today()
        )
        serializer = StockPortfolioSnapshotSerializer(portfolio)

        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def summary(self, request: Request) -> Response:
        """
        Returns a summary for every postion owned by the user.
        """
        asOf = request.query_params.get("asOf")
        if asOf:
            try:
                asOf = parser.parse(asOf)
            except ParserError:
                return Response(
                    {"error": "Invalid date in asOf query param"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        portfolios = get_list_or_404(StockPortfolio, owner=request.user)
        portfolio = self.finance_service.get_portfolio_snapshot(
            portfolios, snapshot_date=asOf or date.today()
        )

        serializer = StockPortfolioSnapshotSerializer(portfolio)

        return Response(serializer.data)

    def perform_create(self, serializer):
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
