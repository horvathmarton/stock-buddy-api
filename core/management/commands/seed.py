"""Seeding command for the project."""

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from apps.stocks.enums import Sector
from apps.stocks.models import Stock


class Command(BaseCommand):
    """
    Custom command to seed a testing database for the project.

    This is dummy data only use on testing databases!
    """

    help = "Seeds the database with example data."

    def handle(self, *args, **kwargs):
        self.stdout.write(ending="\n")

        self.stdout.write("-------- Seeding users. --------", ending="\n\n")
        seed_users()

        self.stdout.write("-------- Seeding stocks. --------", ending="\n\n")
        seed_stocks()


def seed_users():
    """Create some dummy users in the database."""

    mhorvath = User.objects.create_user(
        "mhorvath",
        "mhorvath@stock-buddy.com",
        "password",
        is_superuser=True,
        is_staff=True,
    )
    sync_bot = User.objects.create_user("sync-bot", "sync@stock-buddy.com", "botpass1")

    admin_group = Group.objects.create(name="Admins")
    bots_group = Group.objects.create(name="Bots")

    mhorvath.groups.add(admin_group)
    sync_bot.groups.add(bots_group)


def seed_stocks():
    """Create some dummy stocks in the database."""

    Stock.objects.bulk_create(
        [
            Stock(ticker="MSFT", name="Microsoft Corporation", sector=Sector.SOFTWARE),
            Stock(
                ticker="PM",
                name="Philip Morris International",
                sector=Sector.CONSUMER_GOODS,
            ),
            Stock(
                ticker="BABA",
                name="Alibaba Group Holding Limited",
                sector=Sector.CONSUMER_SERVICES,
            ),
        ]
    )
