"""Streamlit screen functions for the City Airline application."""

from datetime import date

import streamlit as st

from app.data import (
    CityAirlineData,
    TicketUnavailableError,
)
from app.models import Airport, Flight, FlightSearchResult


def show_database_error(error: Exception, fallback: str) -> None:
    """Display expected database failures without exposing raw MySQL errors."""
    error_number = getattr(error, "errno", None)
    messages = {
        1062: "This record already exists.",
        1142: "You do not have permission to perform this operation.",
        1452: "The selected related record no longer exists.",
    }
    st.error(messages.get(error_number, fallback))


def airport_controls(airports: list[Airport], form_key: str) -> tuple[Airport, Airport, date]:
    """Render shared route controls inside a form."""
    airport_by_label = {airport.label: airport for airport in airports}
    labels = list(airport_by_label)
    departure_label = st.selectbox("From", labels, key=f"{form_key}_from")
    arrival_labels = [label for label in labels if label != departure_label]
    arrival_label = st.selectbox("To", arrival_labels, key=f"{form_key}_to")
    travel_date = st.date_input("Travel date", value=date.today(), key=f"{form_key}_date")
    return airport_by_label[departure_label], airport_by_label[arrival_label], travel_date


def selected_flight(data: CityAirlineData) -> Flight | None:
    """Return details for the flight selected in the search workflow."""
    flight_id = st.session_state.get("selected_flight_id")
    return data.get_flight_details(flight_id) if flight_id else None


def show_search(data: CityAirlineData, airports: list[Airport]) -> None:
    """Render the required route/date search feature."""
    st.subheader("1. Search Flights")
    with st.form("search_flights"):
        departure, arrival, travel_date = airport_controls(airports, "search")
        submitted = st.form_submit_button("Search flights")

    if submitted:
        try:
            st.session_state["route_results"] = data.search_route(
                departure.id, arrival.id, travel_date
            )
            st.session_state.pop("selected_flight_id", None)
        except Exception as error:
            show_database_error(error, "Unable to search for flights right now.")

    results: list[FlightSearchResult] = st.session_state.get("route_results", [])
    if not results:
        if "route_results" in st.session_state:
            st.info("No flights matched that route and date.")
        return

    st.dataframe(
        [
            {"Flight": result.flight_number, "Departure": result.departure_time}
            for result in results
        ],
        hide_index=True,
        use_container_width=True,
    )
    flight = st.selectbox("Select a flight", results, format_func=lambda item: item.label)
    st.session_state["selected_flight_id"] = flight.id
    st.success("Flight selected. Open the other tabs to view details or book a seat.")


def show_flight_details(data: CityAirlineData) -> None:
    """Render the required joined flight-detail feature."""
    st.subheader("2. View Flight Details")
    flight = selected_flight(data)
    if flight is None:
        st.info("Search for and select a flight first.")
        return
    st.dataframe(
        [
            {
                "Flight": flight.flight_number,
                "Airline": f"{flight.airline_name} ({flight.airline_code})",
                "Plane": f"{flight.plane_name} ({flight.plane_code})",
                "Departure airport": f"{flight.departure_airport_code} - {flight.departure_airport_name}",
                "Arrival airport": f"{flight.arrival_airport_code} - {flight.arrival_airport_name}",
                "Departure": flight.departure_time,
                "Boarding": flight.boarding_time,
                "Lowest available fare": flight.lowest_available_price,
            }
        ],
        hide_index=True,
        use_container_width=True,
    )


def show_seat_summary(data: CityAirlineData) -> None:
    """Render the required grouped seat-summary feature."""
    st.subheader("3. View Seat Summary")
    flight = selected_flight(data)
    if flight is None:
        st.info("Search for and select a flight first.")
        return
    try:
        summaries = data.get_seat_summary(flight.id)
    except Exception as error:
        show_database_error(error, "Unable to load seat availability.")
        return
    if not summaries:
        st.info("No available seats remain on this flight.")
        return
    st.dataframe(
        [
            {
                "Class": summary.class_designation,
                "Available seats": summary.available_seat_count,
                "Average available fare": summary.average_available_price,
            }
            for summary in summaries
        ],
        hide_index=True,
        use_container_width=True,
    )


def show_fare_deals(data: CityAirlineData, airports: list[Airport]) -> None:
    """Render all available fares and their route price summary."""
    st.subheader("4. View Fares")
    with st.form("fare_deals"):
        departure, arrival, travel_date = airport_controls(airports, "deals")
        submitted = st.form_submit_button("View fares")
    if not submitted:
        return
    try:
        fares = data.list_route_fares(departure.id, arrival.id, travel_date)
    except Exception as error:
        show_database_error(error, "Unable to load fares right now.")
        return
    if not fares:
        st.info("No available fares were found for this route and date.")
        return

    prices = [fare.price for fare in fares]
    minimum_column, maximum_column, average_column = st.columns(3)
    minimum_column.metric("Minimum fare", f"${min(prices):.2f}")
    maximum_column.metric("Maximum fare", f"${max(prices):.2f}")
    average_column.metric("Average fare", f"${sum(prices) / len(prices):.2f}")

    st.dataframe(
        [
            {
                "Flight": fare.flight_number,
                "Departure": fare.departure_time,
                "Seat": fare.seat_number,
                "Class": fare.class_designation,
                "Fare": fare.price,
            }
            for fare in fares
        ],
        hide_index=True,
        use_container_width=True,
    )


