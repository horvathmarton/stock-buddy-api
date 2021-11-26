from re import findall

from dateutil import parser
from django.db.models import Avg, Count, Max, Min
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from lib.decorators import allow_content_types
from lib.enums import SyncStatus
from lib.permissions import IsBot
from lib.services.csv import CsvService
from apps.stocks.models import Stock

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


class StockPriceView(APIView):
    # TODO: Add logging.
    permission_classes = [IsAuthenticated, IsBot]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.csv_service = CsvService()

    @allow_content_types(("multipart/form-data",))
    def post(self, request: Request, ticker: str, format=None) -> Response:
        # TODO: Add consistency checks.
        # TODO: Add cross checks.

        stock = get_object_or_404(Stock, ticker=ticker)
        sync = StockPriceSync(owner=request.user)
        sync.save()

        try:
            prices = self.csv_service.parse(
                request.FILES["data"].file, {"Date": "date", "Close": "value"}
            )
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

            serializer = StockPriceSerializer(data=prices, many=True)
            if not serializer.is_valid():
                sync.status = SyncStatus.FAILED
                sync.save()

                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            serializer.save(ticker=stock, sync=sync)
        except Exception:
            sync.status = SyncStatus.FAILED
            sync.save()

            raise
        else:
            sync.status = SyncStatus.FINISHED
            sync.save()

            return Response(None, status=status.HTTP_201_CREATED)


class StockPriceStatsView(APIView):
    def get(self, request: Request, format=None) -> Response:
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
    permission_classes = [IsAuthenticated, IsBot]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.csv_service = CsvService()

    @allow_content_types(("multipart/form-data",))
    def post(self, request: Request, ticker: str, format=None) -> Response:
        # TODO: Add consistency checks.
        # TODO: Add cross checks.

        stock = get_object_or_404(Stock, ticker=ticker)
        sync = StockDividendSync(owner=request.user)
        sync.save()

        try:
            dividends = self.csv_service.parse(
                request.FILES["data"].file,
                {"Date": "payout_date", "Dividends": "amount"},
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

            serializer = StockDividendSerializer(data=dividends, many=True)
            if not serializer.is_valid():
                sync.status = SyncStatus.FAILED
                sync.save()

                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            serializer.save(ticker=stock, sync=sync)
        except Exception:
            sync.status = SyncStatus.FAILED
            sync.save()

            raise
        else:
            sync.status = SyncStatus.FINISHED
            sync.save()

            return Response(None, status=status.HTTP_201_CREATED)


class StockDividendStatsView(APIView):
    def get(self, request: Request, format=None) -> Response:
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
    permission_classes = [IsAuthenticated, IsBot]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.csv_service = CsvService()

    @allow_content_types(("multipart/form-data",))
    def post(self, request: Request, ticker: str, format=None) -> Response:
        # TODO: Add consistency checks.
        # TODO: Add cross checks.

        stock = get_object_or_404(Stock, ticker=ticker)
        sync = StockSplitSync(owner=request.user)
        sync.save()

        try:
            splits = self.csv_service.parse(
                request.FILES["data"].file, {"Date": "date", "Stock Splits": "ratio"}
            )
            latest_saved = (
                StockPrice.objects.all()
                .filter(ticker=stock)
                .aggregate(Max("date"))["date__max"]
            )

            formatted_splits = []
            for split in splits:
                if latest_saved and parser.parse(split["date"]).date() > latest_saved:
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

            serializer = StockSplitSerializer(data=formatted_splits, many=True)
            if not serializer.is_valid():
                sync.status = SyncStatus.FAILED
                sync.save()

                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            serializer.save(ticker=stock, sync=sync)
        except Exception:
            sync.status = SyncStatus.FAILED
            sync.save()

            raise
        else:
            sync.status = SyncStatus.FINISHED
            sync.save()

            return Response(None, status=status.HTTP_201_CREATED)


class StockSplitStatsView(APIView):
    def get(self, request: Request, format=None) -> Response:
        stats = (
            StockSplit.objects.all()
            .values("ticker")
            .annotate(count=Count("ticker"))
            .order_by("count")
        )

        return Response(stats)
