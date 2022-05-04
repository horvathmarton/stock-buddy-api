"""Business logic for the dashboard module."""

from datetime import date, datetime
from logging import getLogger

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from src.lib.services.stocks import get_first_transaction, get_portfolio_snapshot

from ..lib.enums import Visibility
from ..lib.services.cash import (
    balance_to_usd,
    get_invested_capital_snapshot,
    get_portfolio_cash_balance_snapshot,
)
from ..stocks.models import StockPortfolio
from .models import Strategy, StrategyItem, UserStrategy
from .serializers import StrategySerializer

LOGGER = getLogger(__name__)


class StrategyView(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Business logic for the strategy API."""

    queryset = Strategy.objects.all()
    serializer_class = StrategySerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"])
    def me(self, request: Request) -> Response:
        """Fetch the authenticated user's current and target strategy."""

        LOGGER.info("Lookup target and current strategies for %s.", self.request.user)

        LOGGER.debug("List strategies belonging to %s.", self.request.user)
        strategies = UserStrategy.objects.filter(user=self.request.user)

        if not strategies:
            LOGGER.warning("%s sees no strategies.", self.request.user)
            return Response("Not found", status=404)

        LOGGER.debug(
            "Selecting the target strategy %s for %s.",
            strategies[0].strategy_id,
            self.request.user,
        )
        strategy = Strategy.objects.get(pk=strategies[0].strategy_id)
        serializer = self.get_serializer(strategy)

        return Response(
            {
                "current": {"items": [{"name": "stocks", "size": 1}]},
                "target": serializer.data,
            }
        )

    def create(self, request: Request, *args, **kwargs) -> Response:
        """Create a new user strategy."""

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        items = request.data["items"]
        owner = request.user

        LOGGER.debug(
            "Inserting a new strategy named %s for %s.", serializer.data["name"], owner
        )
        # We only allow for the user to create private strategies for now to avoid spamming each other.
        # Public strategies will be added by administrators.
        strategy = Strategy.objects.create(
            name=serializer.data["name"],
            owner=owner,
            visibility=Visibility.PRIVATE,
        )

        LOGGER.debug(
            "Inserting %s strategy items for %s strategy.",
            len(items),
            strategy.name,
        )
        StrategyItem.objects.bulk_create(
            [StrategyItem(strategy=strategy, **item) for item in items]
        )

        inserted_strategy = Strategy.objects.get(pk=strategy.id)
        serializer = self.get_serializer(inserted_strategy)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request: Request, *args, **kwargs) -> Response:
        """Update the name of the given strategy."""

        name = request.data.get("name")
        strategy_id = kwargs["pk"]
        LOGGER.info(
            "%s is trying to update %s strategy's name to %s.",
            self.request.user,
            strategy_id,
            name,
        )
        if not isinstance(name, str):
            raise ValidationError("Name property is required and must be a string.")

        LOGGER.debug("Looking up %s.", strategy_id)
        strategy = get_object_or_404(Strategy, id=strategy_id)
        LOGGER.debug("Updating %s strategy's name to %s.", strategy_id, name)
        strategy.name = name
        strategy.save()

        serializer = self.get_serializer(strategy)

        return Response(serializer.data)

    def update(self, request: Request, *args, **kwargs) -> Response:
        """Update a user strategy."""

        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        # Remove the old strategy items.
        LOGGER.debug("Remove existing strategy items from %s.", instance.name)
        StrategyItem.objects.filter(strategy=instance).delete()

        items = request.data["items"]
        LOGGER.debug(
            "Inserting %s new strategy items for %s strategy.",
            len(items),
            instance.name,
        )
        StrategyItem.objects.bulk_create(
            [StrategyItem(strategy=instance, **item) for item in items]
        )

        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return Response(serializer.data)

    def filter_queryset(self, queryset):
        is_admin = self.request.user.groups.filter(name="Admins").exists()

        if is_admin:
            return queryset

        return queryset.filter(
            Q(owner=self.request.user) | Q(visibility=Visibility.PUBLIC)
        )


class PortfolioIndicatorView(APIView):
    """Business logic for the portfolio indicators API."""

    def get(self, request: Request):
        """
        Collect and return the main indicators about the performance
        of the whole portfolio and the stock section specifically.
        """

        LOGGER.info(
            "Collecting portfolio indicators for %s's dashboard.",
            self.request.user,
        )

        LOGGER.debug("Lookup stock portfolios for %s.", self.request.user)
        user_portfolios = list(StockPortfolio.objects.filter(owner=self.request.user))
        if not user_portfolios:
            raise NotFound("The user has no stock portfolios.")

        LOGGER.debug(
            "Calculating the summary of %s portfolio for %s.",
            len(user_portfolios),
            self.request.user,
        )
        summary = get_portfolio_snapshot(user_portfolios, date.today())
        balance = get_portfolio_cash_balance_snapshot(portfolios=user_portfolios)
        balance_in_usd = balance_to_usd(balance)
        invested_capital = get_invested_capital_snapshot(portfolios=user_portfolios)
        capital = balance_to_usd(invested_capital)

        LOGGER.debug("Calculating portfolio indicators for %s.", self.request.user)
        aum = summary.assets_under_management
        pnl = aum - capital
        roic = pnl / capital if capital else 0

        # This is not perfectly correct
        first_transaction = get_first_transaction(user_portfolios)
        inception_year = (
            first_transaction.date.year if first_transaction else date.today().year
        )
        current_year = datetime.now().year

        if current_year - inception_year:
            annualized_roic = abs(roic + 1) ** (1 / (current_year - inception_year)) - 1
            annualized_roic = annualized_roic if roic >= 0 else -1 * annualized_roic
        else:
            annualized_roic = roic

        return Response(
            {
                "largest_position_exposure": max(
                    position for position in summary.size_distribution.values()
                ),
                "largest_sector_exposure": max(
                    sector for sector in summary.sector_distribution.values()
                ),
                "total_aum": aum,
                "gross_capital_deployed": 1 - (balance_in_usd / capital)
                if capital
                else 0,
                "total_invested_capital": capital,
                "total_floating_pnl": pnl,
                "roic_since_inception": roic,
                "annualized_roic": annualized_roic,
                "annual_dividend_income": summary.dividend,
            }
        )


class SelectStrategyView(APIView):
    """Business logic for the target strategy selection API."""

    def post(self, request: Request) -> Response:
        """Sets a target strategy for the authenticated user."""

        strategy_id = self.request.data.get("strategy")
        LOGGER.info(
            "%s is trying to select %s as target strategy.",
            self.request.user,
            strategy_id,
        )
        if not isinstance(strategy_id, int):
            raise ValidationError(
                "Strategy property is required and must be an integer."
            )

        LOGGER.debug("Looking up %s.", strategy_id)
        strategy = get_object_or_404(Strategy, pk=strategy_id)
        if (
            strategy.visibility != Visibility.PUBLIC
            and strategy.owner != self.request.user
        ):
            raise NotFound()

        LOGGER.debug(
            "Updating target strategy for %s to %s.", self.request.user, strategy_id
        )
        UserStrategy.objects.update_or_create(
            user=self.request.user, defaults={"strategy": strategy}
        )

        return Response(status=201)