def show_create_passenger(data: CityAirlineData) -> None:
    """Render the required passenger INSERT feature."""
    st.subheader("5. Create Passenger Profile")
    with st.form("create_passenger"):
        contact_information = st.text_input("Contact information (email or phone)")
        submitted = st.form_submit_button("Create profile")
    if submitted:
        if not contact_information.strip():
            st.error("Contact information cannot be empty.")
            return
        try:
            data.create_passenger(contact_information.strip())
        except Exception as error:
            show_database_error(error, "Unable to create the passenger profile.")
        else:
            st.success("Passenger profile created.")


def show_update_passenger(data: CityAirlineData) -> None:
    """Render the required passenger UPDATE feature."""
    st.subheader("6. Update Passenger Contact")
    try:
        passengers = data.list_passengers()
    except Exception as error:
        show_database_error(error, "Unable to load passenger profiles.")
        return
    if not passengers:
        st.info("No passenger profiles are available to update.")
        return
    labels = {f"{item.contact_information} ({item.id[:8]})": item for item in passengers}
    with st.form("update_passenger"):
        passenger = st.selectbox("Passenger", list(labels), format_func=str)
        contact_information = st.text_input("New contact information")
        submitted = st.form_submit_button("Save contact information")
    if submitted:
        if not contact_information.strip():
            st.error("Contact information cannot be empty.")
            return
        try:
            updated = data.update_passenger_contact(
                labels[passenger].id, contact_information.strip()
            )
        except Exception as error:
            show_database_error(error, "Unable to update the passenger profile.")
        else:
            if updated:
                st.success("Passenger contact information updated.")
            else:
                st.error("Passenger profile was not found.")


def show_purchase(data: CityAirlineData) -> None:
    """Render the required ticket-purchase transaction feature."""
    st.subheader("7. Purchase Ticket")
    flight = selected_flight(data)
    if flight is None:
        st.info("Search for and select a flight first.")
        return
    try:
        seats = data.list_available_seats(flight.id)
        passengers = data.list_passengers()
    except Exception as error:
        show_database_error(error, "Unable to load ticket options.")
        return
    if not seats:
        st.warning("There are no available seats on this flight.")
        return
    seats_by_label = {seat.label: seat for seat in seats}
    passenger_labels = {
        f"{item.contact_information} ({item.id[:8]})": item for item in passengers
    }
    with st.form("purchase_ticket"):
        seat = st.selectbox("Available seat", list(seats_by_label))
        traveler_type = st.radio("Traveler", ["New traveler", "Existing passenger"])
        passenger = None
        contact_information = ""
        if traveler_type == "Existing passenger" and passenger_labels:
            passenger_label = st.selectbox("Passenger", list(passenger_labels))
            passenger = passenger_labels[passenger_label]
        elif traveler_type == "Existing passenger":
            st.info("No profiles exist yet. Use a new traveler instead.")
        if traveler_type == "New traveler":
            contact_information = st.text_input("Contact information (email or phone)")
        submitted = st.form_submit_button("Purchase ticket")
    if not submitted:
        return
    if traveler_type == "New traveler" and not contact_information.strip():
        st.error("Contact information is required for a new traveler.")
        return
    if traveler_type == "Existing passenger" and passenger is None:
        st.error("Select a passenger or choose a new traveler.")
        return
    try:
        data.purchase_ticket(
            seats_by_label[seat].ticket_id,
            passenger_id=passenger.id if passenger else None,
            contact_information=contact_information.strip() if not passenger else None,
        )
    except TicketUnavailableError:
        st.error("That seat was just sold. Please choose another available seat.")
        st.info("The checkout transaction was rolled back; no passenger or ticket changes were saved.")
    except Exception as error:
        show_database_error(error, "Unable to complete the purchase.")
        st.info("The checkout transaction was rolled back; no partial purchase was saved.")
    else:
        st.success("Your ticket has been purchased. The passenger and ticket sale were committed together.")
        st.rerun()


def show_demonstrations(data: CityAirlineData) -> None:
    """Run a visible concurrency demonstration for ticket checkout."""
    st.subheader("Concurrent Ticket Purchase")
    st.info(
        "Choose one available seat, then start two buyers at the same instant. "
        "Only one transaction can sell the ticket; the other buyer is rolled back."
    )
    flight = selected_flight(data)
    if flight is None:
        st.warning("Search for and select a flight before running the concurrency demo.")
        return
    try:
        seats = data.list_available_seats(flight.id)
    except Exception as error:
        show_database_error(error, "Unable to load available seats.")
        return
    if not seats:
        st.warning("No available seats remain on the selected flight.")
        return

    seats_by_label = {seat.label: seat for seat in seats}
    selected_seat = st.selectbox("Ticket both buyers will attempt to purchase", seats_by_label)
    st.caption(
        f"Flight {flight.flight_number} · {seats_by_label[selected_seat].label} · "
        "two independent database transactions"
    )
    if not st.button("Start two-buyer race", type="primary"):
        return
    try:
        result = data.demonstrate_concurrent_purchase(seats_by_label[selected_seat].ticket_id)
    except Exception as error:
        show_database_error(error, "Unable to run the concurrent purchase demonstration.")
        return

    st.success("Race complete: exactly one buyer purchased the ticket.")
    buyer_a, buyer_b = st.columns(2)
    for column, attempt in zip((buyer_a, buyer_b), result.attempts, strict=True):
        column.subheader(attempt.buyer)
        column.code(attempt.contact_information, language="text")
        column.metric("Outcome", attempt.outcome)
    status, passenger = st.columns(2)
    status.metric("Final ticket status", result.final_sale_status.title())
    passenger.metric("Passenger saved on ticket", result.final_passenger_contact or "None")
    st.code(
        "Both buyers reached checkout together\n"
        "Buyer 1 updated the available ticket and COMMITed\n"
        "Buyer 2 found no available ticket row and ROLLBACKed\n"
        "Verification: one sold ticket, assigned to the winning buyer",
        language="text",
    )
