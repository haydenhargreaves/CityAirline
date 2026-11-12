"""Streamlit views for each City Airline application workflow."""

from datetime import date

import streamlit as st

from app.controller import ActionResult, CityAirlineController
from app.models import Airport, Flight, FlightSearchResult, Passenger


def render_route_controls(
    available_airports: list[Airport], form_prefix: str
) -> tuple[Airport, Airport, date]:
    """Render route controls and return the selected airports and date."""
    airport_by_display_label = {
        airport.label: airport for airport in available_airports
    }
    airport_display_labels = list(airport_by_display_label)
    selected_departure_airport_label = st.selectbox(
        "From", airport_display_labels, key=f"{form_prefix}_departure_airport"
    )
    available_arrival_airport_labels = [
        airport_display_label
        for airport_display_label in airport_display_labels
        if airport_display_label != selected_departure_airport_label
    ]
    selected_arrival_airport_label = st.selectbox(
        "To", available_arrival_airport_labels, key=f"{form_prefix}_arrival_airport"
    )
    selected_travel_date = st.date_input(
        "Travel date", value=date.today(), key=f"{form_prefix}_travel_date"
    )
    return (
        airport_by_display_label[selected_departure_airport_label],
        airport_by_display_label[selected_arrival_airport_label],
        selected_travel_date,
    )


def render_action_error(action_result: ActionResult[object]) -> bool:
    """Render an action error and report whether rendering should stop."""
    if action_result.error_message is None:
        return False
    st.error(action_result.error_message)
    return True


def selected_flight_id() -> str | None:
    """Return the flight currently selected in the search view."""
    return st.session_state.get("selected_flight_id")


def render_flight_search_view(
    application_controller: CityAirlineController,
    available_airports: list[Airport],
) -> None:
    """Render the route/date flight-search workflow."""
    st.subheader("1. Search Flights")
    with st.form("flight_search_form"):
        (
            selected_departure_airport,
            selected_arrival_airport,
            selected_travel_date,
        ) = render_route_controls(available_airports, "flight_search")
        submitted_search = st.form_submit_button("Search flights")

    if submitted_search:
        matching_route_flights_result = application_controller.search_flights(
            selected_departure_airport.id,
            selected_arrival_airport.id,
            selected_travel_date,
        )
        if render_action_error(matching_route_flights_result):
            return
        st.session_state["matching_route_flights"] = (
            matching_route_flights_result.value or []
        )
        st.session_state.pop("selected_flight_id", None)

    matching_route_flights: list[FlightSearchResult] = st.session_state.get(
        "matching_route_flights", []
    )
    if not matching_route_flights:
        if "matching_route_flights" in st.session_state:
            st.info("No flights matched that route and date.")
        return

    st.dataframe(
        [
            {
                "Flight": route_flight.flight_number,
                "Departure": route_flight.departure_time,
            }
            for route_flight in matching_route_flights
        ],
        hide_index=True,
        use_container_width=True,
    )
    selected_route_flight = st.selectbox(
        "Select a flight",
        matching_route_flights,
        format_func=lambda route_flight: route_flight.label,
    )
    st.session_state["selected_flight_id"] = selected_route_flight.id
    st.success("Flight selected. Open another tab to view details or purchase a seat.")


def render_flight_details_view(application_controller: CityAirlineController) -> None:
    """Render joined details for the selected flight."""
    st.subheader("2. View Flight Details")
    selected_flight_identifier = selected_flight_id()
    if selected_flight_identifier is None:
        st.info("Search for and select a flight first.")
        return
    selected_flight_details_result = application_controller.load_flight_details(
        selected_flight_identifier
    )
    if render_action_error(selected_flight_details_result):
        return
    selected_flight_details = selected_flight_details_result.value
    if selected_flight_details is None:
        return
    st.dataframe(
        [
            {
                "Flight": selected_flight_details.flight_number,
                "Airline": f"{selected_flight_details.airline_name} ({selected_flight_details.airline_code})",
                "Plane": f"{selected_flight_details.plane_name} ({selected_flight_details.plane_code})",
                "Departure airport": f"{selected_flight_details.departure_airport_code} - {selected_flight_details.departure_airport_name}",
                "Arrival airport": f"{selected_flight_details.arrival_airport_code} - {selected_flight_details.arrival_airport_name}",
                "Departure": selected_flight_details.departure_time,
                "Boarding": selected_flight_details.boarding_time,
                "Lowest available fare": selected_flight_details.lowest_available_price,
            }
        ],
        hide_index=True,
        use_container_width=True,
    )


