"""Application entry point for the City Airline Streamlit interface."""

import streamlit as st

from app.data import CityAirlineData
from views import (
    show_create_passenger,
    show_demonstrations,
    show_fare_deals,
    show_flight_details,
    show_purchase,
    show_search,
    show_seat_summary,
    show_update_passenger,
)


@st.cache_resource
def get_data() -> CityAirlineData:
    """Reuse the data-access service across Streamlit reruns."""
    return CityAirlineData()


def main() -> None:
    """Load the application and render each customer workflow."""
    st.set_page_config(page_title="City Airline")
    st.title("City Airline")
    data = get_data()

    try:
        airports = data.list_airports()
    except Exception:
        st.error("Could not connect to the City Airline database.")
        st.caption("Check the MYSQL_* environment variables and database availability.")
        return
    if len(airports) < 2:
        st.error("At least two airports are required to search for flights.")
        return
    st.session_state["airports"] = airports

    tabs = st.tabs(
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
    with tabs[0]:
        show_search(data, airports)
    with tabs[1]:
        show_flight_details(data)
    with tabs[2]:
        show_seat_summary(data)
    with tabs[3]:
        show_fare_deals(data, airports)
    with tabs[4]:
        show_create_passenger(data)
    with tabs[5]:
        show_update_passenger(data)
    with tabs[6]:
        show_purchase(data)
    with tabs[7]:
        show_demonstrations(data)


if __name__ == "__main__":
    main()
