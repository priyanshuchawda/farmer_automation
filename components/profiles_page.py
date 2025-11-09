# components/profiles_page.py
import streamlit as st
from database.db_functions import add_data, get_data, update_farmer_profile
from weather.ai_client import AIClient
from components.translation_utils import t

def render_profiles_page():
    """Renders the page to manage farmer profiles (Admin view only)."""
    st.header(f"👥 {t('Manage Farmer Profiles')}")
    
    st.markdown(f"""
    <div style='background-color:#E3F2FD;padding:15px;border-radius:10px;margin-bottom:20px;border-left:4px solid #1976D2;'>
        <strong>👨‍💼 {t('Admin Tool')}</strong><br>
        <small>💡 {t('New farmers register from the login page. Use this page to view all farmer profiles and manually add new ones if needed.')}</small>
    </div>
    """, unsafe_allow_html=True)

    with st.form("new_farmer_form"):
        name = st.text_input(f"{t('Farmer\'s Name')} *", placeholder=f"{t('e.g.')}, Ramesh Patil")
        
        col_pass1, col_pass2 = st.columns(2)
        with col_pass1:
            password = st.text_input(f"{t('Password')} *", type="password", placeholder=t("Create password"))
        with col_pass2:
            confirm_password = st.text_input(f"{t('Confirm Password')} *", type="password", placeholder=t("Re-enter password"))
        
        location = st.text_input(
            f"{t('Farm/Weather Location')} *", 
            placeholder=f"{t('e.g.')}, Wadgaon Sheri Pune",
            help=t("Village/City for farm and weather forecasts")
        )
        weather_location = location # Assign the same value to weather_location
        
        col3, col4 = st.columns(2)
        with col3:
            farm_size = st.number_input(f"{t('Farm Size')} *", min_value=0.0, format="%.2f")
        with col4:
            farm_unit = st.selectbox(t("Unit"), [t("Acres"), t("Hectares")])
        
        contact = st.text_input(f"{t('Contact Number')} *", placeholder=f"{t('e.g.')}, 9876543210")
        
        submitted = st.form_submit_button(f"💾 {t('Save Farmer Profile')}", use_container_width=True)
        
        if submitted:
            if name and location and farm_size > 0 and contact and password and confirm_password:
                if password != confirm_password:
                    st.error(f"❌ {t('Passwords do not match!')}")
                elif len(password) < 4:
                    st.error(f"❌ {t('Password must be at least 4 characters long!')}")
                else:
                    # Always get coordinates for weather_location
                    latitude = None
                    longitude = None
                    
                    with st.spinner(t("Getting coordinates for location...")):
                        try:
                            ai_client = AIClient()
                            coords = ai_client.get_coordinates_from_google_search(weather_location)
                            
                            if coords:
                                latitude = coords['lat']
                                longitude = coords['lon']
                                st.info(f"📍 {t('Coordinates for')} '{weather_location}': {latitude}, {longitude}")
                            else:
                                st.warning(f"⚠️ {t('Could not find coordinates for')} '{weather_location}'. {t('Profile will be saved without coordinates.')}")
                        except Exception as e:
                            st.warning(f"⚠️ {t('Error getting coordinates')}: {str(e)}. {t('Profile will be saved without coordinates.')}")
                    
                    # Save the profile with coordinates and password
                    farmer_data = (name, location, farm_size, farm_unit, contact, weather_location, latitude, longitude, password)
                    add_data("farmers", farmer_data)
                    st.success(f"✅ {t('Farmer')} '{name}' {t('profile saved successfully! You can now login with your credentials.')}")
            else:
                st.error(f"⚠️ {t('Please fill in all required fields (marked with *).')}")

    st.markdown("<hr>", unsafe_allow_html=True)

    st.subheader(f"📋 {t('All Farmer Profiles')}")
    farmers_df = get_data("farmers")
    
    if not farmers_df.empty:
        # Display with better formatting
        display_df = farmers_df.copy()
        if 'latitude' in display_df.columns and 'longitude' in display_df.columns:
            display_df['coordinates'] = display_df.apply(
                lambda row: f"({row['latitude']:.4f}, {row['longitude']:.4f})" if pd.notna(row['latitude']) else t("Not set"), 
                axis=1
            )
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info(t("No farmer profiles found. Add a new profile above."))

import pandas as pd


