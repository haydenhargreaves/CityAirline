-- Run this script as root after sql/init_001.up.sql.

CREATE USER IF NOT EXISTS 'city_airline_client'@'%' IDENTIFIED BY 'root';

GRANT SELECT ON city_airline.Airlines TO 'city_airline_client'@'%';
GRANT SELECT ON city_airline.Airports TO 'city_airline_client'@'%';
GRANT SELECT ON city_airline.Planes TO 'city_airline_client'@'%';
GRANT SELECT ON city_airline.Flights TO 'city_airline_client'@'%';
GRANT SELECT ON city_airline.Seats TO 'city_airline_client'@'%';
GRANT SELECT ON city_airline.Tickets TO 'city_airline_client'@'%';
GRANT SELECT ON city_airline.Passengers TO 'city_airline_client'@'%';
GRANT INSERT, UPDATE ON city_airline.Passengers TO 'city_airline_client'@'%';
GRANT UPDATE ON city_airline.Tickets TO 'city_airline_client'@'%';

CREATE USER IF NOT EXISTS 'city_airline_data_entry'@'%' IDENTIFIED BY 'root';

GRANT SELECT, INSERT, UPDATE ON city_airline.Airlines TO 'city_airline_data_entry'@'%';
GRANT SELECT, INSERT, UPDATE ON city_airline.Airports TO 'city_airline_data_entry'@'%';
GRANT SELECT, INSERT, UPDATE ON city_airline.Planes TO 'city_airline_data_entry'@'%';
GRANT SELECT, INSERT, UPDATE ON city_airline.Seats TO 'city_airline_data_entry'@'%';
GRANT SELECT, INSERT, UPDATE ON city_airline.Flights TO 'city_airline_data_entry'@'%';
GRANT SELECT, INSERT, UPDATE ON city_airline.Tickets TO 'city_airline_data_entry'@'%';

FLUSH PRIVILEGES;
