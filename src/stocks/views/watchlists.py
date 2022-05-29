"""Watchlists related handlers in the stocks module."""

from logging import getLogger
from typing import cast

from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from src.lib.protocols import Identifiable

from ...lib.permissions import IsOwnerOrAdmin
from ...lib.queries import fetch_watchlist_tree
from ..helpers import parse_watchlist_rows
from ..models import (
    PositionSize,
    Stock,
    StockWatchlist,
    StockWatchlistItem,
    TargetPrice,
)
from ..serializers import (
    PositionSizeSerializer,
    StockWatchlistSerializer,
    TargetPriceSerializer,
    StockWatchlistDetailsSerializer,
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
        parsed = parse_watchlist_rows(cursor)[0]

        return Response(StockWatchlistDetailsSerializer(parsed).data)

    def filter_queryset(self, queryset):
        if self.request.user.groups.filter(name="Admins").exists():
            return queryset

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


class TargetPriceView(APIView):
    """Business logic to add target prices to a watchlist item."""

    def post(self, request: Request, watchlist_id: int, ticker: str) -> Response:
        """Attach a new target price to a monitored stock."""

        LOGGER.info(
            "Adding a new target target price to %s on %s.", ticker, watchlist_id
        )

        serializer = TargetPriceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        LOGGER.debug("Looking up watchlist item.")
        watchlist_item = get_object_or_404(
            StockWatchlistItem, watchlist=watchlist_id, stock=ticker
        )

        LOGGER.debug("Creating the target price entity.")
        target_price = TargetPrice()

        target_price.price = serializer.validated_data["price"]
        target_price.watchlist_item = watchlist_item = watchlist_item
        target_price.description = serializer.validated_data.get("description")

        LOGGER.debug("Trying to insert the target price into the database.")
        target_price.save()

        return Response(TargetPriceSerializer(target_price).data, status=201)


class TargetPriceDetailsView(APIView):
    """Business logic to remove target prices from watchlist item."""

    # pylint: disable=invalid-name

    def delete(
        self, request: Request, watchlist_id: int, ticker: str, pk: int
    ) -> Response:
        """Removes a target price from a monitored stock."""

        LOGGER.info("Removing target target price from %s on %s.", ticker, watchlist_id)

        LOGGER.debug("Looking up watchlist item.")
        target_price = get_object_or_404(TargetPrice, pk=pk)
        watchlist_item = target_price.watchlist_item

        if watchlist_item.watchlist.owner != request.user:
            raise PermissionDenied(
                "The authenticated user is not the owner of the watchlist."
            )

        if (
            watchlist_item.watchlist.id != watchlist_id
            or watchlist_item.stock.ticker != ticker
        ):
            raise PermissionDenied(
                "Target price doesn't belong to this watchlist item."
            )

        LOGGER.debug("Trying to delete the target price from the database.")
        target_price.delete()

        return Response(status=204)


class PositionSizeView(APIView):
    """Business logic to add position size target to watchlist item."""

    def post(self, request: Request, watchlist_id: int, ticker: str) -> Response:
        """Attaches a new position size target to a monitored stock."""

        LOGGER.info(
            "Adding a new target position size to %s on %s.",
            ticker,
            watchlist_id,
        )

        serializer = PositionSizeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        LOGGER.debug("Looking up watchlist item.")
        watchlist_item = get_object_or_404(
            StockWatchlistItem, watchlist=watchlist_id, stock=ticker
        )

        LOGGER.debug("Creating the position size entity.")
        position_size = PositionSize()

        position_size.watchlist_item = watchlist_item
        position_size.size = serializer.validated_data["size"]
        position_size.at_cost = serializer.validated_data.get("at_cost")
        position_size.description = serializer.validated_data.get("description")

        LOGGER.debug("Trying to insert the position size into the database.")
        position_size.save()

        return Response(PositionSizeSerializer(position_size).data, status=201)


class PositionSizeDetailsView(APIView):
    """Business logic to remove position size target from watchlist item."""

    # pylint: disable=invalid-name

    def delete(
        self, request: Request, watchlist_id: int, ticker: str, pk: int
    ) -> Response:
        """Removes a position size target from a monitored stock."""

        LOGGER.info(
            "Removing target position size from %s on %s.", ticker, watchlist_id
        )

        LOGGER.debug("Looking up watchlist item.")
        position_size = get_object_or_404(PositionSize, pk=pk)
        watchlist_item = position_size.watchlist_item

        if watchlist_item.watchlist.owner != request.user:
            raise PermissionDenied(
                "The authenticated user is not the owner of the watchlist."
            )

        if (
            watchlist_item.watchlist.id != watchlist_id
            or watchlist_item.stock.ticker != ticker
        ):
            raise PermissionDenied(
                "Position size doesn't belong to this watchlist item."
            )

        LOGGER.debug("Trying to delete the position size from the database.")
        position_size.delete()

        return Response(status=204)
