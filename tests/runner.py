"""This module customizes the database setup process before running the tests."""

from types import MethodType
from typing import Any

from django.db import connections
from django.db.backends.base.base import BaseDatabaseWrapper
from django.test.runner import DiscoverRunner


def prepare_db(self):
    """
    Prepare the database by creating the `banks_data` schema if it does not already exist.

    Args:
        self: The database connection instance to which this method is bound.
    """
    self.connect()
    self.connection.cursor().execute('CREATE SCHEMA IF NOT EXISTS banks_data;')


class PostgresSchemaRunner(DiscoverRunner):
    """
    A custom test runner that ensures the `banks_data` schema is created.

    Methods:
        setup_databases: Sets up the databases for testing.
    """

    def setup_databases(
        self, **kwargs: Any,
    ) -> list[tuple[BaseDatabaseWrapper, str, bool]]:
        """
        Set up the test databases, preparing each database by creating the `banks_data` schema.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            A list of tuples, where each tuple contains a database wrapper, its name, and a boolean
            indicating whether the database was created.
        """
        for conn_name in connections:
            connection = connections[conn_name]
            connection.prepare_database = MethodType(prepare_db, connection)
        return super().setup_databases(**kwargs)
