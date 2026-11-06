"""Database operations used by the City Airline Streamlit application."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date
from typing import Any
from uuid import uuid4

from scripts.lib.db import get_connection

from app.models import Airport, AvailableSeat, Flight, Passenger, SeatSummary


class TicketUnavailableError(Exception):
    """Raised when a selected ticket is no longer available to purchase."""


ConnectionFactory = Callable[[], Any]


class CityAirlineData:
    """Read and write application data without exposing SQL to the UI."""

    def __init__(self, connection_factory: ConnectionFactory = get_connection) -> None:
        self.connection_factory = connection_factory

    def list_airports(self) -> list[Airport]:
        """Return airports in a stable order for the search form."""
        with self._cursor() as cursor:
            cursor.execute(
                """
                SELECT id, code, name, location
                FROM Airports
                ORDER BY code
                """
            )
            return [Airport(*row) for row in cursor.fetchall()]

    def list_passengers(self) -> list[Passenger]:
        """Return passenger profiles for returning travelers."""
        with self._cursor() as cursor:
            cursor.execute(
                """
                SELECT id, contact_information
                FROM Passengers
                ORDER BY contact_information
                """
            )
            return [Passenger(*row) for row in cursor.fetchall()]

    def search_flights(
        self,
        departure_airport_id: str,
        arrival_airport_id: str,
        travel_date: date,
        below_route_average: bool = False,
    ) -> list[Flight]:
        """Return route flights, optionally limited to below-average fares."""
        average_price_filter = ""
        parameters: tuple[Any, ...] = (
            departure_airport_id,
            arrival_airport_id,
            travel_date,
        )
        if below_route_average:
            average_price_filter = """
                HAVING MIN(Tickets.cost) < (
                    SELECT AVG(AvailableTickets.cost)
                    FROM Flights AS RouteFlights
                    INNER JOIN Tickets AS AvailableTickets
                        ON AvailableTickets.flight_id = RouteFlights.id
                        AND AvailableTickets.sale_status = 'available'
                        AND AvailableTickets.passenger_id IS NULL
                    WHERE RouteFlights.airport_id_departure = %s
                        AND RouteFlights.airport_id_arrival = %s
                        AND DATE(RouteFlights.departure_time) = %s
                )
            """
            parameters += (
                departure_airport_id,
                arrival_airport_id,
                travel_date,
            )
        with self._cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    Flights.id,
                    Flights.flight_number,
                    Flights.departure_time,
                    Flights.boarding_time,
                    Airlines.name,
                    Airlines.code,
                    Planes.name,
                    Planes.code,
                    departure_airport.code,
                    departure_airport.name,
                    arrival_airport.code,
                    arrival_airport.name,
                    MIN(Tickets.cost) AS lowest_available_price
                FROM Flights
                INNER JOIN Airlines ON Airlines.id = Flights.airline_id
                INNER JOIN Planes ON Planes.id = Flights.plane_id
                INNER JOIN Airports AS departure_airport
                    ON departure_airport.id = Flights.airport_id_departure
                INNER JOIN Airports AS arrival_airport
                    ON arrival_airport.id = Flights.airport_id_arrival
                LEFT JOIN Tickets
                    ON Tickets.flight_id = Flights.id
                    AND Tickets.sale_status = 'available'
                    AND Tickets.passenger_id IS NULL
                WHERE Flights.airport_id_departure = %s
                    AND Flights.airport_id_arrival = %s
                    AND DATE(Flights.departure_time) = %s
                GROUP BY
                    Flights.id,
                    Flights.flight_number,
                    Flights.departure_time,
                    Flights.boarding_time,
                    Airlines.name,
                    Airlines.code,
                    Planes.name,
                    Planes.code,
                    departure_airport.code,
                    departure_airport.name,
                    arrival_airport.code,
                    arrival_airport.name
                {average_price_filter}
                ORDER BY Flights.departure_time
                """,
                parameters,
            )
            return [Flight(*row) for row in cursor.fetchall()]

    def get_seat_summary(self, flight_id: str) -> list[SeatSummary]:
        """Return available seat counts and prices grouped by seat class."""
        with self._cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    Seats.class_designation,
                    COUNT(Tickets.id) AS available_seat_count,
                    AVG(Tickets.cost) AS average_available_price
                FROM Tickets
                INNER JOIN Seats ON Seats.id = Tickets.seat_id
                WHERE Tickets.flight_id = %s
                    AND Tickets.sale_status = 'available'
                    AND Tickets.passenger_id IS NULL
                GROUP BY Seats.class_designation
                ORDER BY Seats.class_designation
                """,
                (flight_id,),
            )
            return [SeatSummary(*row) for row in cursor.fetchall()]

    def list_available_seats(self, flight_id: str) -> list[AvailableSeat]:
        """Return every ticket that can currently be purchased for a flight."""
        with self._cursor() as cursor:
            cursor.execute(
                """
                SELECT Tickets.id, Seats.seat_number, Seats.class_designation, Tickets.cost
                FROM Tickets
                INNER JOIN Seats ON Seats.id = Tickets.seat_id
                WHERE Tickets.flight_id = %s
                    AND Tickets.sale_status = 'available'
                    AND Tickets.passenger_id IS NULL
                ORDER BY Seats.seat_number
                """,
                (flight_id,),
            )
            return [AvailableSeat(*row) for row in cursor.fetchall()]

    def update_passenger_contact(self, passenger_id: str, contact_information: str) -> bool:
        """Update a passenger contact record and report whether it was found."""
        with self._cursor() as cursor:
            cursor.execute(
                """
                UPDATE Passengers
                SET contact_information = %s
                WHERE id = %s
                """,
                (contact_information, passenger_id),
            )
            return cursor.rowcount == 1

    def purchase_ticket(
        self,
        ticket_id: str,
        passenger_id: str | None = None,
        contact_information: str | None = None,
    ) -> str:
        """Create or use a traveler and sell an available ticket atomically."""
        connection = self.connection_factory()
        cursor = connection.cursor(buffered=True)
        try:
            if passenger_id is None:
                if not contact_information:
                    raise ValueError("Contact information is required for a new traveler.")
                passenger_id = str(uuid4())
                cursor.execute(
                    """
                    INSERT INTO Passengers (id, contact_information)
                    VALUES (%s, %s)
                    """,
                    (passenger_id, contact_information),
                )
            cursor.execute(
                """
                UPDATE Tickets
                SET
                    passenger_id = %s,
                    sale_price = cost,
                    sale_date = CURRENT_DATE,
                    sale_status = 'sold'
                WHERE id = %s
                    AND sale_status = 'available'
                    AND passenger_id IS NULL
                """,
                (passenger_id, ticket_id),
            )
            if cursor.rowcount != 1:
                raise TicketUnavailableError("The selected seat is no longer available.")
            connection.commit()
            return passenger_id
        except BaseException:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

    def _cursor(self) -> Any:
        """Create a buffered read/write cursor that commits successful operations."""
        return _CursorContext(self.connection_factory)


class _CursorContext:
    """Keep ordinary single-statement operations concise and safely closed."""

    def __init__(self, connection_factory: ConnectionFactory) -> None:
        self.connection_factory = connection_factory
        self.connection: Any | None = None
        self.cursor: Any | None = None

    def __enter__(self) -> Any:
        self.connection = self.connection_factory()
        self.cursor = self.connection.cursor(buffered=True)
        return self.cursor

    def __exit__(self, exception_type: Any, exception: Any, traceback: Any) -> None:
        assert self.connection is not None
        assert self.cursor is not None
        if exception_type is None:
            self.connection.commit()
        else:
            self.connection.rollback()
        self.cursor.close()
        self.connection.close()
