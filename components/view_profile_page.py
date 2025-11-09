import streamlit as st
from database.db_functions import get_farmer_profile, update_farmer_profile
from weather.ai_client import AIClient

def calculate_profile_completeness(profile):
    """Calculate profile completeness percentage"""
    checks = {
        'basic_info': bool(profile['name'] and profile['contact']),
        'farm_details': bool(profile['location'] and profile['farm_size'] > 0),
        'weather_location': bool(profile['weather_location']),
        'coordinates': bool(profile['latitude'] and profile['longitude'])
    }
    
    completed = sum(checks.values())
    total = len(checks)
    percentage = int((completed / total) * 100)
    
    return percentage, checks

def render_view_profile_page():
    st.header("👤 MY PROFILE")
    
    # Custom CSS for profile page
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
    .completeness-bar {
        height: 25px;
        background: #E0E0E0;
        border-radius: 12px;
        overflow: hidden;
        margin: 10px 0;
    }
    .completeness-fill {
        height: 100%;
        background: linear-gradient(90deg, #2E8B57, #3CB371);
        transition: width 0.5s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
    }
    .status-item {
        padding: 10px;
        margin: 8px 0;
        border-radius: 8px;
        border-left: 4px solid;
    }
    .status-complete {
        background: #E8F5E9;
        border-color: #4CAF50;
    }
    .status-incomplete {
        background: #FFF3E0;
        border-color: #FF9800;
    }
    </style>
    """, unsafe_allow_html=True)

    if st.session_state.get("logged_in") and st.session_state.get("role") == "Farmer":
        farmer_name = st.session_state.farmer_name
        farmer_profile = get_farmer_profile(farmer_name)

        if farmer_profile:
            # Calculate profile completeness
            completeness, checks = calculate_profile_completeness(farmer_profile)
            
            # Profile Completeness Indicator
            st.markdown(f"""
            <div class='profile-card'>
                <h3 style='color: #2E8B57; margin-bottom: 15px;'>Profile Completeness: {completeness}%</h3>
                <div class='completeness-bar'>
                    <div class='completeness-fill' style='width: {completeness}%;'>{completeness}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Completeness Details
            col1, col2 = st.columns(2)
            
            with col1:
                # Basic Info Status
                status_class = "status-complete" if checks['basic_info'] else "status-incomplete"
                icon = "✅" if checks['basic_info'] else "❌"
                st.markdown(f"""
                <div class='status-item {status_class}'>
                    {icon} <strong>Basic Info</strong><br>
                    <small>Name and Contact</small>
                </div>
                """, unsafe_allow_html=True)
                
                # Farm Details Status
                status_class = "status-complete" if checks['farm_details'] else "status-incomplete"
                icon = "✅" if checks['farm_details'] else "❌"
                st.markdown(f"""
                <div class='status-item {status_class}'>
                    {icon} <strong>Farm Details</strong><br>
                    <small>Location and Size</small>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Weather Location Status
                status_class = "status-complete" if checks['weather_location'] else "status-incomplete"
                icon = "✅" if checks['weather_location'] else "⚠️"
                st.markdown(f"""
                <div class='status-item {status_class}'>
                    {icon} <strong>Weather Location</strong><br>
                    <small>Set for forecasts</small>
                </div>
                """, unsafe_allow_html=True)
                
                # Coordinates Status
                status_class = "status-complete" if checks['coordinates'] else "status-incomplete"
                icon = "✅" if checks['coordinates'] else "⚠️"
                action = "" if checks['coordinates'] else "<br><small style='color: #FF9800;'>Add coordinates below</small>"
                st.markdown(f"""
                <div class='status-item {status_class}'>
                    {icon} <strong>GPS Coordinates</strong><br>
                    <small>For accurate weather{action}</small>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Profile Information Display
            st.subheader("📋 Profile Information")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class='profile-card'>
                    <strong>👤 Name:</strong> {farmer_profile['name']}<br>
                    <strong>📍 Location:</strong> {farmer_profile['location']}<br>
                    <strong>📞 Contact:</strong> {farmer_profile['contact']}
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class='profile-card'>
                    <strong>🚜 Farm Size:</strong> {farmer_profile['farm_size']} {farmer_profile['farm_unit']}<br>
                    <strong>🌍 Weather Location:</strong> {farmer_profile['weather_location']}<br>
                    <strong>📍 Coordinates:</strong> {f"({farmer_profile['latitude']:.4f}, {farmer_profile['longitude']:.4f})" if farmer_profile['latitude'] and farmer_profile['longitude'] else "Not set"}
                </div>
                """, unsafe_allow_html=True)
            
            # Edit Profile Section
            st.markdown("---")
            st.subheader("✏️ Edit Profile")
            
            with st.expander("📝 Update Profile Information", expanded=False):
                with st.form("edit_profile_form"):
                    st.info("Update your profile information below")
                    
                    new_location = st.text_input("Farm Location", value=farmer_profile['location'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        new_farm_size = st.number_input("Farm Size", min_value=0.0, value=float(farmer_profile['farm_size']), format="%.2f")
                    with col2:
                        new_farm_unit = st.selectbox("Unit", ["Acres", "Hectares"], 
                                                     index=0 if farmer_profile['farm_unit'] == 'Acres' else 1)
                    
                    new_contact = st.text_input("Contact Number", value=farmer_profile['contact'])
                    new_weather_location = st.text_input("Weather Location", value=farmer_profile['weather_location'])
                    
                    # Location verification method
                    st.markdown("#### 🌍 Location Verification Method")
                    verification_method = st.radio(
                        "Choose verification method:",
                        ["Manual Entry", "GPS + AI Verification", "AI Only"],
                        help="GPS is most accurate. AI provides address verification."
                    )
                    
                    update_coords = False
                    if verification_method == "Manual Entry":
                        col_lat, col_lon = st.columns(2)
                        with col_lat:
                            manual_lat = st.number_input("Latitude", value=float(farmer_profile['latitude'] or 0.0), format="%.6f")
                        with col_lon:
                            manual_lon = st.number_input("Longitude", value=float(farmer_profile['longitude'] or 0.0), format="%.6f")
                    elif verification_method == "AI Only":
                        update_coords = st.checkbox("🌍 Fetch coordinates using AI AI", value=True)
                    
                    if st.form_submit_button("💾 Save Changes", use_container_width=True):
                        new_latitude = farmer_profile['latitude']
                        new_longitude = farmer_profile['longitude']
                        
                        # Handle different verification methods
                        if verification_method == "Manual Entry":
                            new_latitude = manual_lat
                            new_longitude = manual_lon
                            st.info("📝 Using manually entered coordinates")
                            
                        elif verification_method == "AI Only":
                            if update_coords and new_weather_location:
                                with st.spinner("🤖 Fetching coordinates with AI..."):
                                    try:
                                        ai_client = AIClient()
                                        coords = ai_client.get_coordinates_from_google_search(new_weather_location)
                                        if coords:
                                            new_latitude = coords['lat']
                                            new_longitude = coords['lon']
                                            st.success(f"✅ AI coordinates: ({new_latitude:.4f}, {new_longitude:.4f})")
                                    except Exception as e:
                                        st.warning(f"⚠️ Could not fetch coordinates: {str(e)}")
                        
                        elif verification_method == "GPS + AI Verification":
                            st.info("🛰️ Using GPS + AI verification. Please use the GPS widget below.")
                            if st.session_state.get('verified_latitude') and st.session_state.get('verified_longitude'):
                                new_latitude = st.session_state.verified_latitude
                                new_longitude = st.session_state.verified_longitude
                                trust_level = st.session_state.get('location_trust_level', 'Unknown')
                                st.success(f"✅ Using verified location (Trust: {trust_level})")
                            else:
                                st.warning("⚠️ Please verify your location using the GPS widget below first!")
                        
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
                            st.success("✅ Profile updated successfully!")
                            st.session_state.farmer_profile = get_farmer_profile(farmer_name)
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error updating profile: {str(e)}")
            
            # GPS + AI Verification Widget
            st.markdown("---")
            with st.expander("🛰️ GPS + AI Location Verification", expanded=False):
                st.info("💡 Use this tool to verify your location with both GPS and AI for maximum accuracy")
                from components.location_verification import render_location_verification_widget
                render_location_verification_widget()
            
            # Complete Profile Button (if incomplete)
            if completeness < 100:
                st.markdown("---")
                st.warning("⚠️ Your profile is incomplete. Complete it for the best experience!")
                if st.button("🎯 Complete Profile Now", use_container_width=True, type="primary"):
                    st.info("👆 Expand the 'Update Profile Information' section above to complete your profile")
                    
        else:
            st.warning("⚠️ Farmer profile not found. Please contact admin.")
            
    elif st.session_state.get("logged_in") and st.session_state.get("role") == "Admin":
        st.info("👨‍💼 Admin does not have a personal profile to view.")
        st.markdown("To manage farmer profiles, go to **Admin Tools → Manage Farmers**")
    else:
        st.warning("⚠️ Please login to view your profile.")


