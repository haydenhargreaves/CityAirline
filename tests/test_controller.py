"""Tests for friendly controller outcomes used by Streamlit views."""

import unittest
from datetime import date, datetime

from app.controller import CityAirlineController
from app.data import ConstraintViolationError, PermissionDeniedError, TicketUnavailableError
from app.models import FlightSearchResult


class FakeCityAirlineData:
    """Small data substitute that makes controller outcomes predictable."""

    def search_route(
        self, departure_airport_id: str, arrival_airport_id: str, travel_date: date
    ) -> list[FlightSearchResult]:
        return [
            FlightSearchResult(
                "flight-id", "CTA101", datetime(2026, 10, 1, 9, 0)
            )
        ]

    def purchase_ticket(
        self,
        ticket_id: str,
        passenger_id: str | None,
        contact_information: str | None,
    ) -> str:
        raise TicketUnavailableError()

    def demonstrate_duplicate_ticket_constraint(self) -> None:
        raise ConstraintViolationError()

    def demonstrate_denied_flight_insert(self) -> None:
        raise PermissionDeniedError()


class ControllerTests(unittest.TestCase):
    """Verify that views receive values or friendly messages, never exceptions."""

    def setUp(self) -> None:
        self.controller = CityAirlineController(FakeCityAirlineData())

    def test_search_returns_matching_route_flights(self) -> None:
        search_result = self.controller.search_flights(
            "departure-id", "arrival-id", date(2026, 10, 1)
        )

        self.assertTrue(search_result.succeeded)
        self.assertEqual(search_result.value[0].flight_number, "CTA101")

    def test_unavailable_ticket_returns_friendly_message(self) -> None:
        purchase_result = self.controller.purchase_ticket(
            "ticket-id", None, "traveler@example.com"
        )

        self.assertFalse(purchase_result.succeeded)
        self.assertEqual(
            purchase_result.error_message,
            "That seat was just sold. Please choose another seat.",
        )

    def test_constraint_rejection_is_a_successful_demonstration(self) -> None:
        demonstration_result = self.controller.demonstrate_duplicate_ticket_constraint()

        self.assertTrue(demonstration_result.succeeded)

    def test_permission_rejection_is_a_successful_demonstration(self) -> None:
        demonstration_result = self.controller.demonstrate_denied_flight_creation()

        self.assertTrue(demonstration_result.succeeded)


if __name__ == "__main__":
    unittest.main()
