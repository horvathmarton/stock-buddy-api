"""Seed data for testing."""

from datetime import date

from django.contrib.auth.models import Group, User
from apps.raw_data.models import (
    StockDividend,
    StockDividendSync,
    StockPrice,
    StockPriceSync,
    StockSplit,
    StockSplitSync,
)
from apps.stocks.enums import Sector
from apps.stocks.models import Stock, StockPortfolio, StockWatchlist
from lib.enums import SyncStatus


class _UsersSeed:  # pylint: disable=too-few-public-methods
    """
    admin - Administrator user in the app.
    bot - Syncer bot user in the app.
    owner - Owner of the main portfolio from the mock. Its a general user.
    other - Other general user in the app.
    """

    def __init__(self):
        self.admin = User.objects.create_user(
            "admin",
            "admin@stockbuddy.com",
            "password",
            is_superuser=True,
            is_staff=True,
        )
        self.bot = User.objects.create_user("bot", "bot@stockbuddy.com", "password")
        self.other = User.objects.create_user(
            "other", "other@stockbuddy.com", "password"
        )
        self.owner = User.objects.create_user(
            "owner", "owner@stockbuddy.com", "password"
        )


class _GroupsSeed:  # pylint: disable=too-few-public-methods
    """
    admins - Group of administrators that can access everything in the app.
    bots - Group of bots who are syncing data to the platform.
    """

    def __init__(self):
        self.admins = Group.objects.create(name="Admins")
        self.bots = Group.objects.create(name="Bots")


class _StocksSeed:  # pylint: disable=too-few-public-methods
    """
    MSFT - Microsoft Corporation
    PM - Philip Morris International
    BABA - Alibaba Group Holding

    EV - Eaton Vance, this is an acquired company, not existing anymore. Good for testing an inactive stock.
    """

    def __init__(self):
        # pylint: disable=invalid-name

        self.MSFT = Stock.objects.create(
            active=True,
            name="Microsoft Corporation",
            ticker="MSFT",
            sector=Sector.SOFTWARE,
        )
        self.PM = Stock.objects.create(
            active=True,
            name="Philip Morris International Inc.",
            ticker="PM",
            sector=Sector.CONSUMER_GOODS,
        )
        self.BABA = Stock.objects.create(
            active=True,
            name="Alibaba Group Holdings",
            ticker="BABA",
            sector=Sector.CONSUMER_SERVICES,
        )
        self.EV = Stock.objects.create(
            active=False,
            name="Eaton Vance",
            ticker="EV",
            sector=Sector.FINANCIAL_SERVICES,
        )


class _PortfolioSeed:  # pylint: disable=too-few-public-methods
    """
    main - Main portfolio that could be the focus of the test cases.
    other - A secondary portfolio that could be used for comparison.
    other_users - A portfolio owned by the other user.
    """

    def __init__(self, USERS):
        self.main = StockPortfolio.objects.create(
            name="Example portfolio", owner=USERS.owner
        )
        self.other = StockPortfolio.objects.create(
            name="Other portfolio", owner=USERS.owner
        )
        self.other_users = StockPortfolio.objects.create(
            name="Other user's portfolio", owner=USERS.other
        )


class _StockWatchlistSeed:  # pylint: disable=too-few-public-methods
    """
    main - Main watchlist that could be the focus of the test cases.
    other_users - A watchlist owned by the other user.
    """

    def __init__(self, USERS):
        self.main = StockWatchlist.objects.create(
            name="Example portfolio", owner=USERS.owner
        )
        self.other_users = StockWatchlist.objects.create(
            name="Other user's portfolio", owner=USERS.other
        )


class _StockPriceSyncsSeed:  # pylint: disable=too-few-public-methods
    """
    main - Main sync to associate price info with.
    """

    def __init__(self, USERS):
        self.main = StockPriceSync.objects.create(
            owner=USERS.owner, status=SyncStatus.FINISHED
        )


class _StockPricesSeed:  # pylint: disable=too-few-public-methods
    """
    Stock prices synced into the app.
    - MSFT - 2020-12-13 - 2021-01-02
    """

    def __init__(self, STOCKS, SYNCS):
        StockPrice.objects.create(
            ticker=STOCKS.MSFT,
            date=date(2020, 12, 31),
            value=89,
            sync=SYNCS.main,
        )
        StockPrice.objects.create(
            ticker=STOCKS.MSFT, date=date(2021, 1, 1), value=89, sync=SYNCS.main
        )
        StockPrice.objects.create(
            ticker=STOCKS.MSFT, date=date(2021, 1, 2), value=90, sync=SYNCS.main
        )
        StockPrice.objects.create(
            ticker=STOCKS.PM, date=date(2021, 1, 1), value=46, sync=SYNCS.main
        )
        StockPrice.objects.create(
            ticker=STOCKS.PM, date=date(2021, 1, 2), value=45, sync=SYNCS.main
        )
        StockPrice.objects.create(
            ticker=STOCKS.BABA, date=date(2021, 1, 1), value=150, sync=SYNCS.main
        )
        StockPrice.objects.create(
            ticker=STOCKS.BABA, date=date(2021, 1, 2), value=170, sync=SYNCS.main
        )


