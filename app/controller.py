"""Application actions and friendly error handling for the Streamlit views."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from typing import Generic, TypeVar

from app.data import (
    CityAirlineData,
    ConstraintViolationError,
    PermissionDeniedError,
    TicketUnavailableError,
)
from app.models import Airport, AvailableSeat, Flight, FlightSearchResult, Passenger, SeatSummary


ResultValue = TypeVar("ResultValue")


@dataclass(frozen=True)
class ActionResult(Generic[ResultValue]):
    """The value or friendly failure message from an application action."""

    value: ResultValue | None = None
    error_message: str | None = None

    @property
    def succeeded(self) -> bool:
        """Return whether the action completed successfully."""
        return self.error_message is None


class CityAirlineController:
    """Expose explicit application actions without database exceptions in views."""

    def __init__(self, city_airline_data: CityAirlineData) -> None:
        self.city_airline_data = city_airline_data

    def load_airports(self) -> ActionResult[list[Airport]]:
        """Load the airports available in route forms."""
        return self._run(self.city_airline_data.list_airports, "Unable to load airports.")

    def search_flights(
        self,
        departure_airport_id: str,
        arrival_airport_id: str,
        selected_travel_date: date,
    ) -> ActionResult[list[FlightSearchResult]]:
        """Search flights for a selected route and date."""
        return self._run(
            lambda: self.city_airline_data.search_route(
                departure_airport_id, arrival_airport_id, selected_travel_date
            ),
            "Unable to search for flights right now.",
        )

    def load_flight_details(self, flight_id: str) -> ActionResult[Flight]:
        """Load joined details for a selected flight."""
        result = self._run(
            lambda: self.city_airline_data.get_flight_details(flight_id),
            "Unable to load flight details.",
        )
        if result.succeeded and result.value is None:
            return ActionResult(error_message="The selected flight was not found.")
        return result

    def load_seat_summary(self, flight_id: str) -> ActionResult[list[SeatSummary]]:
        """Load grouped availability and pricing for a selected flight."""
        return self._run(
            lambda: self.city_airline_data.get_seat_summary(flight_id),
            "Unable to load seat availability.",
        )

    def find_fare_deals(
        self,
        departure_airport_id: str,
        arrival_airport_id: str,
        selected_travel_date: date,
    ) -> ActionResult[list[Flight]]:
        """Find available fares below the route average."""
        return self._run(
            lambda: self.city_airline_data.find_fare_deals(
                departure_airport_id, arrival_airport_id, selected_travel_date
            ),
            "Unable to find fare deals right now.",
        )

    def create_passenger_profile(self, contact_information: str) -> ActionResult[str]:
        """Create a new passenger profile."""
        return self._run(
            lambda: self.city_airline_data.create_passenger(contact_information),
            "Unable to create the passenger profile.",
        )

    def load_passengers(self) -> ActionResult[list[Passenger]]:
        """Load passenger profiles for selection controls."""
        return self._run(
            self.city_airline_data.list_passengers,
            "Unable to load passenger profiles.",
        )

    def update_passenger_contact(
        self, passenger_id: str, contact_information: str
    ) -> ActionResult[bool]:
        """Update a selected passenger profile."""
        return self._run(
            lambda: self.city_airline_data.update_passenger_contact(
                passenger_id, contact_information
            ),
            "Unable to update the passenger profile.",
        )

    def load_available_seats(self, flight_id: str) -> ActionResult[list[AvailableSeat]]:
        """Load tickets that are currently available to purchase."""
        return self._run(
            lambda: self.city_airline_data.list_available_seats(flight_id),
            "Unable to load ticket options.",
        )

    def purchase_ticket(
        self,
        ticket_id: str,
        passenger_id: str | None,
        contact_information: str | None,
    ) -> ActionResult[str]:
        """Purchase an available ticket in the data-layer transaction."""
        return self._run(
            lambda: self.city_airline_data.purchase_ticket(
                ticket_id, passenger_id, contact_information
            ),
            "Unable to complete the purchase.",
        )

    def demonstrate_duplicate_ticket_constraint(self) -> ActionResult[None]:
        """Run the staff-only unique-ticket constraint demonstration."""
        try:
            self.city_airline_data.demonstrate_duplicate_ticket_constraint()
        except ConstraintViolationError:
            return ActionResult()
        except Exception as error:
            return self._database_error_result(error, "Unable to run the constraint demonstration.")
        return ActionResult(error_message="The duplicate ticket was unexpectedly accepted.")

    def demonstrate_denied_flight_creation(self) -> ActionResult[None]:
        """Run the client-account permission denial demonstration."""
        try:
            self.city_airline_data.demonstrate_denied_flight_insert()
        except PermissionDeniedError:
            return ActionResult()
        except Exception as error:
            return self._database_error_result(error, "Unable to run the permission demonstration.")
        return ActionResult(error_message="The client account unexpectedly created a flight.")

    def _run(
        self, database_action: Callable[[], ResultValue], fallback_error_message: str
    ) -> ActionResult[ResultValue]:
        """Run one database action and convert expected failures into messages."""
        try:
            return ActionResult(value=database_action())
        except TicketUnavailableError:
            return ActionResult(
                error_message="That seat was just sold. Please choose another seat."
            )
        except ConstraintViolationError as error:
            return ActionResult(error_message=str(error))
        except PermissionDeniedError as error:
            return ActionResult(error_message=str(error))
        except Exception as error:
            return self._database_error_result(error, fallback_error_message)

    def _database_error_result(
        self, error: Exception, fallback_error_message: str
    ) -> ActionResult[None]:
        """Translate a MySQL error number into the message shown to users."""
        error_number = getattr(error, "errno", None)
        known_messages = {
            1062: "This record already exists.",
            1142: "You do not have permission to perform this operation.",
            1452: "The selected related record no longer exists.",
        }
        return ActionResult(
            error_message=known_messages.get(error_number, fallback_error_message)
        )
