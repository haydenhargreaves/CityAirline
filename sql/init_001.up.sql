CREATE DATABASE IF NOT EXISTS city_airline;

USE city_airline;

CREATE TABLE IF NOT EXISTS Airports (
    id CHAR(36) NOT NULL PRIMARY KEY DEFAULT (UUID()),
    name VARCHAR(64) NOT NULL,
    code VARCHAR(32) NOT NULL UNIQUE,
    location VARCHAR(128) NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Airlines (
    id CHAR(36) NOT NULL PRIMARY KEY DEFAULT (UUID()),
    name VARCHAR(64) NOT NULL,
    code VARCHAR(32) NOT NULL UNIQUE,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Planes (
    id CHAR(36) NOT NULL PRIMARY KEY DEFAULT (UUID()),
    name VARCHAR(64) NOT NULL,
    code VARCHAR(32) NOT NULL UNIQUE,
    tail_number VARCHAR(6) NOT NULL UNIQUE,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Passengers (
    id CHAR(36) NOT NULL PRIMARY KEY DEFAULT (UUID()),
    contact_information VARCHAR(32) NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Seats (
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

CREATE TABLE IF NOT EXISTS Flights (
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

CREATE TABLE IF NOT EXISTS Delays (
    id CHAR(36) NOT NULL PRIMARY KEY DEFAULT (UUID()),
    duration TIME NOT NULL,
    reason VARCHAR(200) NOT NULL,
    flight_id CHAR(36) NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_delays_flight
        FOREIGN KEY (flight_id) REFERENCES Flights (id)
);

CREATE TABLE IF NOT EXISTS Tickets (
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
