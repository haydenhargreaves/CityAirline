# City Airline

A project for CS317: Database and file systems.


### Naming Convention

A document defining the naming convention is in [docs/](https://github.com/haydenhargreaves/CityAirline/blob/master/docs/naming.md). Any SQL written and any 
tables created are expected to follow the guidelines defined in this document.



### Primary Key Data Types

I do not believe in "auto incrementing integers" as the *best* type for a tables
primary key. I am a strong believer in the power of UUID/GUIDs. We will use them
for our tables primary keys. In MySQL the syntax is as follows:

```sql
-- Create a table with a UUID as a key.
CREATE TABLE table (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    ...
);
```

Using the `DEFAULT` keyword means that you never need to create the ID when you 
create a record, it will be generated automatically.


### Telemetry Data

To keep us "sane" during this project each table will contain "telemetry data"
(I made that term up, but I think it suits the need). Each table should contain 
the following columns:

```sql

CREATE TABLE table (
    ...

    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP
);
```

As you notice, each column has a `DEFAULT` set, so they do not need to be created
when records are added. The created timestamp will be set and left alone each time
a record is created. However, the `updated` field will be NULL by default. Once the 
record is updated, the `updated` field will be set to the current timestamp when it 
was updated.

This will provide all of the data we may need to keep track of changes and creations
in the database! **AND** it requires no extra work when creating records!

## Running the Project

Prerequisites: Python 3.12+, Docker Desktop, and the MySQL command-line client.

1. Start MySQL:

```bash
docker compose up -d
```

2. Create the database tables:

```bash
mysql -u root -p < sql/init_001.up.sql
```

3. Create the limited application accounts by replacing the password placeholders
in `sql/application_accounts.sql`, then run it as root:

```bash
mysql -u root -p < sql/application_accounts.sql
```

4. Configure the `MYSQL_*` variables with the root account only while running
the seed scripts, then install dependencies and seed the database:

```bash
pip install -r requirements.txt
python -m scripts.seed
```

5. Configure `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, and
`MYSQL_DATABASE` for `city_airline_client`. Do not run the Streamlit app as
root. See [.env.example](.env.example).

6. Start the application:

```bash
streamlit run app.py
```

The search controls require an exact seeded route and date. The first three seeded
flights share a route and date so the Fare Deals tab can demonstrate its report.

## Python Scripts

To run the python seeding scripts, they are to be run in this way:

```bash
python -m scripts.seed.script_name
```

The entire database can be seeded by running the following command:

```bash
python -m scripts.seed
```

The Streamlit app supports flight search, seat selection, booking, and passenger
contact updates.

## Application Features

| User action | Requirement |
| --- | --- |
| Search Flights | Search (`WHERE`) |
| View Flight Details | Combine tables (`JOIN`) |
| View Seat Summary | Summary (`GROUP BY`) |
| Find Fare Deals | Subquery |
| Create Passenger Profile | Add (`INSERT`) |
| Update Passenger Contact | Change (`UPDATE`) |
| Purchase Ticket | Transaction |

## Team Roles

| Team member | Responsibility |
| --- | --- |
| Preston | Streamlit application and interface |
| Hayden | Queries, transactions, accounts, and grants |
| Cody | Schema, seed data, testing, documentation, and presentation |

## AI Use

AI was used for permitted application interface and boilerplate assistance.
