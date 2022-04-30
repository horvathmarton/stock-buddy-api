"""Business logic for the raw data module."""

import json
from logging import getLogger
from re import findall

from dateutil import parser
from django.db.models import Avg, Count, Max, Min
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..lib.decorators import allow_content_types
from ..lib.enums import SyncStatus
from ..lib.permissions import IsBot
from ..stocks.models import Stock
from .models import (
    StockDividend,
    StockDividendSync,
    StockPrice,
    StockPriceSync,
    StockSplit,
    StockSplitSync,
)
from .serializers import (
    StockDividendSerializer,
    StockPriceSerializer,
    StockSplitSerializer,
)

LOGGER = getLogger(__name__)


class StockPriceView(APIView):
    """Business logic for the stock price API."""

    permission_classes = [IsAuthenticated, IsBot]

    @allow_content_types(("application/json",))
    def post(self, request: Request, ticker: str) -> Response:
        """Sync price timeseries for a given stock."""

        LOGGER.info(
            "Syncing price information for %s initiated by %s.", ticker, request.user
        )

        LOGGER.debug("Looking up stock with ticker %s.", ticker)
        stock = get_object_or_404(Stock, ticker=ticker)
        LOGGER.debug(
            "Starting a new price sync for %s owned by %s.", ticker, request.user
        )
        sync = StockPriceSync(owner=request.user)
        sync.save()

        try:
            prices = json.loads(request.body)["data"]
            LOGGER.debug("Looking up price values for %s from the latest sync.", ticker)
            latest_saved = (
                StockPrice.objects.all()
                .filter(ticker=stock)
                .aggregate(Max("date"))["date__max"]
            )
            prices = [
                price
                for price in prices
                if not latest_saved or parser.parse(price["date"]).date() > latest_saved
            ]

            LOGGER.debug("Validating price data parsed from JSON.")
            serializer = StockPriceSerializer(data=prices, many=True)
            if not serializer.is_valid():
                LOGGER.warning("The price data from JSON was invalid.")
                sync.status = SyncStatus.FAILED
                sync.save()

                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            LOGGER.debug("Saving price data for %s as part of sync %s.", stock, sync)
            serializer.save(ticker=stock, sync=sync)
        except Exception as error:
            LOGGER.exception(error)
            LOGGER.error("An error happened during price sync.")

            sync.status = SyncStatus.FAILED
            sync.save()

            raise
        else:
            LOGGER.debug("Synced price information successfully.")
            sync.status = SyncStatus.FINISHED
            sync.save()

            return Response(None, status=status.HTTP_201_CREATED)


class StockPriceStatsView(APIView):
    """Business logic for the stock price statistics API."""

    def get(self, request: Request) -> Response:
        """Collect statistical information for the stock prices in the app."""

        LOGGER.info("Fetching stock price statistics.")

        stats = (
            StockPrice.objects.all()
            .values("ticker")
            .annotate(
                count=Count("ticker"),
                min=Min("value"),
                avg=Avg("value"),
                max=Max("value"),
            )
            .order_by("count")
        )

        return Response(stats)


class StockDividendView(APIView):
    """Business logic for the stock dividend API."""

    permission_classes = [IsAuthenticated, IsBot]

    @allow_content_types(("application/json",))
    def post(self, request: Request, ticker: str) -> Response:
        """Sync dividend timeseries for a given stock."""

        LOGGER.info(
            "Syncing dividend information for %s initiated by %s.", ticker, request.user
        )

        LOGGER.debug("Looking up stock with ticker %s.", ticker)
        stock = get_object_or_404(Stock, ticker=ticker)
        LOGGER.debug(
            "Starting a new dividend sync for %s owned by %s.", ticker, request.user
        )
        sync = StockDividendSync(owner=request.user)
        sync.save()

        try:
            dividends = json.loads(request.body)["data"]
            LOGGER.debug(
                "Looking up dividend values for %s from the latest sync.", ticker
            )
            latest_saved = (
                StockDividend.objects.all()
                .filter(ticker=stock)
                .aggregate(Max("payout_date"))["payout_date__max"]
            )
            dividends = [
                dividend
                for dividend in dividends
                if not latest_saved
                or parser.parse(dividend["payout_date"]).date() > latest_saved
            ]

            LOGGER.debug("Validating dividend data parsed from the JSON.")
            serializer = StockDividendSerializer(data=dividends, many=True)
            if not serializer.is_valid():
                sync.status = SyncStatus.FAILED
                sync.save()

                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            LOGGER.debug("Saving dividend data for %s as part of sync %s.", stock, sync)
            serializer.save(ticker=stock, sync=sync)
        except Exception as error:
            LOGGER.exception(error)
            LOGGER.error("An error happened during dividend sync.")

            sync.status = SyncStatus.FAILED
            sync.save()

            raise
        else:
            LOGGER.debug("Synced dividend information successfully.")
            sync.status = SyncStatus.FINISHED
            sync.save()

            return Response(None, status=status.HTTP_201_CREATED)


