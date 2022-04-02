"""Business logic for the cash module."""

from datetime import date
from logging import getLogger

from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from lib.permissions import IsOwnerOrAdmin
from lib.services.cash import CashService
from lib.helpers import parse_date_query_param

from apps.cash.serializers import CashBalanceSerializer
from apps.stocks.models import StockPortfolio

LOGGER = getLogger(__name__)


class CashBalanceDetailsView(APIView):
    """Business logic for the cash details API."""

    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def __init__(self, *args, **kwargs):
        self.cash_service = CashService()
        super().__init__(*args, **kwargs)

    def get(self, request: Request, pk: int) -> Response:
        """
        Returns the cash balance of a given portfolio.
        """

        # pylint: disable=invalid-name

        LOGGER.debug("Parsing as_of parameter from the request.")
        as_of = parse_date_query_param(request, "as_of")

        LOGGER.info(
            "The user %s has requested %s portfolio's cash balance as of %s.",
            request.user,
            pk,
            as_of,
        )

        LOGGER.debug("Looking for %s portfolio.", pk)
        portfolio = get_object_or_404(StockPortfolio, pk=pk, owner=request.user)

        balance = self.cash_service.get_portfolio_cash_balance(
            [portfolio], snapshot_date=as_of or date.today()
        )

        LOGGER.debug("Validating output for cash balance snapshot.")
        serializer = CashBalanceSerializer(balance)

        return Response(serializer.data)


class CashBalanceSummaryView(APIView):
    """Business logic for the cash summary API."""

    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def __init__(self, *args, **kwargs):
        self.cash_service = CashService()
        super().__init__(*args, **kwargs)

    def get(self, request: Request) -> Response:
        """
        Returns a summary of cash balance for all of the portfolios owned by the user.
        """

        LOGGER.debug("Parsing as_of parameter from the request.")
        as_of = parse_date_query_param(request, "as_of")

        LOGGER.info(
            "The user %s has requested a cash balance summary as of %s.",
            request.user,
            as_of,
        )

        LOGGER.debug("Looking up portfolios belonging to %s.", request.user)
        portfolios = get_list_or_404(StockPortfolio, owner=request.user)
        balance = self.cash_service.get_portfolio_cash_balance(
            portfolios, snapshot_date=as_of or date.today()
        )

        LOGGER.debug("Validating output for cash balance snapshot.")
        serializer = CashBalanceSerializer(balance)

        return Response(serializer.data)
