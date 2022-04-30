"""Custom test runners for the project."""

import logging
from types import MethodType

from django.db import connections
from django.test.runner import DiscoverRunner


def prepare_database(self):
    """Sets up the schemas required by the Postgres database."""

    self.connect()
    self.connection.cursor().execute(
        """
            CREATE SCHEMA raw_data;
            CREATE SCHEMA stocks;
            CREATE SCHEMA transactions;
            CREATE SCHEMA dashboard;
        """
    )


class PostgresSchemaTestRunner(DiscoverRunner):
    """Custom test runner to set up Postgres database schemas properly, before running."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logging.disable(logging.CRITICAL)

    def setup_databases(self, **kwargs):
        for connection_name in connections:
            connection = connections[connection_name]
            connection.prepare_database = MethodType(prepare_database, connection)
        return super().setup_databases(**kwargs)
