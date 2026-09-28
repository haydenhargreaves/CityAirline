from scripts.lib.db import cursor

planes = [
    {
        "name": "City Hopper 100",
        "code": "CA100",
        "tail_number": "N10001",
        "seat_count": 64,
        "first_class_count": 8,
    },
    {
        "name": "City Hopper 200",
        "code": "CA200",
        "tail_number": "N10002",
        "seat_count": 72,
        "first_class_count": 12,
    },
    {
        "name": "City Jet 300",
        "code": "CJ300",
        "tail_number": "N10003",
        "seat_count": 80,
        "first_class_count": 16,
    },
    {
        "name": "City Jet 400",
        "code": "CJ400",
        "tail_number": "N10004",
        "seat_count": 88,
        "first_class_count": 20,
    },
    {
        "name": "City Cruiser 500",
        "code": "CC500",
        "tail_number": "N10005",
        "seat_count": 96,
        "first_class_count": 24,
    },
    {
        "name": "City Cruiser 600",
        "code": "CC600",
        "tail_number": "N10006",
        "seat_count": 100,
        "first_class_count": 24,
    },
]


if __name__ == "__main__":
    with cursor() as db:
        db.executemany(
            """
            INSERT IGNORE INTO Planes (name, code, tail_number)
            VALUES (%(name)s, %(code)s, %(tail_number)s)
            """,
            planes,
        )

        plane_codes = [plane["code"] for plane in planes]
        placeholders = ", ".join(["%s"] * len(plane_codes))
        db.execute(
            f"SELECT id, code FROM Planes WHERE code IN ({placeholders})",
            plane_codes,
        )
        plane_ids = {code: plane_id for plane_id, code in db.fetchall()}

        seats = []
        for plane in planes:
            for seat_number in range(1, plane["seat_count"] + 1):
                seats.append(
                    {
                        "plane_id": plane_ids[plane["code"]],
                        "seat_number": seat_number,
                        "class_designation": (
                            "First"
                            if seat_number <= plane["first_class_count"]
                            else "Economy"
                        ),
                    }
                )

        db.executemany(
            """
            INSERT IGNORE INTO Seats (plane_id, seat_number, class_designation)
            VALUES (%(plane_id)s, %(seat_number)s, %(class_designation)s)
            """,
            seats,
        )
