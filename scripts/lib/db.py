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

    config = {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", "root"),
        "database": os.getenv("MYSQL_DATABASE", "city_airline"),
    }
    config.update(overrides)
    return mysql.connector.connect(**config)


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
