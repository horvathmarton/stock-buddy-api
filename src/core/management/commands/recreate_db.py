from os import getenv

from django.core.management.base import BaseCommand
from psycopg2 import connect, extensions, sql


class Command(BaseCommand):
    help = "Drop the existing database and recreate it with schemas."

    def handle(self, *args, **kwargs):
        self.stdout.write(
            f"-------- Drop and recreate the database {getenv('DATABASE_NAME')}. --------"
        )
        drop_and_recreate_database()
        self.stdout.write("-------- Create schemas in the new database. --------")
        create_schemas()


def drop_and_recreate_database():
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
