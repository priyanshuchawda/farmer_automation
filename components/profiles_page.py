# components/profiles_page.py
import streamlit as st
from database.db_functions import add_data, get_data, update_farmer_profile
from weather.gemini_client import GeminiClient

def render_profiles_page():
    """Renders the page to manage farmer profiles."""
    st.subheader("🌾 Add/Update Farmer Profile")
    
    st.info("💡 Weather location will be used to show personalized weather forecasts and alerts on your calendar.")

    with st.form("new_farmer_form"):
        name = st.text_input("Farmer's Name *", placeholder="e.g., Ramesh Patil")
        
        location = st.text_input(
            "Farm/Weather Location *", 
            placeholder="e.g., Wadgaon Sheri Pune",
            help="Village/City for farm and weather forecasts"
        )
        weather_location = location # Assign the same value to weather_location
        
        col3, col4 = st.columns(2)
        with col3:
            farm_size = st.number_input("Farm Size *", min_value=0.0, format="%.2f")
        with col4:
            farm_unit = st.selectbox("Unit", ["Acres", "Hectares"])
        
        contact = st.text_input("Contact Number *", placeholder="e.g., 9876543210")
        
        submitted = st.form_submit_button("💾 Save Farmer Profile", use_container_width=True)
        
        if submitted:
            if name and location and farm_size > 0 and contact:
                # Always get coordinates for weather_location
                latitude = None
                longitude = None
                
                with st.spinner("Getting coordinates for location..."):
                    try:
                        gemini_client = GeminiClient()
                        coords = gemini_client.get_coordinates_from_google_search(weather_location)
                        
                        if coords:
                            latitude = coords['lat']
                            longitude = coords['lon']
                            st.info(f"📍 Coordinates for '{weather_location}': {latitude}, {longitude}")
                        else:
                            st.warning(f"⚠️ Could not find coordinates for '{weather_location}'. Profile will be saved without coordinates.")
                    except Exception as e:
                        st.warning(f"⚠️ Error getting coordinates: {str(e)}. Profile will be saved without coordinates.")
                
                # Save the profile with coordinates (or None if not found)
                farmer_data = (name, location, farm_size, farm_unit, contact, weather_location, latitude, longitude)
                add_data("farmers", farmer_data)
                st.success(f"✅ Farmer '{name}' profile saved successfully!")
            else:
                st.error("⚠️ Please fill in all required fields (marked with *).")

    st.markdown("<hr>", unsafe_allow_html=True)

    st.subheader("📋 All Farmer Profiles")
    farmers_df = get_data("farmers")
    
    if not farmers_df.empty:
        # Display with better formatting
        display_df = farmers_df.copy()
        if 'latitude' in display_df.columns and 'longitude' in display_df.columns:
            display_df['coordinates'] = display_df.apply(
                lambda row: f"({row['latitude']:.4f}, {row['longitude']:.4f})" if pd.notna(row['latitude']) else "N/A", 
                axis=1
            )
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("No farmer profiles found. Add a new profile above.")

import pandas as pd
