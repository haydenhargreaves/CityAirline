"""Seed a full November 2026 flight schedule and its available tickets."""

from datetime import datetime, timedelta
from decimal import Decimal
from itertools import islice

from scripts.lib.db import cursor


NOVEMBER_START = datetime(2026, 11, 1)
DAYS_IN_NOVEMBER = 30
DEPARTURE_HOURS = (6, 10, 14, 18)
TICKET_BATCH_SIZE = 1_000


def batches(items: list[dict[str, object]], size: int):
    """Yield fixed-size batches without creating more ticket copies in memory."""
    iterator = iter(items)
    while batch := list(islice(iterator, size)):
        yield batch


if __name__ == "__main__":
    with cursor() as db:
        db.execute("SELECT id FROM Airports ORDER BY code")
        airport_ids = [airport_id for (airport_id,) in db.fetchall()]
        if len(airport_ids) < 2:
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

        flights = []
        for plane_index, (plane_id, plane_code) in enumerate(planes):
            for day_offset in range(DAYS_IN_NOVEMBER):
                for departure_index, hour in enumerate(DEPARTURE_HOURS):
                    # Every day has several JFK-to-ORD options for the fare-deals report.
                    # The rest rotate through the seeded airports deterministically.
                    if plane_index == 0:
                        departure_airport_id, arrival_airport_id = airport_ids[:2]
                    else:
                        departure_airport_id = airport_ids[
                            (plane_index * 3 + day_offset + departure_index) % len(airport_ids)
                        ]
                        arrival_airport_id = airport_ids[
                            (plane_index * 7 + day_offset * 2 + departure_index + 1)
                            % len(airport_ids)
                        ]
                        if arrival_airport_id == departure_airport_id:
                            arrival_airport_id = airport_ids[
                                (airport_ids.index(arrival_airport_id) + 1) % len(airport_ids)
                            ]

                    departure_time = NOVEMBER_START + timedelta(
                        days=day_offset, hours=hour
                    )
                    flights.append(
                        {
                            "flight_number": (
                                f"NOV26-{plane_code}-{day_offset + 1:02d}-{departure_index + 1}"
                            ),
                            "departure_time": departure_time,
                            "boarding_time": departure_time - timedelta(minutes=45),
                            "airline_id": airline_ids[plane_index % len(airline_ids)],
                            "plane_id": plane_id,
                            "airport_id_departure": departure_airport_id,
                            "airport_id_arrival": arrival_airport_id,
                        }
                    )

        flight_numbers = [flight["flight_number"] for flight in flights]
        placeholders = ", ".join(["%s"] * len(flight_numbers))
        db.execute(
            f"SELECT flight_number FROM Flights WHERE flight_number IN ({placeholders})",
            flight_numbers,
        )
        existing_flight_numbers = {
            flight_number for (flight_number,) in db.fetchall()
        }
        new_flights = [
            flight
            for flight in flights
            if flight["flight_number"] not in existing_flight_numbers
        ]
        if new_flights:
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
                new_flights,
            )

        db.execute(
            f"""
            SELECT id, plane_id, flight_number
            FROM Flights
            WHERE flight_number IN ({placeholders})
            """,
            flight_numbers,
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
        seats_by_plane = {plane_id: [] for plane_id in plane_ids}
        for seat_id, plane_id, class_designation in db.fetchall():
            seats_by_plane[plane_id].append((seat_id, class_designation))

        tickets = []
        for flight in flights:
            flight_id, plane_id = flight_ids[flight["flight_number"]]
            departure_index = int(flight["flight_number"][-1])
            for seat_id, class_designation in seats_by_plane[plane_id]:
                # Four distinct fares make the monthly data useful for fare comparisons.
                base_fare = Decimal("29.99") + Decimal("10.00") * (departure_index - 1)
                tickets.append(
                    {
                        "cost": base_fare + (
                            Decimal("25.00") if class_designation == "First" else Decimal("0")
                        ),
                        "sale_price": None,
                        "sale_date": None,
                        "sale_status": "available",
                        "passenger_id": None,
                        "seat_id": seat_id,
                        "flight_id": flight_id,
                    }
                )

        for ticket_batch in batches(tickets, TICKET_BATCH_SIZE):
            db.executemany(
                """
                INSERT IGNORE INTO Tickets (
                    cost, sale_price, sale_date, sale_status, passenger_id, seat_id, flight_id
                )
                VALUES (
                    %(cost)s, %(sale_price)s, %(sale_date)s, %(sale_status)s,
                    %(passenger_id)s, %(seat_id)s, %(flight_id)s
                )
                """,
                ticket_batch,
            )
