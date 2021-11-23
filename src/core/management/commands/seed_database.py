from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from src.stocks.enums import Sector
from src.stocks.models import Stock


class Command(BaseCommand):
    help = "Seeds the database with example data."

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding users.")
        seed_users()
        self.stdout.write("Seeding stocks.")
        seed_stocks()


def seed_users():
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
