"""Data returned by the City Airline application queries."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class Airport:
    """An airport available in the flight-search form."""

    id: str
    code: str
    name: str
    location: str

    @property
    def label(self) -> str:
        """Return the human-readable airport label."""
        return f"{self.code} - {self.name}"


@dataclass(frozen=True)
class Passenger:
    """A passenger profile available for booking or contact updates."""

    id: str
    contact_information: str

    @property
    def label(self) -> str:
        """Return the contact displayed in the passenger selector."""
        return self.contact_information


@dataclass(frozen=True)
class Flight:
    """Flight information displayed in search results."""

    id: str
    flight_number: str
    departure_time: datetime
    boarding_time: datetime
    airline_name: str
    airline_code: str
    plane_name: str
    plane_code: str
    departure_airport_code: str
    departure_airport_name: str
    arrival_airport_code: str
    arrival_airport_name: str
    lowest_available_price: Decimal | None


@dataclass(frozen=True)
class SeatSummary:
    """Availability and pricing totals for one seat class."""

    class_designation: str
    available_seat_count: int
    average_available_price: Decimal | None


@dataclass(frozen=True)
class AvailableSeat:
    """An available ticket and its physical seat."""

    ticket_id: str
    seat_number: int
    class_designation: str
    price: Decimal

    @property
    def label(self) -> str:
        """Return the label shown in the seat selector."""
        return f"Seat {self.seat_number} ({self.class_designation}) - ${self.price:.2f}"
