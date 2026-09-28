from datetime import date
from decimal import Decimal

from scripts.lib.db import cursor

TICKETS_TO_SELL = 20


if __name__ == "__main__":
    with cursor() as db:
        db.execute(
            """
            SELECT Passengers.id
            FROM Passengers
            LEFT JOIN Tickets
                ON Tickets.passenger_id = Passengers.id
                AND Tickets.sale_status = 'sold'
            WHERE Tickets.id IS NULL
            ORDER BY Passengers.id
            LIMIT %s
            """,
            (TICKETS_TO_SELL,),
        )
        passenger_ids = [passenger_id for (passenger_id,) in db.fetchall()]

        db.execute(
            """
            SELECT id
            FROM Tickets
            WHERE sale_status = 'available' AND passenger_id IS NULL
            ORDER BY flight_id, seat_id
            LIMIT %s
            """,
            (len(passenger_ids),),
        )
        ticket_ids = [ticket_id for (ticket_id,) in db.fetchall()]

        sales = [
            {
                "ticket_id": ticket_id,
                "passenger_id": passenger_id,
                "sale_price": Decimal("79.99"),
                "sale_date": date(2026, 9, 28),
            }
            for passenger_id, ticket_id in zip(passenger_ids, ticket_ids)
        ]

        if sales:
            db.executemany(
                """
                UPDATE Tickets
                SET
                    passenger_id = %(passenger_id)s,
                    sale_price = %(sale_price)s,
                    sale_date = %(sale_date)s,
                    sale_status = 'sold'
                WHERE
                    id = %(ticket_id)s
                    AND sale_status = 'available'
                    AND passenger_id IS NULL
                """,
                sales,
            )
