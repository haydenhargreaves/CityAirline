# CS317 Final Project: Application Plan

## 1. Who Uses It and Why

City Airline customers use the application to find flights between two airports,
compare available seats and prices, and purchase tickets. The application provides a
Streamlit interface for browsing flights and completing bookings without allowing
customers to alter airline scheduling data.

## 2. Seven Features

1. **Search:** Customers can search for flights by departure airport, arrival airport,
   and travel date.
2. **Combine tables:** Customers can view matching flight details that combine
   `Flights`, `Airlines`, `Airports`, and `Planes`, including the airline name, flight
   number, departure time, and airport names.
3. **Summary:** Customers can view a selected flight's seat availability and average
   price grouped by seat class.
4. **Subquery:** Customers can find flight options with available-seat prices below
   the average available-seat price for the same searched route.
5. **Add:** Customers can create a passenger/traveler profile with their contact
   information before booking.
6. **Change:** Customers can update the contact information in their passenger
   profile.
7. **Transaction:** Customers can purchase an available seat; for a first-time
   customer, the application creates their passenger record and marks the selected
   ticket as sold together.

## 3. Transaction

During checkout, the application will create a `Passengers` record for a first-time
customer and update the selected available `Tickets` record with that passenger, the
sale price, sale date, and a `sold` status. These changes will occur in one
transaction.

To demonstrate failure, the application will simulate the selected ticket being sold
after the customer chooses it but before checkout. The ticket update will find no
available ticket, so the application will roll back the newly created passenger
record and display a message that the seat is no longer available.

## 4. GRANT List

Two MySQL accounts will use least-privilege permissions.

### Client application account: `city_airline_client`

- `SELECT` on `Airlines`, `Airports`, `Planes`, `Flights`, `Seats`, `Tickets`, and
  `Passengers`, to search flights, display flight and seat details, show prices, and
  display passenger information.
- `INSERT` on `Passengers`, to create a traveler profile and register a first-time
  customer during checkout.
- `UPDATE` on `Passengers`, to allow customers to change their contact information.
- `UPDATE` on `Tickets`, to mark an available seat as sold during checkout.

This account will not have permission to create or modify airlines, airports, planes,
seats, or flights.

### Flight-data account: `city_airline_data_entry`

- `SELECT`, `INSERT`, and `UPDATE` on `Airlines`, `Airports`, `Planes`, `Seats`,
  `Flights`, and `Tickets`.
- This account is used manually by airline staff to enter and maintain airports,
  aircraft, seats, scheduled flights, and the available ticket inventory for each
  flight.

Neither account receives `DELETE` permission because no planned feature requires it.

## 5. Constraint and Refused Operation

The application will demonstrate the `uq_tickets_flight_seat` constraint on
`Tickets`, which prevents more than one ticket for the same seat on the same flight.
The flight-data account will attempt to insert a second ticket with an existing
`(flight_id, seat_id)` pair, and MySQL will refuse the duplicate.

The application will also demonstrate least privilege by attempting to insert a new
flight while connected as `city_airline_client`. MySQL will refuse the operation
because that account does not have `INSERT` permission on `Flights`.

## 6. Language, Interface, and Team Roles

The application will be written in Python with a Streamlit web interface and a MySQL database.

- **Preston:** Build the Streamlit screens for flight search, results,
  seat selection, and checkout.
- **Hayden:** Implement MySQL queries, transactions, accounts, GRANT
  statements, and constraint demonstrations.
- **Cody:** Prepare schema and seed data, test the application, write
  documentation, and prepare the presentation/demo.
