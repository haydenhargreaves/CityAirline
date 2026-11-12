"""Application entry point for the City Airline Streamlit interface."""

import streamlit as st

from app.controller import CityAirlineController
from app.data import CityAirlineData
from app.views import (
    render_create_passenger_view,
    render_demonstrations_view,
    render_fare_deals_view,
    render_flight_details_view,
    render_flight_search_view,
    render_purchase_ticket_view,
    render_seat_summary_view,
    render_update_passenger_view,
)


@st.cache_resource
def get_application_controller() -> CityAirlineController:
    """Create the controller shared across Streamlit reruns."""
    return CityAirlineController(CityAirlineData())


def main() -> None:
    """Load the application and render each customer workflow."""
    st.set_page_config(page_title="City Airline")
    st.title("City Airline")

    application_controller = get_application_controller()
    available_airports_result = application_controller.load_airports()
    if not available_airports_result.succeeded:
        st.error(available_airports_result.error_message)
        st.caption("Check the MYSQL_* environment variables and database availability.")
        return

    available_airports = available_airports_result.value or []
    if len(available_airports) < 2:
        st.error("At least two airports are required to search for flights.")
        return

    application_tabs = st.tabs(
        [
            "Search",
            "Flight Details",
            "Seat Summary",
            "Fare Deals",
            "Create Profile",
            "Update Profile",
            "Purchase",
            "Demonstrations",
        ]
    )
    with application_tabs[0]:
        render_flight_search_view(application_controller, available_airports)
    with application_tabs[1]:
        render_flight_details_view(application_controller)
    with application_tabs[2]:
        render_seat_summary_view(application_controller)
    with application_tabs[3]:
        render_fare_deals_view(application_controller, available_airports)
    with application_tabs[4]:
        render_create_passenger_view(application_controller)
    with application_tabs[5]:
        render_update_passenger_view(application_controller)
    with application_tabs[6]:
        render_purchase_ticket_view(application_controller)
    with application_tabs[7]:
        render_demonstrations_view(application_controller)


if __name__ == "__main__":
    main()
