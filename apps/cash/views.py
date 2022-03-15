"""Business logic for the cash module."""

from datetime import date
from logging import getLogger

import dateutil
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from lib.permissions import IsOwnerOrAdmin
from lib.services.cash import CashService

from apps.cash.serializers import CashBalanceSerializer
from apps.stocks.models import Stock, StockPortfolio

LOGGER = getLogger(__name__)


class CashBalanceViewSet(viewsets.GenericViewSet):
    """Business logic for the cash API."""

    queryset = Stock.objects.filter(active=True)
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def __init__(self, *args, **kwargs):
        self.cash_service = CashService()
        super().__init__(*args, **kwargs)

    def retrieve(self, request: Request, pk: int) -> Response:
        """
        Returns the cash balance of a given portfolio.
        """

        # pylint: disable=arguments-differ, disable=invalid-name

        LOGGER.debug("Parsing as_of parameter from the request.")
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

        LOGGER.info(
            "The user %s has requested %s portfolio's cash balance as of %s.",
            request.user,
            pk,
            parsed_as_of,
        )

        LOGGER.debug("Looking for %s portfolio.", pk)
        portfolio = get_object_or_404(StockPortfolio, pk=pk, owner=request.user)

        balance = self.cash_service.get_portfolio_cash_balance(
            [portfolio], snapshot_date=parsed_as_of or date.today()
        )

        LOGGER.debug("Validating output for cash balance snapshot.")
        serializer = CashBalanceSerializer(balance)

        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def summary(self, request: Request) -> Response:
        """
        Returns a summary of cash balance for all of the portfolios owned by the user.
        """

        LOGGER.debug("Parsing as_of parameter from the request.")
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

        LOGGER.info(
            "The user %s has requested a cash balance summary as of %s.",
            request.user,
            parsed_as_of,
        )

        LOGGER.debug("Looking up portfolios belonging to %s.", request.user)
        portfolios = get_list_or_404(StockPortfolio, owner=request.user)
        balance = self.cash_service.get_portfolio_cash_balance(
            portfolios, snapshot_date=parsed_as_of or date.today()
        )

        LOGGER.debug("Validating output for cash balance snapshot.")
        serializer = CashBalanceSerializer(balance)

        return Response(serializer.data)
