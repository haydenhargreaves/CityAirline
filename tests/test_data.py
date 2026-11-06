"""Tests for the database transaction behavior used during checkout."""

import unittest

from app.data import CityAirlineData, TicketUnavailableError


class FakeCursor:
    """Minimal cursor used to test transaction control without MySQL."""

    def __init__(self, ticket_update_count: int) -> None:
        self.ticket_update_count = ticket_update_count
        self.rowcount = 0
        self.closed = False

    def execute(self, query: str, parameters: tuple[str, ...]) -> None:
        if "UPDATE Tickets" in query:
            self.rowcount = self.ticket_update_count

    def close(self) -> None:
        self.closed = True


class FakeConnection:
    """Record checkout transaction outcomes for assertions."""

    def __init__(self, ticket_update_count: int) -> None:
        self.cursor_instance = FakeCursor(ticket_update_count)
        self.committed = False
        self.rolled_back = False
        self.closed = False

    def cursor(self, buffered: bool) -> FakeCursor:
        return self.cursor_instance

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True

    def close(self) -> None:
        self.closed = True


class PurchaseTicketTests(unittest.TestCase):
    """Verify that a lost seat rolls back the newly created passenger."""

    def test_purchase_commits_when_ticket_is_available(self) -> None:
        connection = FakeConnection(ticket_update_count=1)

        passenger_id = CityAirlineData(lambda: connection).purchase_ticket(
            "ticket-id", "traveler@example.com"
        )

        self.assertTrue(passenger_id)
        self.assertTrue(connection.committed)
        self.assertFalse(connection.rolled_back)

    def test_purchase_rolls_back_when_ticket_is_unavailable(self) -> None:
        connection = FakeConnection(ticket_update_count=0)

        with self.assertRaises(TicketUnavailableError):
            CityAirlineData(lambda: connection).purchase_ticket(
                "ticket-id", "traveler@example.com"
            )

        self.assertFalse(connection.committed)
        self.assertTrue(connection.rolled_back)


if __name__ == "__main__":
    unittest.main()
