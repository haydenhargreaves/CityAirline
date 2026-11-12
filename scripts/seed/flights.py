"""Seed every directed airport route for every day in November 2026."""

from collections.abc import Iterable, Iterator
from datetime import datetime, timedelta
from decimal import Decimal
from itertools import islice
from typing import Any

from scripts.lib.db import cursor


NOVEMBER_START = datetime(2026, 11, 1)
DAYS_IN_NOVEMBER = 30
FLIGHT_BATCH_SIZE = 1_000
TICKET_BATCH_SIZE = 1_000


def batches(items: Iterable[dict[str, Any]], size: int) -> Iterator[list[dict[str, Any]]]:
    """Yield fixed-size batches without retaining all tickets in memory."""
    iterator = iter(items)
    while batch := list(islice(iterator, size)):
        yield batch


def ticket_rows(
    flights: Iterable[dict[str, Any]],
    flight_ids: dict[str, tuple[str, str]],
    seats_by_plane: dict[str, list[tuple[str, str]]],
) -> Iterator[dict[str, Any]]:
    """Create one bookable ticket per new route without overloading local MySQL."""
    for flight in flights:
        flight_id, plane_id = flight_ids[flight["flight_number"]]
        route_fare = Decimal("29.99") + Decimal("10.00") * (
            int(flight["route_index"]) % 4
        )
        seat_id, class_designation = seats_by_plane[plane_id][0]
        yield {
            "cost": route_fare
            + (Decimal("25.00") if class_designation == "First" else Decimal("0")),
            "sale_price": None,
            "sale_date": None,
            "sale_status": "available",
            "passenger_id": None,
            "seat_id": seat_id,
            "flight_id": flight_id,
        }


if __name__ == "__main__":
    with cursor() as db:
        db.execute("SELECT id, code FROM Airports ORDER BY code")
        airports = db.fetchall()
        if len(airports) < 2:
            raise RuntimeError("At least two airports are required to seed flights.")

        db.execute("SELECT id FROM Airlines ORDER BY code")
        airline_ids = [airline_id for (airline_id,) in db.fetchall()]
        if not airline_ids:
            raise RuntimeError("At least one airline is required to seed flights.")

        db.execute(
            """
            SELECT DISTINCT Planes.id, Planes.code
            FROM Planes
            INNER JOIN Seats ON Seats.plane_id = Planes.id
            ORDER BY Planes.code
            """
        )
        planes = db.fetchall()
        if not planes:
            raise RuntimeError("At least one plane with seats is required to seed flights.")

        flights: list[dict[str, Any]] = []
        for day_offset in range(DAYS_IN_NOVEMBER):
            for departure_index, (departure_airport_id, _) in enumerate(airports):
                for arrival_index, (arrival_airport_id, _) in enumerate(airports):
                    if departure_index == arrival_index:
                        continue
                    route_index = departure_index * len(airports) + arrival_index
                    plane_id, _ = planes[route_index % len(planes)]
                    departure_time = NOVEMBER_START + timedelta(
                        days=day_offset,
                        hours=5 + route_index % 16,
                        minutes=(route_index * 7) % 60,
                    )
                    flights.append(
                        {
                            # Airport indexes keep the identifier well below the 32-character limit.
                            "flight_number": (
                                f"NOV26-{day_offset + 1:02d}-{departure_index:02d}-{arrival_index:02d}"
                            ),
                            "departure_time": departure_time,
                            "boarding_time": departure_time - timedelta(minutes=45),
                            "airline_id": airline_ids[route_index % len(airline_ids)],
                            "plane_id": plane_id,
                            "airport_id_departure": departure_airport_id,
                            "airport_id_arrival": arrival_airport_id,
                            "route_index": route_index,
                        }
                    )

        db.execute(
            """
            SELECT flight_number
            FROM Flights
            WHERE departure_time >= %s AND departure_time < %s
            """,
            (NOVEMBER_START, datetime(2026, 12, 1)),
        )
        existing_flight_numbers = {
            flight_number for (flight_number,) in db.fetchall()
        }
        new_flights = [
            flight
            for flight in flights
            if flight["flight_number"] not in existing_flight_numbers
        ]

        for flight_batch in batches(new_flights, FLIGHT_BATCH_SIZE):
            db.executemany(
                """
                INSERT INTO Flights (
                    flight_number, departure_time, boarding_time, airline_id, plane_id,
                    airport_id_departure, airport_id_arrival
                )
                VALUES (
                    %(flight_number)s, %(departure_time)s, %(boarding_time)s,
                    %(airline_id)s, %(plane_id)s, %(airport_id_departure)s,
                    %(airport_id_arrival)s
                )
                """,
                flight_batch,
            )

        db.execute(
            """
            SELECT id, plane_id, flight_number
            FROM Flights
            WHERE departure_time >= %s AND departure_time < %s
            """,
            (NOVEMBER_START, datetime(2026, 12, 1)),
        )
        flight_ids = {
            flight_number: (flight_id, plane_id)
            for flight_id, plane_id, flight_number in db.fetchall()
        }

        plane_ids = [plane_id for plane_id, _ in planes]
        placeholders = ", ".join(["%s"] * len(plane_ids))
        db.execute(
            f"SELECT id, plane_id, class_designation FROM Seats WHERE plane_id IN ({placeholders})",
            plane_ids,
        )
        seats_by_plane: dict[str, list[tuple[str, str]]] = {
            plane_id: [] for plane_id in plane_ids
        }
        for seat_id, plane_id, class_designation in db.fetchall():
            seats_by_plane[plane_id].append((seat_id, class_designation))

        for ticket_batch in batches(
            ticket_rows(new_flights, flight_ids, seats_by_plane), TICKET_BATCH_SIZE
        ):
            db.executemany(
                """
                INSERT INTO Tickets (
                    cost, sale_price, sale_date, sale_status, passenger_id, seat_id, flight_id
                )
                VALUES (
                    %(cost)s, %(sale_price)s, %(sale_date)s, %(sale_status)s,
                    %(passenger_id)s, %(seat_id)s, %(flight_id)s
                )
                """,
                ticket_batch,
            )
