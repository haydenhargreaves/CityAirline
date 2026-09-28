from datetime import time

from scripts.lib.db import cursor

delay_details = [
    (time(0, 15), "Late arrival of incoming aircraft"),
    (time(0, 25), "Weather conditions at departure airport"),
    (time(0, 40), "Air traffic control congestion"),
    (time(0, 20), "Routine maintenance inspection"),
    (time(0, 35), "Crew scheduling delay"),
    (time(0, 10), "Delayed baggage loading"),
]


if __name__ == "__main__":
    with cursor() as db:
        db.execute(
            "SELECT id FROM Flights ORDER BY flight_number LIMIT %s",
            (len(delay_details),),
        )
        flight_ids = [flight_id for (flight_id,) in db.fetchall()]

        if flight_ids:
            placeholders = ", ".join(["%s"] * len(flight_ids))
            db.execute(
                f"SELECT flight_id FROM Delays WHERE flight_id IN ({placeholders})",
                flight_ids,
            )
            delayed_flight_ids = {flight_id for (flight_id,) in db.fetchall()}

            delays = [
                {
                    "flight_id": flight_id,
                    "duration": duration,
                    "reason": reason,
                }
                for flight_id, (duration, reason) in zip(flight_ids, delay_details)
                if flight_id not in delayed_flight_ids
            ]

            if delays:
                db.executemany(
                    """
                    INSERT INTO Delays (duration, reason, flight_id)
                    VALUES (%(duration)s, %(reason)s, %(flight_id)s)
                    """,
                    delays,
                )
