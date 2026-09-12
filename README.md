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
