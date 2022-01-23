"""Business logic for the dashboard module."""

from datetime import datetime

from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed, NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from lib.enums import Visibility
from lib.services.finance import FinanceService

from apps.dashboard.models import Strategy, UserStrategy
from apps.dashboard.serializers import StrategySerializer
from apps.stocks.models import StockPortfolio


class StrategyView(ModelViewSet):
    """Business logic for the strategy API."""

    queryset = Strategy.objects.all()
    serializer_class = StrategySerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"])
    def me(self, request: Request) -> Response:
        """Fetch the authenticated user's current and target strategy."""

        strategies = UserStrategy.objects.filter(user=self.request.user)

        if not strategies:
            return Response("Not found")

        strategy = Strategy.objects.get(pk=strategies[0].id)
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

        if not isinstance(strategy_id, int):
            raise ValidationError(
                "Strategy property is required and must be an integer."
            )

        strategy = get_object_or_404(Strategy, pk=strategy_id)
        if (
            strategy.visibility != Visibility.PUBLIC
            and strategy.owner != self.request.user
        ):
            raise NotFound()

        UserStrategy.objects.update_or_create(
            user=self.request.user, defaults={"strategy": strategy}
        )

        return Response(status=201)

    def partial_update(self, request: Request, *args, **kwargs) -> Response:
        """Update the name of the given strategy."""

        name = request.data.get("name")

        if not isinstance(name, str):
            raise ValidationError("Name property is required and must be a string.")

        strategy = get_object_or_404(Strategy, id=kwargs["pk"])
        strategy.name = name
        strategy.save()

        serializer = self.get_serializer(strategy)

        return Response(serializer.data)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        raise MethodNotAllowed(
            detail="Strategies cannot be deleted via API.", method="DELETE"
        )

    def filter_queryset(self, queryset):
        is_admin = self.request.user.groups.filter(name="Admins").exists()

        if is_admin:
            return queryset

        return queryset.filter(owner=self.request.user)


class PortfolioIndicatorView(APIView):
    """Business logic for the portfolio indicators API."""

    def __init__(self, *args, **kwargs):
        self.finance_service = FinanceService()
        super().__init__(*args, **kwargs)

    def get(self, request: Request):
        """
        Collect and return the main indicators about the performance
        of the whole portfolio and the stock section specifically.
        """

        user_portfolios = list(StockPortfolio.objects.filter(owner=self.request.user))
        if not user_portfolios:
            raise NotFound("The user has no stock portfolios.")

        summary = self.finance_service.get_portfolio_snapshot(
            portfolios=user_portfolios
        )

        aum = summary.assets_under_management
        capital = summary.capital_invested
        pnl = aum - capital
        roic = pnl / capital

        # This is not perfectly correct
        inception_year = min(
            position.first_purchase_date for position in summary.positions.values()
        ).year
        current_year = datetime.now().year
        annualized_roic = abs(roic) ** (1 / (current_year - inception_year))
        annualized_roic = annualized_roic if roic >= 0 else -1 * annualized_roic

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
            }
        )
