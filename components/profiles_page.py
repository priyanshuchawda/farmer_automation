# components/profiles_page.py
import streamlit as st
from database.db_functions import add_data, get_data
from weather.gemini_client import GeminiClient

def render_profiles_page():
    """Renders the page to manage farmer profiles."""
    st.subheader("🌾 Add/Update Farmer Profile")
    
    st.info("💡 Weather location will be used to show personalized weather forecasts and alerts on your calendar.")

    with st.form("new_farmer_form"):
        name = st.text_input("Farmer's Name *", placeholder="e.g., Ramesh Patil")
        
        col1, col2 = st.columns(2)
        with col1:
            location = st.text_input("Farm Location (Village) *", placeholder="e.g., Wadgaon Sheri")
        with col2:
            weather_location = st.text_input(
                "Weather Location *", 
                placeholder="e.g., Pune or Wadgaon Sheri Pune",
                help="City or area for weather forecasts"
            )
        
        col3, col4 = st.columns(2)
        with col3:
            farm_size = st.number_input("Farm Size *", min_value=0.0, format="%.2f")
        with col4:
            farm_unit = st.selectbox("Unit", ["Acres", "Hectares"])
        
        contact = st.text_input("Contact Number *", placeholder="e.g., 9876543210")
        
        submitted = st.form_submit_button("💾 Save Farmer Profile", use_container_width=True)
        
        if submitted:
            if name and location and farm_size > 0 and contact and weather_location:
                with st.spinner("Getting coordinates for weather location..."):
                    # Get coordinates for weather location
                    gemini_client = GeminiClient()
                    coords = gemini_client.get_coordinates_from_google_search(weather_location)
                    
                    if coords:
                        latitude = coords['lat']
                        longitude = coords['lon']
                        farmer_data = (name, location, farm_size, farm_unit, contact, weather_location, latitude, longitude)
                        add_data("farmers", farmer_data)
                        st.success(f"✅ Farmer '{name}' profile saved successfully!")
                        st.info(f"📍 Weather coordinates: {latitude}, {longitude}")
                        st.rerun()
                    else:
                        st.error("❌ Could not find coordinates for weather location. Please check the location name.")
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
