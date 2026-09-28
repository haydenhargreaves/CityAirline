from scripts.lib.db import cursor

passengers: list[dict[str, str]] = [
    {"contact_information": "alex.morgan@example.com"},
    {"contact_information": "jamie.lee@example.com"},
    {"contact_information": "taylor.smith@example.com"},
    {"contact_information": "jordan.brown@example.com"},
    {"contact_information": "casey.wilson@example.com"},
    {"contact_information": "morgan.davis@example.com"},
    {"contact_information": "riley.miller@example.com"},
    {"contact_information": "avery.thomas@example.com"},
    {"contact_information": "cameron.jackson@example.com"},
    {"contact_information": "quinn.white@example.com"},
    {"contact_information": "parker.harris@example.com"},
    {"contact_information": "reese.martin@example.com"},
    {"contact_information": "blake.thompson@example.com"},
    {"contact_information": "drew.garcia@example.com"},
    {"contact_information": "skyler.martinez@example.com"},
    {"contact_information": "hayden.robinson@example.com"},
    {"contact_information": "rowan.clark@example.com"},
    {"contact_information": "emerson.lewis@example.com"},
    {"contact_information": "finley.walker@example.com"},
    {"contact_information": "sawyer.hall@example.com"},
]


if __name__ == "__main__":
    with cursor() as db:
        db.executemany(
            """
            INSERT INTO Passengers (contact_information)
            VALUES (%(contact_information)s)
            """,
            passengers,
        )
