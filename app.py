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


def main() -> None:
    """Load the application and render each customer workflow."""
    st.set_page_config(page_title="City Airline")
    st.title("City Airline")
    data = CityAirlineData()

    try:
        airports = data.list_airports()
    except Exception:
        st.error("Could not connect to the City Airline database.")
        st.caption("Check the MYSQL_* environment variables and database availability.")
        return
    if len(airports) < 2:
        st.error("At least two airports are required to search for flights.")
        return

    (
        search_tab,
        flight_details_tab,
        seat_summary_tab,
        fare_deals_tab,
        create_profile_tab,
        update_profile_tab,
        purchase_tab,
        demonstrations_tab,
    ) = st.tabs(
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
    with search_tab: show_search(data, airports)
    with flight_details_tab: show_flight_details(data)
    with seat_summary_tab: show_seat_summary(data)
    with fare_deals_tab: show_fare_deals(data, airports)
    with create_profile_tab: show_create_passenger(data)
    with update_profile_tab: show_update_passenger(data)
    with purchase_tab: show_purchase(data)
    with demonstrations_tab: show_demonstrations(data)


if __name__ == "__main__":
    main()
