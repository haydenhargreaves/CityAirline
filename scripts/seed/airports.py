from scripts.lib.db import cursor

airports: list[dict[str, str]] = [
    {
        "name": "John F. Kennedy International Airport",
        "code": "JFK",
        "location": "New York, NY",
    },
    {
        "name": "Chicago O'Hare International Airport",
        "code": "ORD",
        "location": "Chicago, IL",
    },
    {
        "name": "Dallas Fort Worth International Airport",
        "code": "DFW",
        "location": "Dallas, TX",
    },
    {
        "name": "Hartsfield-Jackson Atlanta International Airport",
        "code": "ATL",
        "location": "Atlanta, GA",
    },
    {
        "name": "Miami International Airport",
        "code": "MIA",
        "location": "Miami, FL",
    },
    {
        "name": "Boston Logan International Airport",
        "code": "BOS",
        "location": "Boston, MA",
    },
    {
        "name": "Washington Dulles International Airport",
        "code": "IAD",
        "location": "Dulles, VA",
    },
    {
        "name": "Harry Reid International Airport",
        "code": "LAS",
        "location": "Las Vegas, NV",
    },
    {
        "name": "Phoenix Sky Harbor International Airport",
        "code": "PHX",
        "location": "Phoenix, AZ",
    },
    {
        "name": "Minneapolis-Saint Paul International Airport",
        "code": "MSP",
        "location": "Minneapolis, MN",
    },
    {
        "name": "Detroit Metropolitan Wayne County Airport",
        "code": "DTW",
        "location": "Detroit, MI",
    },
    {
        "name": "Charlotte Douglas International Airport",
        "code": "CLT",
        "location": "Charlotte, NC",
    },
    {
        "name": "Salt Lake City International Airport",
        "code": "SLC",
        "location": "Salt Lake City, UT",
    },
    {
        "name": "Toronto Pearson International Airport",
        "code": "YYZ",
        "location": "Toronto, ON, Canada",
    },
    {
        "name": "Vancouver International Airport",
        "code": "YVR",
        "location": "Vancouver, BC, Canada",
    },
    {
        "name": "Heathrow Airport",
        "code": "LHR",
        "location": "London, United Kingdom",
    },
    {
        "name": "Charles de Gaulle Airport",
        "code": "CDG",
        "location": "Paris, France",
    },
    {
        "name": "Frankfurt Airport",
        "code": "FRA",
        "location": "Frankfurt, Germany",
    },
    {
        "name": "Narita International Airport",
        "code": "NRT",
        "location": "Narita, Japan",
    },
    {
        "name": "Sydney Kingsford Smith Airport",
        "code": "SYD",
        "location": "Sydney, Australia",
    },
    {
        "name": "San Francisco International Airport",
        "code": "SFO",
        "location": "San Francisco, CA",
    },
    {
        "name": "San Diego International Airport",
        "code": "SAN",
        "location": "San Diego, CA",
    },
    {
        "name": "Portland International Airport",
        "code": "PDX",
        "location": "Portland, OR",
    },
    {
        "name": "Daniel K. Inouye International Airport",
        "code": "HNL",
        "location": "Honolulu, HI",
    },
    {
        "name": "Ted Stevens Anchorage International Airport",
        "code": "ANC",
        "location": "Anchorage, AK",
    },
    {
        "name": "George Bush Intercontinental Airport",
        "code": "IAH",
        "location": "Houston, TX",
    },
    {
        "name": "Austin-Bergstrom International Airport",
        "code": "AUS",
        "location": "Austin, TX",
    },
    {
        "name": "Nashville International Airport",
        "code": "BNA",
        "location": "Nashville, TN",
    },
    {
        "name": "Orlando International Airport",
        "code": "MCO",
        "location": "Orlando, FL",
    },
    {
        "name": "Tampa International Airport",
        "code": "TPA",
        "location": "Tampa, FL",
    },
    {
        "name": "Fort Lauderdale-Hollywood International Airport",
        "code": "FLL",
        "location": "Fort Lauderdale, FL",
    },
    {
        "name": "Philadelphia International Airport",
        "code": "PHL",
        "location": "Philadelphia, PA",
    },
    {
        "name": "Newark Liberty International Airport",
        "code": "EWR",
        "location": "Newark, NJ",
    },
    {
        "name": "Ronald Reagan Washington National Airport",
        "code": "DCA",
        "location": "Arlington, VA",
    },
    {
        "name": "Baltimore/Washington International Thurgood Marshall Airport",
        "code": "BWI",
        "location": "Baltimore, MD",
    },
    {
        "name": "Cleveland Hopkins International Airport",
        "code": "CLE",
        "location": "Cleveland, OH",
    },
    {
        "name": "John Glenn Columbus International Airport",
        "code": "CMH",
        "location": "Columbus, OH",
    },
    {
        "name": "Indianapolis International Airport",
        "code": "IND",
        "location": "Indianapolis, IN",
    },
    {
        "name": "Milwaukee Mitchell International Airport",
        "code": "MKE",
        "location": "Milwaukee, WI",
    },
    {
        "name": "St. Louis Lambert International Airport",
        "code": "STL",
        "location": "St. Louis, MO",
    },
    {
        "name": "Kansas City International Airport",
        "code": "MCI",
        "location": "Kansas City, MO",
    },
    {
        "name": "Raleigh-Durham International Airport",
        "code": "RDU",
        "location": "Raleigh, NC",
    },
    {
        "name": "Pittsburgh International Airport",
        "code": "PIT",
        "location": "Pittsburgh, PA",
    },
    {
        "name": "Mexico City International Airport",
        "code": "MEX",
        "location": "Mexico City, Mexico",
    },
    {
        "name": "Sao Paulo/Guarulhos International Airport",
        "code": "GRU",
        "location": "Sao Paulo, Brazil",
    },
    {
        "name": "Dubai International Airport",
        "code": "DXB",
        "location": "Dubai, United Arab Emirates",
    },
    {
        "name": "Singapore Changi Airport",
        "code": "SIN",
        "location": "Singapore",
    },
    {
        "name": "Incheon International Airport",
        "code": "ICN",
        "location": "Incheon, South Korea",
    },
    {
        "name": "Hong Kong International Airport",
        "code": "HKG",
        "location": "Hong Kong",
    },
    {
        "name": "Amsterdam Airport Schiphol",
        "code": "AMS",
        "location": "Amsterdam, Netherlands",
    },
]


if __name__ == "__main__":
    with cursor() as db:
        db.executemany(
            """
            INSERT INTO Airports (name, code, location)
            VALUES (%(name)s, %(code)s, %(location)s)
            """,
            airports,
        )
