-- CS317 Milestone 2: City Airline working database
-- This script is self-contained and can be run repeatedly.

DROP DATABASE IF EXISTS city_airline;

CREATE DATABASE city_airline;

USE city_airline;

CREATE TABLE Airports (
    id CHAR(36) NOT NULL PRIMARY KEY DEFAULT (UUID()),
    name VARCHAR(64) NOT NULL,
    code VARCHAR(32) NOT NULL UNIQUE,
    location VARCHAR(128) NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE Airlines (
    id CHAR(36) NOT NULL PRIMARY KEY DEFAULT (UUID()),
    name VARCHAR(64) NOT NULL,
    code VARCHAR(32) NOT NULL UNIQUE,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE Planes (
    id CHAR(36) NOT NULL PRIMARY KEY DEFAULT (UUID()),
    name VARCHAR(64) NOT NULL,
    code VARCHAR(32) NOT NULL UNIQUE,
    tail_number VARCHAR(6) NOT NULL UNIQUE,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE Passengers (
    id CHAR(36) NOT NULL PRIMARY KEY DEFAULT (UUID()),
    contact_information VARCHAR(32) NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE Seats (
    id CHAR(36) NOT NULL PRIMARY KEY DEFAULT (UUID()),
    seat_number INT NOT NULL,
    class_designation VARCHAR(10) NOT NULL,
    plane_id CHAR(36) NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_seats_plane
        FOREIGN KEY (plane_id) REFERENCES Planes (id),
    UNIQUE KEY uq_seats_plane_seat_number (plane_id, seat_number)
);

CREATE TABLE Flights (
    id CHAR(36) NOT NULL PRIMARY KEY DEFAULT (UUID()),
    flight_number VARCHAR(32) NOT NULL,
    departure_time DATETIME NOT NULL,
    boarding_time DATETIME NOT NULL,
    airline_id CHAR(36) NOT NULL,
    plane_id CHAR(36) NOT NULL,
    airport_id_departure CHAR(36) NOT NULL,
    airport_id_arrival CHAR(36) NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_flights_airline
        FOREIGN KEY (airline_id) REFERENCES Airlines (id),
    CONSTRAINT fk_flights_plane
        FOREIGN KEY (plane_id) REFERENCES Planes (id),
    CONSTRAINT fk_flights_departure_airport
        FOREIGN KEY (airport_id_departure) REFERENCES Airports (id),
    CONSTRAINT fk_flights_arrival_airport
        FOREIGN KEY (airport_id_arrival) REFERENCES Airports (id)
);

CREATE TABLE Delays (
    id CHAR(36) NOT NULL PRIMARY KEY DEFAULT (UUID()),
    duration TIME NOT NULL,
    reason VARCHAR(200) NOT NULL,
    flight_id CHAR(36) NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_delays_flight
        FOREIGN KEY (flight_id) REFERENCES Flights (id)
);

CREATE TABLE Tickets (
    id CHAR(36) NOT NULL PRIMARY KEY DEFAULT (UUID()),
    cost DECIMAL(4, 2) NOT NULL,
    sale_price DECIMAL(4, 2) NULL,
    sale_date DATE NULL,
    sale_status VARCHAR(45) NOT NULL,
    passenger_id CHAR(36) NULL,
    seat_id CHAR(36) NOT NULL,
    flight_id CHAR(36) NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_tickets_passenger
        FOREIGN KEY (passenger_id) REFERENCES Passengers (id),
    CONSTRAINT fk_tickets_seat
        FOREIGN KEY (seat_id) REFERENCES Seats (id),
    CONSTRAINT fk_tickets_flight
        FOREIGN KEY (flight_id) REFERENCES Flights (id),
    UNIQUE KEY uq_tickets_flight_seat (flight_id, seat_id)
);

INSERT INTO Airports (name, code, location) VALUES
    ('Seattle-Tacoma International Airport', 'SEA', 'Seattle, WA'),
    ('Los Angeles International Airport', 'LAX', 'Los Angeles, CA'),
    ('Denver International Airport', 'DEN', 'Denver, CO');

INSERT INTO Airlines (name, code) VALUES
    ('City Airlines', 'CTA'),
    ('Metro Air', 'MTA');

INSERT INTO Planes (name, code, tail_number) VALUES
    ('City Hopper', 'CH100', 'N10001'),
    ('Metro Jet', 'MJ200', 'N20002');

INSERT INTO Passengers (contact_information) VALUES
    ('alex@example.com'),
    ('jamie@example.com');

INSERT INTO Seats (seat_number, class_designation, plane_id) VALUES
    (1, 'First', (SELECT id FROM Planes WHERE code = 'CH100')),
    (2, 'Economy', (SELECT id FROM Planes WHERE code = 'CH100')),
    (3, 'Economy', (SELECT id FROM Planes WHERE code = 'CH100')),
    (4, 'Economy', (SELECT id FROM Planes WHERE code = 'CH100')),
    (1, 'First', (SELECT id FROM Planes WHERE code = 'MJ200')),
    (2, 'Economy', (SELECT id FROM Planes WHERE code = 'MJ200')),
    (3, 'Economy', (SELECT id FROM Planes WHERE code = 'MJ200')),
    (4, 'Economy', (SELECT id FROM Planes WHERE code = 'MJ200'));

INSERT INTO Flights (
    flight_number,
    departure_time,
    boarding_time,
    airline_id,
    plane_id,
    airport_id_departure,
    airport_id_arrival
) VALUES
    (
        'CTA101',
        '2026-10-01 09:00:00',
        '2026-10-01 08:20:00',
        (SELECT id FROM Airlines WHERE code = 'CTA'),
        (SELECT id FROM Planes WHERE code = 'CH100'),
        (SELECT id FROM Airports WHERE code = 'SEA'),
        (SELECT id FROM Airports WHERE code = 'LAX')
    ),
    (
        'MTA202',
        '2026-10-02 14:30:00',
        '2026-10-02 13:50:00',
        (SELECT id FROM Airlines WHERE code = 'MTA'),
        (SELECT id FROM Planes WHERE code = 'MJ200'),
        (SELECT id FROM Airports WHERE code = 'LAX'),
        (SELECT id FROM Airports WHERE code = 'DEN')
    );

INSERT INTO Delays (duration, reason, flight_id) VALUES
    (
        '00:25:00',
        'Late arrival of incoming aircraft',
        (SELECT id FROM Flights WHERE flight_number = 'MTA202')
    );

INSERT INTO Tickets (
    cost,
    sale_price,
    sale_date,
    sale_status,
    passenger_id,
    seat_id,
    flight_id
) VALUES
    (42.00, 79.99, '2026-09-10', 'sold', (SELECT id FROM Passengers WHERE contact_information = 'alex@example.com'), (SELECT Seats.id FROM Seats INNER JOIN Planes ON Seats.plane_id = Planes.id WHERE Planes.code = 'CH100' AND Seats.seat_number = 1), (SELECT id FROM Flights WHERE flight_number = 'CTA101')),
    (32.00, NULL, NULL, 'available', NULL, (SELECT Seats.id FROM Seats INNER JOIN Planes ON Seats.plane_id = Planes.id WHERE Planes.code = 'CH100' AND Seats.seat_number = 2), (SELECT id FROM Flights WHERE flight_number = 'CTA101')),
    (32.00, 59.99, '2026-09-11', 'sold', (SELECT id FROM Passengers WHERE contact_information = 'jamie@example.com'), (SELECT Seats.id FROM Seats INNER JOIN Planes ON Seats.plane_id = Planes.id WHERE Planes.code = 'CH100' AND Seats.seat_number = 3), (SELECT id FROM Flights WHERE flight_number = 'CTA101')),
    (32.00, NULL, NULL, 'available', NULL, (SELECT Seats.id FROM Seats INNER JOIN Planes ON Seats.plane_id = Planes.id WHERE Planes.code = 'CH100' AND Seats.seat_number = 4), (SELECT id FROM Flights WHERE flight_number = 'CTA101')),
    (45.00, 89.99, '2026-09-12', 'sold', (SELECT id FROM Passengers WHERE contact_information = 'alex@example.com'), (SELECT Seats.id FROM Seats INNER JOIN Planes ON Seats.plane_id = Planes.id WHERE Planes.code = 'MJ200' AND Seats.seat_number = 1), (SELECT id FROM Flights WHERE flight_number = 'MTA202')),
    (35.00, NULL, NULL, 'available', NULL, (SELECT Seats.id FROM Seats INNER JOIN Planes ON Seats.plane_id = Planes.id WHERE Planes.code = 'MJ200' AND Seats.seat_number = 2), (SELECT id FROM Flights WHERE flight_number = 'MTA202')),
    (35.00, 64.99, '2026-09-13', 'cancelled', (SELECT id FROM Passengers WHERE contact_information = 'jamie@example.com'), (SELECT Seats.id FROM Seats INNER JOIN Planes ON Seats.plane_id = Planes.id WHERE Planes.code = 'MJ200' AND Seats.seat_number = 3), (SELECT id FROM Flights WHERE flight_number = 'MTA202')),
    (35.00, NULL, NULL, 'available', NULL, (SELECT Seats.id FROM Seats INNER JOIN Planes ON Seats.plane_id = Planes.id WHERE Planes.code = 'MJ200' AND Seats.seat_number = 4), (SELECT id FROM Flights WHERE flight_number = 'MTA202'));

-- Verification queries
SHOW TABLES;
SHOW CREATE TABLE Flights;
SHOW CREATE TABLE Tickets;

SELECT
    Flights.flight_number,
    Airlines.name AS airline,
    Planes.name AS plane,
    departure_airport.code AS departure_airport,
    arrival_airport.code AS arrival_airport,
    Flights.departure_time
FROM Flights
INNER JOIN Airlines ON Flights.airline_id = Airlines.id
INNER JOIN Planes ON Flights.plane_id = Planes.id
INNER JOIN Airports AS departure_airport ON Flights.airport_id_departure = departure_airport.id
INNER JOIN Airports AS arrival_airport ON Flights.airport_id_arrival = arrival_airport.id;

SELECT
    Flights.flight_number,
    COUNT(Tickets.id) AS ticket_count,
    SUM(Tickets.sale_status = 'sold') AS sold_ticket_count,
    SUM(Tickets.sale_status = 'available') AS available_ticket_count
FROM Flights
LEFT JOIN Tickets ON Tickets.flight_id = Flights.id
GROUP BY Flights.id, Flights.flight_number;

SELECT
    Tickets.sale_status,
    Passengers.contact_information,
    Seats.seat_number,
    Flights.flight_number
FROM Tickets
LEFT JOIN Passengers ON Tickets.passenger_id = Passengers.id
INNER JOIN Seats ON Tickets.seat_id = Seats.id
INNER JOIN Flights ON Tickets.flight_id = Flights.id;
