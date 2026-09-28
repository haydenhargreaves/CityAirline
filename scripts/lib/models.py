"""Python representations of the City Airline database tables."""

from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import Decimal


@dataclass
class Airport:
    """An airport where flights depart or arrive."""

    id: str
    name: str
    code: str
    location: str
    created: datetime
    updated: datetime | None


@dataclass
class Airline:
    """An airline that operates flights."""

    id: str
    name: str
    code: str
    created: datetime
    updated: datetime | None


@dataclass
class Plane:
    """An aircraft assigned to flights and seats."""

    id: str
    name: str
    code: str
    tail_number: str
    created: datetime
    updated: datetime | None


@dataclass
class Passenger:
    """A passenger who may hold tickets."""

    id: str
    contact_information: str
    created: datetime
    updated: datetime | None


@dataclass
class Seat:
    """A seat on a specific plane."""

    id: str
    seat_number: int
    class_designation: str
    plane_id: str
    created: datetime
    updated: datetime | None


@dataclass
class Flight:
    """A scheduled flight between two airports."""

    id: str
    flight_number: str
    departure_time: datetime
    boarding_time: datetime
    airline_id: str
    plane_id: str
    airport_id_departure: str
    airport_id_arrival: str
    created: datetime
    updated: datetime | None


@dataclass
class Delay:
    """A recorded delay affecting a flight."""

    id: str
    duration: time
    reason: str
    flight_id: str
    created: datetime
    updated: datetime | None


@dataclass
class Ticket:
    """A ticket for a seat on a flight."""

    id: str
    cost: Decimal
    sale_price: Decimal | None
    sale_date: date | None
    sale_status: str
    passenger_id: str | None
    seat_id: str
    flight_id: str
    created: datetime
    updated: datetime | None
