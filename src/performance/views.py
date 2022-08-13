"""Business logic for the performance module."""

from logging import getLogger
from typing import cast

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..lib.helpers import get_range
from ..lib.services.date import get_resolution, get_timeseries
from ..lib.services.performance import (
    get_portfolio_performance,
    get_position_performance,
)
from ..lib.services.stocks import get_portfolio
from ..raw_data.models import StockDividend, StockPrice
from ..stocks.models import StockPortfolio
from ..transactions.models import CashTransaction, StockTransaction
from .serializers import PerformanceSnapshotSerializer

LOGGER = getLogger(__name__)


class PositionPerformanceView(APIView):
    """Business logic for the position performance API."""

    # pylint: disable=invalid-name

    def get(self, request: Request, pk: int, ticker: str) -> Response:
        """Timeseries of performance snapshot for a single position."""

        interval = get_range(request)
        series = get_timeseries(interval, get_resolution(interval))

        portfolio = get_object_or_404(StockPortfolio, pk=pk)
        stock_transactions = StockTransaction.objects.filter(portfolio=portfolio)
        portfolio_snapshots = get_portfolio(
            cast(list, stock_transactions),
            series,
            cast(User, request.user),
        )

        if not portfolio_snapshots:
            raise NotFound("Position was not present in this portfolio.")

        price_info = StockPrice.objects.filter(ticker=ticker)
        dividends = StockDividend.objects.filter(ticker=ticker)

        performance = get_position_performance(
            portfolio_snapshots=portfolio_snapshots,
            price_info=cast(list, price_info),
            dividends=cast(list, dividends),
            transactions=cast(list, stock_transactions),
            series=series,
        )

        serializer = PerformanceSnapshotSerializer(performance.values(), many=True)

        return Response({"results": serializer.data})


class PortfolioPerformanceView(APIView):
    """Business logic for the portfolio performance API."""

    # pylint: disable=invalid-name

    def get(self, request: Request, pk: int) -> Response:
        """Timeseries of performance snapshot for a portfolio."""

        interval = get_range(request)
        series = get_timeseries(interval, get_resolution(interval))

        portfolio = get_object_or_404(StockPortfolio, pk=pk)
        stock_transactions = StockTransaction.objects.filter(
            portfolio=portfolio,
            date__range=(interval.start_date, interval.end_date),
        )
        portfolio_snapshots = get_portfolio(
            cast(list, stock_transactions),
            series,
            cast(User, request.user),
        )
        dividends = StockDividend.objects.filter(
            ticker__in=portfolio_snapshots[series[-1]].positions.keys(),
            date__range=(interval.start_date, interval.end_date),
        )
        cash_transactions = CashTransaction.objects.filter(
            portfolio=portfolio,
            date__range=(interval.start_date, interval.end_date),
        )

        performance = get_portfolio_performance(
            portfolio_snapshots=portfolio_snapshots,
            dividends=cast(list, dividends),
            cash_transactions=cast(list, cash_transactions),
            series=series,
        )

        serializer = PerformanceSnapshotSerializer(performance.values(), many=True)

        return Response({"results": serializer.data})


class PortfolioSummaryPerformanceView(APIView):
    """Business logic for the portfolio summary performance API."""

    def get(self, request: Request) -> Response:
        """Timeseries of performance snapshot for all user owned portfolio."""

        return Response({"results": []})
