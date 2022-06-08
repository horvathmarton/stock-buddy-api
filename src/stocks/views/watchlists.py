"""Watchlists related handlers in the stocks module."""

from logging import getLogger
from typing import cast

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from ...lib.permissions import IsOwnerOrAdmin
from ...lib.protocols import Identifiable
from ...lib.queries import fetch_watchlist_tree
from ..dataclasses import WatchlistRow
from ..helpers import parse_watchlist_rows
from ..models import (
    PositionSize,
    Stock,
    StockWatchlist,
    StockWatchlistItem,
    TargetPrice,
)
from ..serializers import (
    StockWatchlistDetailsSerializer,
    StockWatchlistItemSerializer,
    StockWatchlistSerializer,
)

LOGGER = getLogger(__name__)


class StockWatchlistViewSet(ModelViewSet):
    """Business logic for the stock watchlist API."""

    queryset = StockWatchlist.objects.all()
    serializer_class = StockWatchlistSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def perform_create(self, serializer):
        LOGGER.debug("Inserting a new stock portfolio for %s.", self.request.user)
        serializer.save(owner=self.request.user)

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        watchlist = self.get_object()
        cursor = fetch_watchlist_tree(watchlist.id)
        rows = [
            WatchlistRow(
                watchlist_id=i[0],
                stock_id=i[1],
                item_type=i[2],
                watchlist_name=i[3],
                watchlist_description=i[4],
                target_id=i[5],
                target_name=i[6],
                price=i[7],
                size=i[8],
                at_cost=i[9],
            )
            for i in cursor
        ]
        parsed = parse_watchlist_rows(rows)[0]

        return Response(StockWatchlistDetailsSerializer(parsed).data)

    def filter_queryset(self, queryset):
        return queryset.filter(owner=self.request.user)


class StockWatchlistManagementView(APIView):
    """Business logic to add and remove items to a stock watchlist."""

    # pylint: disable=invalid-name

    def post(self, request: Request, pk: int, ticker: str) -> Response:
        """Adds a new monitored stock to a watchlist if not already on the list."""

        LOGGER.info("Adding %s to watchlist %s.", ticker, pk)

        LOGGER.debug("Looking up watchlist and stock.")
        watchlist = get_object_or_404(StockWatchlist, pk=pk)
        stock = get_object_or_404(Stock, ticker=ticker)

        if not watchlist.owner == request.user:
            raise PermissionDenied("User is not owner of the watchlist.")

        LOGGER.debug("Trying to add the new ticker to the watchlist.")
        StockWatchlistItem.objects.get_or_create(watchlist=watchlist, stock=stock)

        LOGGER.debug("Looking up each ticker on the current watchlist.")
        stocks = [
            item.stock.ticker
            for item in StockWatchlistItem.objects.filter(watchlist=watchlist)
        ]

        return Response(
            {
                "id": cast(Identifiable, watchlist).id,
                "name": watchlist.name,
                "stocks": stocks,
            }
        )

    def put(self, request: Request, pk: int, ticker: str) -> Response:
        """Updates an existing item on the watchlist with new targets."""

        LOGGER.info("Updating %s on watchlist %s.", ticker, pk)

        serializer = StockWatchlistItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        LOGGER.debug("Looking up watchlist and stock.")
        watchlist = get_object_or_404(StockWatchlist, pk=pk)
        stock = get_object_or_404(Stock, ticker=ticker)

        if not watchlist.owner == request.user:
            raise PermissionDenied("User is not owner of the watchlist.")

        try:
            LOGGER.debug("Looking up the stock on the watchlist.")
            item: StockWatchlistItem = StockWatchlistItem.objects.get(
                watchlist=watchlist, stock=stock
            )
        except StockWatchlistItem.DoesNotExist as error:
            raise NotFound("Stock is not on the watchlist.") from error

        LOGGER.debug("Updating targets in bulk.")
        with transaction.atomic():
            TargetPrice.objects.filter(watchlist_item=item).delete()
            PositionSize.objects.filter(watchlist_item=item).delete()

            TargetPrice.objects.bulk_create(
                [
                    TargetPrice(**target, watchlist_item=item)
                    for target in serializer.validated_data.get("target_prices")
                ]
            )
            PositionSize.objects.bulk_create(
                [
                    PositionSize(**target, watchlist_item=item)
                    for target in serializer.validated_data.get("position_sizes")
                ]
            )

        return Response()

    def delete(self, request: Request, pk: int, ticker: str) -> Response:
        """Removes a monitored stock from a watchlist."""

        LOGGER.info("Removing %s from watchlist %s.", ticker, pk)

        LOGGER.debug("Looking up watchlist and stock.")
        watchlist = get_object_or_404(StockWatchlist, pk=pk)
        stock = get_object_or_404(Stock, ticker=ticker)

        if not watchlist.owner == request.user:
            raise PermissionDenied("User is not owner of the watchlist.")

        try:
            LOGGER.debug("Looking up the stock on the watchlist.")
            item: StockWatchlistItem = StockWatchlistItem.objects.get(
                watchlist=watchlist, stock=stock
            )
        except StockWatchlistItem.DoesNotExist as error:
            raise NotFound("Stock is not on the watchlist.") from error

        LOGGER.debug("Trying to remove the ticker from the watchlist.")
        item.delete()

        LOGGER.debug("Looking up each ticker on the current watchlist.")
        stocks = [
            item.stock.ticker
            for item in StockWatchlistItem.objects.filter(watchlist=watchlist)
        ]

        return Response(
            {
                "id": cast(Identifiable, watchlist).id,
                "name": watchlist.name,
                "stocks": stocks,
            }
        )
