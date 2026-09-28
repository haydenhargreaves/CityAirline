from scripts.lib.db import cursor

airlines: list[dict[str, str]] = [
    {
        "name": "American Airlines",
        "code": "AA",
    },
    {
        "name": "Delta Air Lines",
        "code": "DL",
    },
    {
        "name": "United Airlines",
        "code": "UA",
    },
    {
        "name": "Southwest Airlines",
        "code": "WN",
    },
    {
        "name": "Alaska Airlines",
        "code": "AS",
    },
    {
        "name": "JetBlue Airways",
        "code": "B6",
    },
    {
        "name": "Air Canada",
        "code": "AC",
    },
    {
        "name": "British Airways",
        "code": "BA",
    },
    {
        "name": "Lufthansa",
        "code": "LH",
    },
    {
        "name": "Air France",
        "code": "AF",
    },
]


if __name__ == "__main__":
    with cursor() as db:
        db.executemany(
            """
            INSERT INTO Airlines (name, code)
            VALUES (%(name)s, %(code)s)
            """,
            airlines,
        )
