"""Creates a backup from the active database."""

from os import getenv, system

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Custom command to backup the database."""

    help = "Create a backup from the database."

    def handle(self, *args, **kwargs):
        system(  # nosec
            f"""pg_dump --no-owner postgres://{getenv('DATABASE_USER')}:{getenv('DATABASE_PASSWORD')}@{getenv(
                'DATABASE_HOST'
            )}:{getenv('DATABASE_PORT')}/{getenv('DATABASE_NAME')} > dump.sql"""
        )