def render_seat_summary_view(application_controller: CityAirlineController) -> None:
    """Render grouped seat availability and average fare data."""
    st.subheader("3. View Seat Summary")
    selected_flight_identifier = selected_flight_id()
    if selected_flight_identifier is None:
        st.info("Search for and select a flight first.")
        return
    seat_summary_result = application_controller.load_seat_summary(
        selected_flight_identifier
    )
    if render_action_error(seat_summary_result):
        return
    seat_summaries = seat_summary_result.value or []
    if not seat_summaries:
        st.info("No available seats remain on this flight.")
        return
    st.dataframe(
        [
            {
                "Class": seat_summary.class_designation,
                "Available seats": seat_summary.available_seat_count,
                "Average available fare": seat_summary.average_available_price,
            }
            for seat_summary in seat_summaries
        ],
        hide_index=True,
        use_container_width=True,
    )


def render_fare_deals_view(
    application_controller: CityAirlineController,
    available_airports: list[Airport],
) -> None:
    """Render the below-route-average fare report."""
    st.subheader("4. Find Fare Deals")
    with st.form("fare_deals_form"):
        (
            selected_departure_airport,
            selected_arrival_airport,
            selected_travel_date,
        ) = render_route_controls(available_airports, "fare_deals")
        submitted_fare_deal_search = st.form_submit_button("Find below-average fares")
    if not submitted_fare_deal_search:
        return
    fare_deals_result = application_controller.find_fare_deals(
        selected_departure_airport.id,
        selected_arrival_airport.id,
        selected_travel_date,
    )
    if render_action_error(fare_deals_result):
        return
    below_average_flights = fare_deals_result.value or []
    if not below_average_flights:
        st.info("No fares on this route are below the route average.")
        return
    st.dataframe(
        [
            {
                "Flight": below_average_flight.flight_number,
                "Departure": below_average_flight.departure_time,
                "Lowest available fare": below_average_flight.lowest_available_price,
            }
            for below_average_flight in below_average_flights
        ],
        hide_index=True,
        use_container_width=True,
    )


def render_create_passenger_view(application_controller: CityAirlineController) -> None:
    """Render the standalone passenger-profile creation workflow."""
    st.subheader("5. Create Passenger Profile")
    with st.form("create_passenger_form"):
        new_passenger_contact_information = st.text_input(
            "Contact information (email or phone)"
        )
        submitted_passenger_profile = st.form_submit_button("Create profile")
    if not submitted_passenger_profile:
        return
    if not new_passenger_contact_information.strip():
        st.error("Contact information cannot be empty.")
        return
    create_passenger_result = application_controller.create_passenger_profile(
        new_passenger_contact_information.strip()
    )
    if render_action_error(create_passenger_result):
        return
    st.success("Passenger profile created.")


def render_update_passenger_view(application_controller: CityAirlineController) -> None:
    """Render the passenger contact-information update workflow."""
    st.subheader("6. Update Passenger Contact")
    passenger_profiles_result = application_controller.load_passengers()
    if render_action_error(passenger_profiles_result):
        return
    passenger_profiles = passenger_profiles_result.value or []
    if not passenger_profiles:
        st.info("No passenger profiles are available to update.")
        return
    passenger_by_display_label = {
        f"{passenger_profile.contact_information} ({passenger_profile.id[:8]})": passenger_profile
        for passenger_profile in passenger_profiles
    }
    with st.form("update_passenger_form"):
        selected_passenger_label = st.selectbox(
            "Passenger", list(passenger_by_display_label)
        )
        updated_contact_information = st.text_input("New contact information")
        submitted_passenger_update = st.form_submit_button("Save contact information")
    if not submitted_passenger_update:
        return
    if not updated_contact_information.strip():
        st.error("Contact information cannot be empty.")
        return
    selected_passenger = passenger_by_display_label[selected_passenger_label]
    passenger_update_result = application_controller.update_passenger_contact(
        selected_passenger.id, updated_contact_information.strip()
    )
    if render_action_error(passenger_update_result):
        return
    if passenger_update_result.value:
        st.success("Passenger contact information updated.")
    else:
        st.error("Passenger profile was not found.")


