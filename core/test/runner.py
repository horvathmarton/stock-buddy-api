"""Custom test runners for the project."""

from types import MethodType
from django.test.runner import DiscoverRunner
from django.db import connections


def prepare_database(self):
    """Sets up the schemas required by the Postgres database."""

    self.connect()
    self.connection.cursor().execute(
        """
            CREATE SCHEMA raw_data;
            CREATE SCHEMA stocks;
            CREATE SCHEMA transactions;
    """
    )


class PostgresSchemaTestRunner(DiscoverRunner):
    """Custom test runner to set up Postgres database schemas properly, before running."""

    def setup_databases(self, **kwargs):
        for connection_name in connections:
            connection = connections[connection_name]
            connection.prepare_database = MethodType(prepare_database, connection)
        return super().setup_databases(**kwargs)
