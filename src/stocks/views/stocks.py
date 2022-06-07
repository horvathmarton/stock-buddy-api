"""Stocks related handlers in the stocks module."""

from datetime import date
from logging import getLogger

from django.db import transaction
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from ...lib.helpers import parse_date_query_param
from ...lib.permissions import IsOwnerOrAdmin
from ...lib.services.stocks import get_portfolio_snapshot
from ...transactions.models import StockTransaction
from ..models import Stock, StockPortfolio
from ..serializers import (
    StockPortfolioSerializer,
    StockPortfolioSnapshotSerializer,
    StockSerializer,
)

LOGGER = getLogger(__name__)


class StockViewSet(ReadOnlyModelViewSet):
    """Business logic for the stock API."""

    queryset = Stock.objects.filter(active=True)
    serializer_class = StockSerializer


class StockPortfolioViewSet(ModelViewSet):
    """Business logic for the stock portfolio API."""

    queryset = StockPortfolio.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    serializer_class = StockPortfolioSerializer

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        # pylint: disable=invalid-name

        LOGGER.debug("Parsing as_of parameter from the request.")
        as_of = parse_date_query_param(request, "as_of")
        pk = kwargs["pk"]

        LOGGER.info(
            "The user %s has requested %s portfolio as of %s.",
            request.user,
            pk,
            as_of,
        )

        LOGGER.debug("Looking for %s portfolio.", pk)
        portfolio = get_object_or_404(StockPortfolio, pk=pk)

        if not IsOwnerOrAdmin().has_object_permission(request, self, portfolio):
            raise NotFound()

        snapshot = get_portfolio_snapshot([portfolio], as_of or date.today())
        if not snapshot.number_of_positions:
            raise NotFound(
                "The portfolio has no transaction data before the selected date."
            )

        LOGGER.debug("Validating output for %s stock portfolio snapshot.", pk)
        serializer = StockPortfolioSnapshotSerializer(snapshot)

        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def summary(self, request: Request) -> Response:
        """
        Returns a summary for every postion owned by the user.
        """

        LOGGER.debug("Parsing as_of parameter from the request.")
        as_of = parse_date_query_param(request, "as_of")

        LOGGER.info(
            "The user %s has requested a portfolio summary as of %s.",
            self.request.user,
            as_of,
        )

        LOGGER.debug("Looking up portfolios belonging to %s.", request.user)
        portfolios = get_list_or_404(StockPortfolio, owner=request.user)
        portfolio = get_portfolio_snapshot(portfolios, as_of or date.today())

        if not portfolio.number_of_positions:
            LOGGER.warning(
                "%s has no active postion to summarize as of %s.",
                request.user,
                as_of,
            )

            raise NotFound(
                "The portfolio has no transaction data before the selected date."
            )

        LOGGER.debug("Validating output for stock portfolio summary snapshot.")
        serializer = StockPortfolioSnapshotSerializer(portfolio)

        return Response(serializer.data)

    def perform_create(self, serializer):
        """We have to redefine the saving process to use the serializer."""

        LOGGER.debug("Inserting a new stock portfolio for %s.", self.request.user)
        serializer.save(owner=self.request.user)

    def perform_destroy(self, instance: StockPortfolio) -> None:
        with transaction.atomic():
            StockTransaction.objects.filter(portfolio=instance).delete()

            instance.delete()

    def filter_queryset(self, queryset):
        is_admin = self.request.user.groups.filter(name="Admins").exists()

        if is_admin:
            return queryset

        return queryset.filter(owner=self.request.user)
