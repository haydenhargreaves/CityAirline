from datetime import datetime, timedelta
from decimal import Decimal
from random import Random

from scripts.lib.db import cursor

FLIGHTS_PER_PLANE = 3


if __name__ == "__main__":
    random = Random(317)

    with cursor() as db:
        db.execute("SELECT id FROM Airports")
        airport_ids = [airport_id for (airport_id,) in db.fetchall()]
        if len(airport_ids) < 2:
            raise RuntimeError("At least two airports are required to seed flights.")

        db.execute("SELECT id FROM Airlines")
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
            for flight_index in range(FLIGHTS_PER_PLANE):
                departure_airport_id, arrival_airport_id = random.sample(airport_ids, 2)
                departure_time = datetime(2026, 10, 1, 8, 0) + timedelta(
                    days=plane_index,
                    hours=flight_index * 5,
                )
                flights.append(
                    {
                        "flight_number": f"SEED-{plane_code}-{flight_index + 1:02d}",
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
                    flight_number,
                    departure_time,
                    boarding_time,
                    airline_id,
                    plane_id,
                    airport_id_departure,
                    airport_id_arrival
                )
                VALUES (
                    %(flight_number)s,
                    %(departure_time)s,
                    %(boarding_time)s,
                    %(airline_id)s,
                    %(plane_id)s,
                    %(airport_id_departure)s,
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
            f"SELECT id, plane_id FROM Seats WHERE plane_id IN ({placeholders})",
            plane_ids,
        )
        seats_by_plane = {plane_id: [] for plane_id in plane_ids}
        for seat_id, plane_id in db.fetchall():
            seats_by_plane[plane_id].append(seat_id)

        tickets = []
        for flight in flights:
            flight_id, plane_id = flight_ids[flight["flight_number"]]
            for seat_id in seats_by_plane[plane_id]:
                tickets.append(
                    {
                        "cost": Decimal("49.99"),
                        "sale_price": None,
                        "sale_date": None,
                        "sale_status": "available",
                        "passenger_id": None,
                        "seat_id": seat_id,
                        "flight_id": flight_id,
                    }
                )

        db.executemany(
            """
            INSERT IGNORE INTO Tickets (
                cost,
                sale_price,
                sale_date,
                sale_status,
                passenger_id,
                seat_id,
                flight_id
            )
            VALUES (
                %(cost)s,
                %(sale_price)s,
                %(sale_date)s,
                %(sale_status)s,
                %(passenger_id)s,
                %(seat_id)s,
                %(flight_id)s
            )
            """,
            tickets,
        )
