import streamlit as st
from database.db_functions import get_farmer_profile

def render_view_profile_page():
    st.header("👨‍🌾 Your Profile")

    if st.session_state.get("logged_in") and st.session_state.get("role") == "Farmer":
        farmer_name = st.session_state.farmer_name
        farmer_profile = get_farmer_profile(farmer_name)

        if farmer_profile:
            st.subheader(f"Welcome, {farmer_profile['name']}!")
            st.write(f"**Location:** {farmer_profile['location']}")
            st.write(f"**Farm Size:** {farmer_profile['farm_size']} {farmer_profile['farm_unit']}")
            st.write(f"**Contact:** {farmer_profile['contact']}")
            st.write(f"**Weather Location:** {farmer_profile['weather_location']}")
            st.write(f"**Latitude:** {farmer_profile['latitude']}")
            st.write(f"**Longitude:** {farmer_profile['longitude']}")
        else:
            st.warning("⚠️ Farmer profile not found. Please create your profile.")
            # Optionally, provide a link or button to create profile
            # For now, we'll just display the message.
    elif st.session_state.get("logged_in") and st.session_state.get("role") == "Admin":
        st.info("Admin does not have a personal profile to view.")
    else:
        st.warning("⚠️ Please login to view your profile.")
