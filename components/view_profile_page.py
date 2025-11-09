import streamlit as st
from database.db_functions import get_farmer_profile, update_farmer_profile
from weather.ai_client import AIClient
from components.translation_utils import t

def render_view_profile_page():
    st.header(f"👤 {t('MY PROFILE')}")
    
    # Custom CSS for profile page with mobile responsiveness
    st.markdown("""
    <style>
    .profile-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border-left: 5px solid #2E8B57;
    }
    
    @media (max-width: 768px) {
        .profile-card {
            padding: 15px;
            font-size: 0.9rem;
        }
        
        /* Stack profile columns */
        [data-testid="column"] {
            width: 100% !important;
            margin-bottom: 10px;
        }
        
        /* Form inputs */
        .stTextInput, .stNumberInput, .stSelectbox {
            margin-bottom: 10px;
        }
    }
    
    @media (max-width: 480px) {
        .profile-card {
            padding: 10px;
            font-size: 0.85rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    if st.session_state.get("logged_in") and st.session_state.get("role") == "Farmer":
        farmer_name = st.session_state.farmer_name
        farmer_profile = get_farmer_profile(farmer_name)

        if farmer_profile:
            # Profile Information Display
            st.subheader(f"📋 {t('Profile Information')}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class='profile-card'>
                    <strong>👤 {t('Name')}:</strong> {farmer_profile['name']}<br>
                    <strong>📍 {t('Location')}:</strong> {farmer_profile['location']}<br>
                    <strong>📞 {t('Contact')}:</strong> {farmer_profile['contact']}
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class='profile-card'>
                    <strong>🚜 {t('Farm Size')}:</strong> {farmer_profile['farm_size']} {farmer_profile['farm_unit']}<br>
                    <strong>🌍 {t('Weather Location')}:</strong> {farmer_profile['weather_location']}<br>
                    <strong>📍 {t('Coordinates')}:</strong> {f"({farmer_profile['latitude']:.4f}, {farmer_profile['longitude']:.4f})" if farmer_profile['latitude'] and farmer_profile['longitude'] else t('Not set')}
                </div>
                """, unsafe_allow_html=True)
            
            # Location Management Section
            st.markdown("---")
            from components.location_manager import render_location_setup
            render_location_setup(
                farmer_name,
                farmer_profile.get('location'),
                farmer_profile.get('latitude'),
                farmer_profile.get('longitude')
            )
            
            # Edit Profile Section
            st.markdown("---")
            st.subheader(f"✏️ {t('Edit Profile')}")
            
            with st.expander(f"📝 {t('Update Profile Information')}", expanded=False):
                with st.form("edit_profile_form"):
                    st.info(t("Update your profile information below"))
                    
                    new_location = st.text_input(t("Farm Location"), value=farmer_profile['location'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        new_farm_size = st.number_input(t("Farm Size"), min_value=0.0, value=float(farmer_profile['farm_size']), format="%.2f")
                    with col2:
                        new_farm_unit = st.selectbox(t("Unit"), [t("Acres"), t("Hectares")], 
                                                     index=0 if farmer_profile['farm_unit'] == t('Acres') else 1)
                    
                    new_contact = st.text_input(t("Contact Number"), value=farmer_profile['contact'])
                    new_weather_location = st.text_input(t("Weather Location"), value=farmer_profile['weather_location'])
                    
                    # Location verification method
                    st.markdown(f"#### 🌍 {t('Location Verification Method')}")
                    verification_method = st.radio(
                        t("Choose verification method:"),
                        [t("Manual Entry"), t("GPS + AI Verification"), t("AI Only")],
                        help="GPS is most accurate. AI provides address verification."
                    )
                    
                    update_coords = False
                    if verification_method == t("Manual Entry"):
                        col_lat, col_lon = st.columns(2)
                        with col_lat:
                            manual_lat = st.number_input(t("Latitude"), value=float(farmer_profile['latitude'] or 0.0), format="%.6f")
                        with col_lon:
                            manual_lon = st.number_input(t("Longitude"), value=float(farmer_profile['longitude'] or 0.0), format="%.6f")
                    elif verification_method == t("AI Only"):
                        update_coords = st.checkbox(f"🌍 {t('Fetch coordinates using AI')}", value=True)
                    
                    if st.form_submit_button(f"💾 {t('Save Changes')}", width="stretch"):
                        new_latitude = farmer_profile['latitude']
                        new_longitude = farmer_profile['longitude']
                        
                        # Handle different verification methods
                        if verification_method == t("Manual Entry"):
                            new_latitude = manual_lat
                            new_longitude = manual_lon
                            st.info(f"📝 {t('Using manually entered coordinates')}")
                            
                        elif verification_method == t("AI Only"):
                            if update_coords and new_weather_location:
                                with st.spinner(f"🤖 {t('Fetching coordinates with AI...')}"):
                                    try:
                                        ai_client = AIClient()
                                        coords = ai_client.get_coordinates_from_google_search(new_weather_location)
                                        if coords:
                                            new_latitude = coords['lat']
                                            new_longitude = coords['lon']
                                            st.success(f"✅ {t('AI coordinates')}: ({new_latitude:.4f}, {new_longitude:.4f})")
                                    except Exception as e:
                                        st.warning(f"⚠️ {t('Could not fetch coordinates')}: {str(e)}")
                        
                        elif verification_method == t("GPS + AI Verification"):
                            st.info(f"🛰️ {t('Using GPS + AI verification. Please use the GPS widget below.')}")
                            if st.session_state.get('verified_latitude') and st.session_state.get('verified_longitude'):
                                new_latitude = st.session_state.verified_latitude
                                new_longitude = st.session_state.verified_longitude
                                trust_level = st.session_state.get('location_trust_level', 'Unknown')
                                st.success(f"✅ {t('Using verified location')} (Trust: {trust_level})")
                            else:
                                st.warning(f"⚠️ {t('Please verify your location using the GPS widget below first!')}")
                        
                        # Update profile
                        try:
                            update_farmer_profile(
                                farmer_name,
                                new_location,
                                new_farm_size,
                                new_farm_unit,
                                new_contact,
                                new_weather_location,
                                new_latitude,
                                new_longitude
                            )
                            st.success(f"✅ {t('Profile updated successfully!')}")
                            st.session_state.farmer_profile = get_farmer_profile(farmer_name)
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ {t('Error updating profile')}: {str(e)}")
            
            # GPS + AI Verification Widget
            st.markdown("---")
            with st.expander(f"🛰️ {t('GPS + AI Location Verification')}", expanded=False):
                st.info(f"💡 {t('Use this tool to verify your location with both GPS and AI for maximum accuracy')}")
                from components.location_verification import render_location_verification_widget
                render_location_verification_widget()
                    
        else:
            st.warning(f"⚠️ {t('Farmer profile not found. Please contact admin.')}")
            
    elif st.session_state.get("logged_in") and st.session_state.get("role") == "Admin":
        st.info(f"👨‍💼 {t('Admin does not have a personal profile to view.')}")
        st.markdown(f"{t('To manage farmer profiles, go to')} **{t('ADMIN TOOLS')} → {t('Manage Farmers')}**")
    else:
        st.warning(f"⚠️ {t('Please login to view your profile.')}")