class StockDividendStatsView(APIView):
    """Business logic for the stock dividend statistics API."""

    def get(self, request: Request) -> Response:
        """Collect statistical information for the stock dividends in the app."""

        LOGGER.info("Fetching stock dividend statistics.")

        stats = (
            StockDividend.objects.all()
            .values("ticker")
            .annotate(
                count=Count("ticker"),
                min=Min("amount"),
                avg=Avg("amount"),
                max=Max("amount"),
            )
            .order_by("count")
        )

        return Response(stats)


class StockSplitView(APIView):
    """Business logic for the stock split API."""

    permission_classes = [IsAuthenticated, IsBot]

    @allow_content_types(("application/json",))
    def post(self, request: Request, ticker: str) -> Response:
        """Sync split timeseries for a given stock."""

        LOGGER.info(
            "Syncing split information for %s initiated by %s.", ticker, request.user
        )

        LOGGER.debug("Looking up stock with ticker %s.", ticker)
        stock = get_object_or_404(Stock, ticker=ticker)
        LOGGER.debug(
            "Starting a new split sync for %s owned by %s.", ticker, request.user
        )
        sync = StockSplitSync(owner=request.user)
        sync.save()

        try:
            splits = json.loads(request.body)["data"]
            LOGGER.debug("Looking up split values for %s from the latest sync.", ticker)
            latest_saved = (
                StockSplit.objects.all()
                .filter(ticker=stock)
                .aggregate(Max("date"))["date__max"]
            )

            LOGGER.debug("Formatting split values before inserting for %s.", ticker)
            formatted_splits = []
            for split in splits:
                if latest_saved and parser.parse(split["date"]).date() <= latest_saved:
                    continue

                ratio = findall(r"(\d+):(\d+)", split["ratio"])

                if len(ratio) == 0:
                    sync.status = SyncStatus.FAILED
                    sync.save()

                    return Response(f"Couldn't parse ratio {ratio}.")

                dividend, divisor = ratio[0]
                formatted_splits.append(
                    {**split, "ratio": float(dividend) / float(divisor)}
                )

            LOGGER.debug("Validating split data parsed from the JSON.")
            serializer = StockSplitSerializer(data=formatted_splits, many=True)
            if not serializer.is_valid():
                sync.status = SyncStatus.FAILED
                sync.save()

                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            LOGGER.debug("Saving split data for %s as part of sync %s.", stock, sync)
            serializer.save(ticker=stock, sync=sync)
        except Exception as error:
            LOGGER.exception(error)
            LOGGER.error("An error happened during split sync.")

            sync.status = SyncStatus.FAILED
            sync.save()

            raise
        else:
            LOGGER.debug("Synced dividend information successfully.")
            sync.status = SyncStatus.FINISHED
            sync.save()

            return Response(None, status=status.HTTP_201_CREATED)


class StockSplitStatsView(APIView):
    """Business logic for the stock split statistics API."""

    def get(self, request: Request) -> Response:
        """Collect statistical information for the stock splits in the app."""

        LOGGER.info("Fetching stock split statistics.")

        stats = (
            StockSplit.objects.all()
            .values("ticker")
            .annotate(count=Count("ticker"))
            .order_by("count")
        )

        return Response(stats)