class _StockDividendSyncsSeed:  # pylint: disable=too-few-public-methods
    """
    main - Main sync to associate dividend info with.
    """

    def __init__(self, USERS):
        self.main = StockDividendSync.objects.create(
            owner=USERS.owner, status=SyncStatus.FINISHED
        )


class _StockDividendsSeed:  # pylint: disable=too-few-public-methods
    """
    Stock dividends synced into the app.
    - MSFT
    """

    def __init__(self, STOCKS, SYNCS):
        StockDividend.objects.create(
            ticker=STOCKS.PM,
            amount=1.5,
            payout_date=date(2021, 1, 1),
            sync=SYNCS.main,
        )
        StockDividend.objects.create(
            ticker=STOCKS.MSFT,
            amount=3,
            payout_date=date(2021, 1, 1),
            sync=SYNCS.main,
        )


class _StockSplitSyncsSeed:  # pylint: disable=too-few-public-methods
    """
    main - Main sync to associate split info with.
    """

    def __init__(self, USERS):
        self.main = StockSplitSync.objects.create(
            owner=USERS.owner, status=SyncStatus.FINISHED
        )


class _StockSplitsSeed:  # pylint: disable=too-few-public-methods
    """
    Stock splits synced into the app.
    - PM
    """

    def __init__(self, STOCKS, SYNCS):
        StockSplit.objects.create(
            ticker=STOCKS.PM,
            date=date(2021, 1, 9),
            ratio=2,
            sync=SYNCS.main,
        )


class _Seed:  # pylint: disable=too-few-public-methods, disable=invalid-name, too-many-instance-attributes
    """
    Seed object that is returned when generating test data.

    To use seed data call the generation function and get the required
    object from this data.
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        USERS,
        GROUPS,
        STOCKS,
        PORTFOLIOS,
        STOCK_PRICE_SYNCS,
        STOCK_PRICES,
        STOCK_DIVIDEND_SYNCS,
        STOCK_DIVIDENDS,
        STOCK_SPLIT_SYNCS,
        STOCK_SPLITS,
        WATCHLISTS,
    ):
        self.USERS = USERS
        self.GROUPS = GROUPS
        self.STOCKS = STOCKS
        self.PORTFOLIOS = PORTFOLIOS
        self.STOCK_PRICE_SYNCS = STOCK_PRICE_SYNCS
        self.STOCK_PRICES = STOCK_PRICES
        self.STOCK_DIVIDEND_SYNCS = STOCK_DIVIDEND_SYNCS
        self.STOCK_DIVIDENDS = STOCK_DIVIDENDS
        self.STOCK_SPLIT_SYNCS = STOCK_SPLIT_SYNCS
        self.STOCK_SPLITS = STOCK_SPLITS
        self.WATCHLISTS = WATCHLISTS


def generate_test_data():
    """
    Create a seed data structure to use in tests.

    This should contain core data that could be shared between tests. So stock, price data etc.
    The transaction data should be added in the specific test cases.
    """

    users = _UsersSeed()
    groups = _GroupsSeed()
    stocks = _StocksSeed()

    users.admin.groups.add(groups.admins)
    users.bot.groups.add(groups.bots)

    portfolios = _PortfolioSeed(users)
    watchlists = _StockWatchlistSeed(users)

    stock_price_syncs = _StockPriceSyncsSeed(users)
    stock_dividend_syncs = _StockDividendSyncsSeed(users)
    stock_split_syncs = _StockSplitSyncsSeed(users)

    stock_prices = _StockPricesSeed(stocks, stock_price_syncs)
    stock_dividends = _StockDividendsSeed(stocks, stock_dividend_syncs)
    stock_splits = _StockSplitsSeed(stocks, stock_split_syncs)

    return _Seed(
        USERS=users,
        GROUPS=groups,
        STOCKS=stocks,
        PORTFOLIOS=portfolios,
        STOCK_PRICE_SYNCS=stock_price_syncs,
        STOCK_PRICES=stock_prices,
        STOCK_DIVIDEND_SYNCS=stock_dividend_syncs,
        STOCK_DIVIDENDS=stock_dividends,
        STOCK_SPLIT_SYNCS=stock_split_syncs,
        STOCK_SPLITS=stock_splits,
        WATCHLISTS=watchlists,
    )
