# Business Requirements: City Airlines

1. **Airlines:** The system tracks various airlines. Each airline has a unique airline 
ID, a name, and an airline code. An airline may operate many flights, but each flight 
is operated by exactly one airline.
2. **Planes:** The database keeps a record of planes (aircraft). Each plane has a
unique plane ID, a name, a code, and a tail number. A plane may be assigned to many
flights over time, but each flight uses exactly one plane.
3. **Seats:** The system records the physical seating arrangement for each plane.
Each seat has a unique seat ID, a seat number, and a class designation (e.g.,
Economy, First Class). A plane contains many seats, but each seat belongs to
exactly one physical plane. A seat number must be unique within its plane.
Seats do not store a sold status; availability is specific to a flight.
4. **Airports:** The system operates across multiple airports. Each airport has a
unique airport ID, a name, an airport code, and a location. An airport can serve 
as the source or destination for many flights. 
5. **Flights:** The core of the operation is the flight schedule. Each flight has
a unique flight ID, a flight number, a departure time, and a boarding time. 
A flight ID identifies one scheduled flight instance; a flight
number may be used by multiple instances over time. Every flight is operated by
exactly one airline, uses exactly one plane, departs from exactly one source airport,
and arrives at exactly one destination airport. An airline, plane, and airport may 
be associated with many flights.
6. **Passengers:** The system records passengers. Each passenger has a unique
passenger ID and identifying contact information. A passenger may have many tickets.
7. **Tickets:** The system manages seat inventory and ticket sales through a
single Tickets table. Each ticket has a unique ticket ID and maps to exactly one
flight and exactly one seat. The assigned seat must belong to the plane used by
the flight. A ticket may be associated with one passenger. A passenger association
is required when a ticket is sold and is absent while a ticket is available. Each
ticket records the ticket cost, sale price, sale date, and status. The status
identifies whether the ticket is available, sold, cancelled, or otherwise
unavailable. A ticket's sale price and sale date are populated when it is sold.
Each flight may have many tickets, and each physical seat may be represented by
tickets on many different flights. A flight may have at most one ticket for a
given seat. Seat availability for a flight is determined by the ticket status.
8. **Delays:** Flights can occasionally be delayed. Each delay incident has a unique
delay ID, a recorded delay duration/time, and a specific reason. Every delay 
record is associated with exactly one flight. A single flight could potentially 
have multiple delay records.
9. **Telemetry:** The system requires comprehensive telemetry and logging. All 
transactions and entity updates across Airlines, Planes, Seats, Airports, Flights,
Passengers, Tickets, and Delays must have telemetry data tracked for auditing and operational 
monitoring. This is done via the created and updated records defined in the README.md file.
