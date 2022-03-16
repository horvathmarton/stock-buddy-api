"""Business logic for the dashboard module."""

from datetime import date, datetime
from logging import getLogger

from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed, NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.dashboard.models import Strategy, UserStrategy
from apps.dashboard.serializers import StrategySerializer
from apps.stocks.models import StockPortfolio
from lib.enums import Visibility
from lib.services.cash import CashService
from lib.services.stocks import StocksService


LOGGER = getLogger(__name__)


class StrategyView(ModelViewSet):
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

    @action(detail=False, methods=["post"])
    def select_strategy(self, request: Request) -> Response:
        """Sets a target strategy for the authenticated user."""

        strategy_id = request.data.get("strategy")
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

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        LOGGER.warning("%s is trying to delete a strategy.", self.request.user)
        raise MethodNotAllowed(
            detail="Strategies cannot be deleted via API.", method="DELETE"
        )

    def filter_queryset(self, queryset):
        is_admin = self.request.user.groups.filter(name="Admins").exists()

        if is_admin:
            return queryset

        return queryset.filter(
            Q(owner=self.request.user) | Q(visibility=Visibility.PUBLIC)
        )


class PortfolioIndicatorView(APIView):
    """Business logic for the portfolio indicators API."""

    def __init__(self, *args, **kwargs):
        self.stocks_service = StocksService()
        self.cash_service = CashService()
        super().__init__(*args, **kwargs)

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
        summary = self.stocks_service.get_portfolio_snapshot(portfolios=user_portfolios)
        balance = self.cash_service.get_invested_capital(portfolios=user_portfolios)

        LOGGER.debug("Calculating portfolio indicators for %s.", self.request.user)
        aum = summary.assets_under_management
        # pylint: disable=fixme
        # TODO: Replace me when adding raw forex data.
        capital = balance.HUF / 300
        pnl = aum - capital
        roic = pnl / capital if capital else 0

        # This is not perfectly correct
        first_transaction = self.stocks_service.get_first_transaction(user_portfolios)
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
                "largestPositionExposure": 5,
                "largetsSectorExposure": 4,
                "totalAum": aum,
                "grossCapitalDeployed": 1,
                "totalInvestedCapital": capital,
                "totalFloatingPnl": pnl,
                "roicSinceInception": roic,
                "annualizedRoic": annualized_roic,
                "annualDividendIncome": summary.dividend,
            }
        )
