"""Helpers for connecting to the City Airline MySQL database."""

from __future__ import annotations

import os
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any


def get_connection(**overrides: Any) -> Any:
    """Create a MySQL connection using environment variables or overrides.

    Supported environment variables are ``MYSQL_HOST``, ``MYSQL_PORT``,
    ``MYSQL_USER``, ``MYSQL_PASSWORD``, and ``MYSQL_DATABASE``.
    """
    try:
        import mysql.connector
    except ImportError as error:
        raise RuntimeError(
            "MySQL support requires mysql-connector-python. "
            "Install it with: pip install mysql-connector-python"
        ) from error

    user = overrides.pop("user", None) or _required_environment("MYSQL_USER")
    password = overrides.pop("password", None) or _required_environment(
        "MYSQL_PASSWORD"
    )
    config = {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": user,
        "password": password,
        "database": os.getenv("MYSQL_DATABASE", "city_airline"),
    }
    config.update(overrides)
    return mysql.connector.connect(**config)


def get_data_entry_connection(**overrides: Any) -> Any:
    """Create a connection for the staff-only constraint demonstration."""
    overrides.setdefault("user", _required_environment("MYSQL_DATA_ENTRY_USER"))
    overrides.setdefault(
        "password", _required_environment("MYSQL_DATA_ENTRY_PASSWORD")
    )
    return get_connection(**overrides)


def _required_environment(name: str) -> str:
    """Return a required configuration value without providing unsafe defaults."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} must be set before connecting to MySQL.")
    return value


@contextmanager
def connection(**overrides: Any) -> Generator[Any, None, None]:
    """Yield a connection and always close it when the block exits."""
    db_connection = get_connection(**overrides)
    try:
        yield db_connection
    finally:
        db_connection.close()


@contextmanager
def cursor(**overrides: Any) -> Generator[Any, None, None]:
    """Yield a cursor, committing successful work and rolling back failures."""
    with connection(**overrides) as db_connection:
        # Buffer result sets so callers may fetch only the rows they need.
        db_cursor = db_connection.cursor(buffered=True)
        try:
            yield db_cursor
        except BaseException:
            db_connection.rollback()
            raise
        else:
            db_connection.commit()
        finally:
            db_cursor.close()