def render_purchase_ticket_view(application_controller: CityAirlineController) -> None:
    """Render the ticket-purchase transaction workflow."""
    st.subheader("7. Purchase Ticket")
    selected_flight_identifier = selected_flight_id()
    if selected_flight_identifier is None:
        st.info("Search for and select a flight first.")
        return
    available_seats_result = application_controller.load_available_seats(
        selected_flight_identifier
    )
    passenger_profiles_result = application_controller.load_passengers()
    if render_action_error(available_seats_result) or render_action_error(
        passenger_profiles_result
    ):
        return
    available_seats = available_seats_result.value or []
    passenger_profiles = passenger_profiles_result.value or []
    if not available_seats:
        st.warning("There are no available seats on this flight.")
        return
    available_seat_by_display_label = {
        available_seat.label: available_seat for available_seat in available_seats
    }
    passenger_by_display_label = {
        f"{passenger_profile.contact_information} ({passenger_profile.id[:8]})": passenger_profile
        for passenger_profile in passenger_profiles
    }
    with st.form("purchase_ticket_form"):
        selected_seat_label = st.selectbox(
            "Available seat", list(available_seat_by_display_label)
        )
        selected_traveler_type = st.radio(
            "Traveler", ["New traveler", "Existing passenger"]
        )
        selected_existing_passenger: Passenger | None = None
        new_passenger_contact_information = ""
        if selected_traveler_type == "Existing passenger" and passenger_by_display_label:
            selected_passenger_label = st.selectbox(
                "Passenger", list(passenger_by_display_label)
            )
            selected_existing_passenger = passenger_by_display_label[
                selected_passenger_label
            ]
        elif selected_traveler_type == "Existing passenger":
            st.info("No profiles exist yet. Choose New traveler instead.")
        if selected_traveler_type == "New traveler":
            new_passenger_contact_information = st.text_input(
                "Contact information (email or phone)"
            )
        submitted_ticket_purchase = st.form_submit_button("Purchase ticket")
    if not submitted_ticket_purchase:
        return
    if (
        selected_traveler_type == "New traveler"
        and not new_passenger_contact_information.strip()
    ):
        st.error("Contact information is required for a new traveler.")
        return
    if (
        selected_traveler_type == "Existing passenger"
        and selected_existing_passenger is None
    ):
        st.error("Select a passenger or choose New traveler.")
        return
    selected_available_seat = available_seat_by_display_label[selected_seat_label]
    ticket_purchase_result = application_controller.purchase_ticket(
        selected_available_seat.ticket_id,
        selected_existing_passenger.id if selected_existing_passenger else None,
        new_passenger_contact_information.strip()
        if selected_existing_passenger is None
        else None,
    )
    if render_action_error(ticket_purchase_result):
        return
    st.success("Your ticket has been purchased.")
    st.rerun()


def render_demonstrations_view(application_controller: CityAirlineController) -> None:
    """Render the constraint and least-privilege demonstrations."""
    st.subheader("Database Requirement Demonstrations")
    if st.button("Demonstrate duplicate ticket constraint"):
        constraint_result = application_controller.demonstrate_duplicate_ticket_constraint()
        if constraint_result.succeeded:
            st.success("MySQL rejected the duplicate ticket for this flight and seat.")
        else:
            st.error(constraint_result.error_message)
    if st.button("Demonstrate denied flight creation"):
        permission_result = application_controller.demonstrate_denied_flight_creation()
        if permission_result.succeeded:
            st.success("The client account is not allowed to create flights.")
        else:
            st.error(permission_result.error_message)
