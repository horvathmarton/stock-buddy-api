"""Database recreation for the project."""

from os import getenv

from django.core.management.base import BaseCommand
from psycopg2 import connect, extensions, sql


class Command(BaseCommand):
    """
    Custom command to drop and recreate a database for the project.

    It removes existing data so only use on development environment!
    """

    help = "Drop the existing database and recreate it with schemas."

    def handle(self, *args, **kwargs):
        self.stdout.write(ending="\n")

        self.stdout.write(
            f"-------- Drop and recreate the database {getenv('DATABASE_NAME')}. --------",
            ending="\n\n",
        )
        drop_and_recreate_database()

        self.stdout.write(
            "-------- Create schemas in the new database. --------", ending="\n\n"
        )
        create_schemas()


def drop_and_recreate_database():
    """Drops the database accessible with the provided creds and recreates an empty database."""

    connection = connect(
        host=getenv("DATABASE_HOST"),
        user=getenv("DATABASE_USER"),
        password=getenv("DATABASE_PASSWORD"),
        dbname="postgres",
    )
    connection.set_isolation_level(extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()

    cursor.execute(sql.SQL(f"DROP DATABASE IF EXISTS {getenv('DATABASE_NAME')}"))
    cursor.execute(sql.SQL(f"CREATE DATABASE {getenv('DATABASE_NAME')}"))

    connection.close()


def create_schemas():
    """Create the schemas for the Postgres database."""

    connection = connect(
        host=getenv("DATABASE_HOST"),
        user=getenv("DATABASE_USER"),
        password=getenv("DATABASE_PASSWORD"),
        dbname=getenv("DATABASE_NAME"),
    )

    with connection:
        cursor = connection.cursor()

        cursor.execute(sql.SQL("CREATE SCHEMA raw_data"))
        cursor.execute(sql.SQL("CREATE SCHEMA stocks"))
        cursor.execute(sql.SQL("CREATE SCHEMA transactions"))
        cursor.execute(sql.SQL("CREATE SCHEMA dashboard"))
