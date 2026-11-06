"""Simple Streamlit interface for searching and booking City Airline flights."""

from datetime import date

import streamlit as st

from app.data import CityAirlineData, TicketUnavailableError
from app.models import Airport, Flight


@st.cache_resource
def get_data() -> CityAirlineData:
    """Reuse the lightweight data-access service across Streamlit reruns."""
    return CityAirlineData()


def flight_label(flight: Flight) -> str:
    """Format a search result for the flight selector."""
    price = (
        f"from ${flight.lowest_available_price:.2f}"
        if flight.lowest_available_price is not None
        else "no seats available"
    )
    return (
        f"{flight.flight_number} | {flight.departure_time:%H:%M} | "
        f"{flight.airline_name} | {price}"
    )


def show_search(data: CityAirlineData, airports: list[Airport]) -> None:
    """Render flight-search form and matching flights."""
    st.header("Find a flight")
    if len(airports) < 2:
        st.info("At least two airports are required to search for flights.")
        return

    airport_by_label = {airport.label: airport for airport in airports}
    labels = list(airport_by_label)
    with st.form("flight_search"):
        departure_label = st.selectbox("From", labels)
        arrival_options = [label for label in labels if label != departure_label]
        arrival_label = st.selectbox("To", arrival_options)
        travel_date = st.date_input("Travel date", value=date.today())
        below_route_average = st.checkbox(
            "Only show flights with an available fare below the route average"
        )
        submitted = st.form_submit_button("Search flights")

    if submitted:
        departure = airport_by_label[departure_label]
        arrival = airport_by_label[arrival_label]
        st.session_state["flights"] = data.search_flights(
            departure.id, arrival.id, travel_date, below_route_average
        )
        st.session_state["selected_flight_id"] = None

    flights: list[Flight] = st.session_state.get("flights", [])
    if not flights:
        if "flights" in st.session_state:
            st.info("No flights matched that route and date.")
        return

    st.subheader("Search results")
    st.dataframe(
        [
            {
                "Flight": flight.flight_number,
                "Airline": flight.airline_name,
                "From": f"{flight.departure_airport_code} - {flight.departure_airport_name}",
                "To": f"{flight.arrival_airport_code} - {flight.arrival_airport_name}",
                "Departure": flight.departure_time,
                "Boarding": flight.boarding_time,
                "Plane": flight.plane_name,
                "Lowest available price": flight.lowest_available_price,
            }
            for flight in flights
        ],
        hide_index=True,
        use_container_width=True,
    )
    selected_flight = st.selectbox(
        "Choose a flight",
        flights,
        format_func=flight_label,
        key="flight_choice",
    )
    st.session_state["selected_flight_id"] = selected_flight.id
    show_booking(data, selected_flight)


def show_booking(data: CityAirlineData, flight: Flight) -> None:
    """Render seat availability and checkout for the selected flight."""
    st.header(f"Book {flight.flight_number}")
    summaries = data.get_seat_summary(flight.id)
    if summaries:
        st.dataframe(
            [
                {
                    "Class": summary.class_designation,
                    "Available seats": summary.available_seat_count,
                    "Average price": summary.average_available_price,
                }
                for summary in summaries
            ],
            hide_index=True,
            use_container_width=True,
        )

    seats = data.list_available_seats(flight.id)
    if not seats:
        st.warning("There are no available seats on this flight.")
        return

    seat_by_label = {seat.label: seat for seat in seats}
    with st.form("checkout"):
        seat_label = st.selectbox("Available seat", list(seat_by_label))
        passengers = data.list_passengers()
        traveler_type = st.radio(
            "Traveler", ["New traveler", "Existing passenger"], horizontal=True
        )
        passenger = None
        contact_information = ""
        if traveler_type == "Existing passenger" and passengers:
            passenger_by_label = {
                f"{item.contact_information} ({item.id[:8]})": item for item in passengers
            }
            passenger_label = st.selectbox(
                "Passenger", list(passenger_by_label)
            )
            passenger = passenger_by_label[passenger_label]
        elif traveler_type == "Existing passenger":
            st.info("No passenger profiles exist yet. Enter a new traveler instead.")
            traveler_type = "New traveler"

        if traveler_type == "New traveler":
            contact_information = st.text_input("Contact information (email or phone)")
        confirmed = st.form_submit_button("Purchase ticket")

    if confirmed:
        try:
            data.purchase_ticket(
                ticket_id=seat_by_label[seat_label].ticket_id,
                passenger_id=passenger.id if passenger else None,
                contact_information=contact_information if not passenger else None,
            )
        except TicketUnavailableError:
            st.error("That seat was just sold. Please choose another available seat.")
        except Exception as error:
            st.error(f"Unable to complete the purchase: {error}")
        else:
            st.success("Your ticket has been purchased.")
            st.rerun()


def show_contact_update(data: CityAirlineData) -> None:
    """Render a small contact-information editor for existing passengers."""
    with st.expander("Update passenger contact information"):
        passengers = data.list_passengers()
        if not passengers:
            st.info("No passenger profiles are available to update.")
            return

        passenger_by_label = {
            f"{passenger.contact_information} ({passenger.id[:8]})": passenger
            for passenger in passengers
        }
        with st.form("update_contact"):
            passenger_label = st.selectbox("Passenger", list(passenger_by_label))
            updated_contact = st.text_input("New contact information")
            submitted = st.form_submit_button("Save contact information")

        if submitted:
            if not updated_contact.strip():
                st.error("Contact information cannot be empty.")
            elif data.update_passenger_contact(
                passenger_by_label[passenger_label].id, updated_contact.strip()
            ):
                st.success("Passenger contact information updated.")
                st.rerun()
            else:
                st.error("Passenger profile was not found.")


def main() -> None:
    """Load reference data and show the flight booking workflow."""
    st.set_page_config(page_title="City Airline", page_icon="✈️")
    st.title("City Airline")
    try:
        data = get_data()
        airports = data.list_airports()
    except Exception as error:
        st.error(f"Could not connect to the City Airline database: {error}")
        st.caption("Check the MYSQL_* environment variables and database availability.")
        return

    show_search(data, airports)
    show_contact_update(data)


if __name__ == "__main__":
    main()
