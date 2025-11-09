# components/auth_page.py
"""
Dedicated Login and Registration Page for Smart Farmer Marketplace
Phase 1: Complete Login & Authentication Overhaul
"""

import streamlit as st
from database.db_functions import verify_farmer_login, add_data, get_farmer_profile
from weather.ai_client import AIClient
from datetime import datetime
from components.translation_utils import t, render_language_selector

def check_password_strength(password):
    """Check password strength and return score and message"""
    if len(password) < 4:
        return 0, "Too short"
    elif len(password) < 6:
        return 1, "Weak"
    elif len(password) < 8:
        return 2, "Good"
    else:
        return 3, "Strong"

def render_auth_page():
    """Render the main authentication page with login and registration"""
    
    # Add sidebar info while on login page
    with st.sidebar:
        # Language selector at the very top
        render_language_selector()
        st.markdown("---")
        
        st.markdown(f"## 🌾 {t('Welcome')}!")
        st.info(f"**Smart Farmer Marketplace**\n\n{t('Please login to continue')}")
        st.markdown("---")
        st.markdown(f"### 🌟 {t('Features')}")
        st.write(f"✅ {t('Marketplace for tools & crops')}")
        st.write(f"🌤️ {t('Weather forecasts')}")
        st.write(f"📅 {t('Smart calendar')}")
        st.write(f"💰 {t('Market prices')}")
        st.write(f"🤖 {t('AI assistance')}")
    
    # Custom CSS for authentication page
    st.markdown("""
    <style>
    /* Full screen centered layout with backdrop */
    .main .block-container {
        max-width: 500px;
        padding-top: 3rem;
        padding-bottom: 2rem;
    }
    
    /* Blurred background effect */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, rgba(46, 139, 87, 0.1) 0%, rgba(60, 179, 113, 0.1) 100%);
        z-index: -1;
    }
    
    /* Hero section */
    .hero-section {
        text-align: center;
        padding: 2rem 1rem;
        background: linear-gradient(135deg, #2E8B57 0%, #3CB371 100%);
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(46, 139, 87, 0.3);
    }
    
    .hero-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
        opacity: 0.95;
        font-weight: 400;
    }
    
    /* Centered Login Modal */
    .auth-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 3rem 2.5rem;
        border-radius: 20px;
        box-shadow: 0 15px 50px rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(224, 224, 224, 0.5);
        margin: 0 auto;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #F5F5F5;
        border-radius: 10px;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #2E8B57 !important;
        color: white !important;
    }
    
    /* Password strength indicator */
    .password-strength {
        height: 5px;
        border-radius: 3px;
        margin-top: 5px;
        transition: all 0.3s ease;
    }
    
    .strength-0 { width: 25%; background-color: #F44336; }
    .strength-1 { width: 50%; background-color: #FF9800; }
    .strength-2 { width: 75%; background-color: #FFC107; }
    .strength-3 { width: 100%; background-color: #4CAF50; }
    
    /* Input field styling with icons */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #E0E0E0;
        padding: 12px 15px 12px 45px;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #2E8B57;
        box-shadow: 0 0 0 3px rgba(46, 139, 87, 0.1);
        transform: translateY(-1px);
    }
    
    /* Input field icons simulation via label */
    .stTextInput > label {
        font-weight: 600;
        color: #2E8B57;
        margin-bottom: 8px;
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #2E8B57 0%, #3CB371 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 15px 30px;
        font-size: 18px;
        font-weight: 700;
        box-shadow: 0 5px 15px rgba(46, 139, 87, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(46, 139, 87, 0.4);
    }
    
    /* Progress steps */
    .progress-steps {
        display: flex;
        justify-content: space-between;
        margin-bottom: 2rem;
        padding: 0 1rem;
    }
    
    .step {
        flex: 1;
        text-align: center;
        position: relative;
    }
    
    .step-circle {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: #E0E0E0;
        color: #666;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        margin-bottom: 8px;
    }
    
    .step-active .step-circle {
        background: #2E8B57;
        color: white;
        box-shadow: 0 3px 10px rgba(46, 139, 87, 0.3);
    }
    
    .step-complete .step-circle {
        background: #4CAF50;
        color: white;
    }
    
    .step-label {
        font-size: 12px;
        color: #666;
        font-weight: 500;
    }
    
    .step-active .step-label {
        color: #2E8B57;
        font-weight: 700;
    }
    
    /* Info boxes */
    .info-box {
        background: #E8F5E9;
        border-left: 4px solid #4CAF50;
        padding: 15px;
        border-radius: 8px;
        margin: 15px 0;
    }
    
    .warning-box {
        background: #FFF3E0;
        border-left: 4px solid #FF9800;
        padding: 15px;
        border-radius: 8px;
        margin: 15px 0;
    }
    
    /* Admin login section */
    .admin-section {
        margin-top: 2rem;
        padding-top: 2rem;
        border-top: 2px dashed #E0E0E0;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Hero Section - Using Streamlit native components
    st.markdown("# 🌾 Smart Farmer Marketplace")
    st.markdown(f"### {t('Empowering Farmers, Connecting Communities')}")
    st.markdown("---")
    
    # Tabs for Login and Registration
    tab1, tab2 = st.tabs([f"👤 {t('Login')}", f"🌱 {t('New Farmer Registration')}"])
    
    # ========================================
    # TAB 1: EXISTING FARMER LOGIN
    # ========================================
    with tab1:
        # Centered login box with visual appeal
        st.markdown(f"""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h2 style='color: #2E8B57; margin-bottom: 0.5rem;'>🌾 {t('FARMER LOGIN').upper()}</h2>
            <p style='color: #666; font-size: 1rem;'>{t('Enter your credentials to access your dashboard')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Initialize login state
        if 'login_state' not in st.session_state:
            st.session_state.login_state = 'idle'  # idle, loading, success, error
        
        with st.form("login_form"):
            farmer_name = st.text_input(
                f"👤 {t('Username')}",
                placeholder=t("Enter your name"),
                help=t("Use the name you registered with"),
                key="login_username"
            )
            
            farmer_password = st.text_input(
                f"🔒 {t('Password')}",
                type="password",
                placeholder=t("Enter your password"),
                help=t("Enter your secure password"),
                key="login_password"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            login_button = st.form_submit_button(
                f"🌱 {t('Login')}",
                use_container_width=True,
                type="primary"
            )
            
            if login_button:
                if farmer_name and farmer_password:
                    # LOADING STATE
                    st.session_state.login_state = 'loading'
                    with st.spinner("⏳ Verifying credentials..."):
                        farmer_profile = verify_farmer_login(farmer_name.strip(), farmer_password)
                        
                        if farmer_profile:
                            # SUCCESS STATE
                            st.session_state.login_state = 'success'
                            st.session_state.logged_in = True
                            st.session_state.role = "Farmer"
                            st.session_state.farmer_name = farmer_profile['name']
                            st.session_state.farmer_profile = farmer_profile
                            st.session_state.first_login = False
                            
                            st.success("✅ Login Success! Redirecting...")
                            st.balloons()
                            st.rerun()
                        else:
                            # ERROR STATE
                            st.session_state.login_state = 'error'
                            st.error("❌ Invalid Login")
                            st.warning("Please check your username and password and try again.")
                else:
                    st.warning("⚠️ Please enter both username and password")
        
        # Registration link
        st.markdown("""
        <div style='text-align: center; margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid #E0E0E0;'>
            <p style='color: #666;'>New user? <strong style='color: #2E8B57;'>Switch to Registration tab above</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    # ========================================
    # TAB 2: NEW FARMER REGISTRATION
    # ========================================
    with tab2:
        st.markdown("### Join Our Farming Community! 🌱")
        st.markdown("Create your account in just a few simple steps")
        
        # Initialize registration step if not exists
        if 'reg_step' not in st.session_state:
            st.session_state.reg_step = 1
        if 'reg_data' not in st.session_state:
            st.session_state.reg_data = {}
        
        # Progress Steps Indicator
        steps = [
            ("1", "Basic Info"),
            ("2", "Farm & Location"),
            ("3", "Create Account"),
            ("4", "Complete")
        ]
        
        # Progress indicator using columns
        progress_cols = st.columns(4)
        for i, (num, label) in enumerate(steps):
            with progress_cols[i]:
                step_num = i + 1
                if step_num < st.session_state.reg_step:
                    st.success(f"✓ {label}")
                elif step_num == st.session_state.reg_step:
                    st.info(f"**{num}. {label}**")
                else:
                    st.text(f"{num}. {label}")
        
        # ========================================
        # STEP 1: BASIC INFO
        # ========================================
        if st.session_state.reg_step == 1:
            st.markdown("#### 📝 Step 1: Basic Information")
            
            with st.form("step1_form"):
                st.info("👤 **Tell us about yourself** - This information will be used to create your farmer profile")
                
                name = st.text_input(
                    "Your Name *",
                    placeholder="e.g., Ramesh Patil",
                    help="Enter your full name as you'd like it to appear",
                    value=st.session_state.reg_data.get('name', '')
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    password = st.text_input(
                        "Create Password *",
                        type="password",
                        placeholder="Min. 4 characters",
                        help="Choose a secure password"
                    )
                    
                    if password:
                        strength, label = check_password_strength(password)
                        if strength == 0:
                            st.error(f"Password strength: {label}")
                        elif strength == 1:
                            st.warning(f"Password strength: {label}")
                        elif strength == 2:
                            st.info(f"Password strength: {label}")
                        else:
                            st.success(f"Password strength: {label}")
                
                with col2:
                    confirm_password = st.text_input(
                        "Confirm Password *",
                        type="password",
                        placeholder="Re-enter password",
                        help="Must match the password above"
                    )
                
                contact = st.text_input(
                    "Mobile Number *",
                    placeholder="e.g., 9876543210",
                    help="Your contact number for marketplace communications",
                    value=st.session_state.reg_data.get('contact', '')
                )
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    next_button = st.form_submit_button("Next: Farm Details →", use_container_width=True)
                
                if next_button:
                    # Validation
                    errors = []
                    if not name or not name.strip():
                        errors.append("Name is required")
                    if not password:
                        errors.append("Password is required")
                    elif len(password) < 4:
                        errors.append("Password must be at least 4 characters")
                    if password != confirm_password:
                        errors.append("Passwords do not match")
                    if not contact or not contact.strip():
                        errors.append("Contact number is required")
                    
                    if errors:
                        for error in errors:
                            st.error(f"❌ {error}")
                    else:
                        # Save step 1 data
                        st.session_state.reg_data['name'] = name.strip()
                        st.session_state.reg_data['password'] = password
                        st.session_state.reg_data['contact'] = contact.strip()
                        st.session_state.reg_step = 2
                        st.rerun()
        
        # ========================================
        # STEP 2: FARM DETAILS WITH LOCATION
        # ========================================
        elif st.session_state.reg_step == 2:
            st.markdown("#### 🌾 Step 2: Farm Details & Location")
            
            st.info("🚜 **Tell us about your farm and location** - We'll get your GPS coordinates for weather, market prices, and location services")
            
            # Farm Size and Unit (outside form for better UX)
            col1, col2 = st.columns(2)
            with col1:
                farm_size = st.number_input(
                    "Farm Size *",
                    min_value=0.0,
                    format="%.2f",
                    help="Enter the size of your farm",
                    value=st.session_state.reg_data.get('farm_size', 0.0),
                    key="reg_farm_size"
                )
            
            with col2:
                farm_unit = st.selectbox(
                    "Unit *",
                    ["Acres", "Hectares"],
                    help="Choose the unit of measurement",
                    index=0 if st.session_state.reg_data.get('farm_unit', 'Acres') == 'Acres' else 1,
                    key="reg_farm_unit"
                )
            
            st.markdown("---")
            st.markdown("#### 📍 Farm Location Setup")
            
            # Location method selection
            location_method = st.radio(
                "How would you like to set your location?",
                ["📝 Enter Location Manually", "🧭 Use GPS Auto-Detect"],
                help="Choose your preferred method to set your farm location",
                key="location_method_radio"
            )
            
            # Initialize session state for coordinates if not exists
            if 'temp_coordinates' not in st.session_state:
                st.session_state.temp_coordinates = None
            if 'temp_location_name' not in st.session_state:
                st.session_state.temp_location_name = None
            
            if location_method == "📝 Enter Location Manually":
                st.markdown("**Enter your farm location and we'll find the GPS coordinates**")
                
                location = st.text_input(
                    "Farm Location *",
                    placeholder="e.g., Wadgaon Sheri, Pune, Maharashtra",
                    help="Enter your village, city, district, and state for best results",
                    value=st.session_state.reg_data.get('location', ''),
                    key="manual_location_input"
                )
                
                if st.button("🔍 Find My Location", use_container_width=True, type="primary", key="find_coords_btn"):
                    if location and location.strip():
                        with st.spinner("🔍 Finding your location..."):
                            try:
                                ai_client = AIClient()
                                coords = ai_client.get_coordinates_from_google_search(location.strip())
                                
                                if coords:
                                    st.session_state.temp_coordinates = coords
                                    st.session_state.temp_location_name = location.strip()
                                    
                                    # Get full address confirmation using Google Maps
                                    with st.spinner("📍 Verifying your location with Google Maps..."):
                                        try:
                                            from components.location_manager import LocationManager
                                            location_manager = LocationManager()
                                            address_info = location_manager.get_address_from_coordinates(coords['lat'], coords['lon'])
                                            
                                            if address_info:
                                                st.success("✅ **Location Found!**")
                                                st.info(f"📍 **You live at:** {address_info['full_address']}")
                                                st.success(f"🌐 **GPS Coordinates:** {coords['lat']:.6f}, {coords['lon']:.6f}")
                                                
                                                if 'sources' in address_info and address_info['sources']:
                                                    with st.expander("🗺️ View on Google Maps"):
                                                        for source in address_info['sources']:
                                                            st.markdown(f"- [{source['title']}]({source['uri']})")
                                            else:
                                                st.success(f"✅ Found coordinates: {coords['lat']:.6f}, {coords['lon']:.6f}")
                                                st.info(f"📍 Location: {location.strip()}")
                                        except Exception as e:
                                            st.success(f"✅ Found coordinates: {coords['lat']:.6f}, {coords['lon']:.6f}")
                                            st.info(f"📍 Location: {location.strip()}")
                                else:
                                    st.error("❌ Could not find this location. Please check spelling and try again.")
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                    else:
                        st.warning("⚠️ Please enter a location first")
                
                # Show saved coordinates if available
                if st.session_state.temp_coordinates:
                    st.markdown("---")
                    st.success("✅ **Location Ready!** You can now proceed to the next step.")
                    st.info(f"📍 **Your Location:** {st.session_state.temp_location_name}\n\n🌐 **Coordinates:** {st.session_state.temp_coordinates['lat']:.6f}, {st.session_state.temp_coordinates['lon']:.6f}")
            
            else:  # GPS Auto-detect (location_method == "🧭 Use GPS Auto-Detect")
                # Initialize session state for GPS coordinates
                if 'gps_detected_lat' not in st.session_state:
                    st.session_state.gps_detected_lat = 0.0
                if 'gps_detected_lon' not in st.session_state:
                    st.session_state.gps_detected_lon = 0.0
                
                # Show saved location if already detected
                if st.session_state.temp_coordinates and st.session_state.temp_location_name:
                    st.success("✅ **Location Set Successfully!**")
                    
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.markdown(f"**📍 Your Farm Location:**")
                        st.write(f"{st.session_state.temp_location_name}")
                        st.caption(f"🌐 Coordinates: {st.session_state.temp_coordinates['lat']:.6f}, {st.session_state.temp_coordinates['lon']:.6f}")
                    with col2:
                        if st.button("🔄 Change Location", use_container_width=True):
                            st.session_state.temp_coordinates = None
                            st.session_state.temp_location_name = None
                            st.session_state.gps_detected_lat = 0.0
                            st.session_state.gps_detected_lon = 0.0
                            st.rerun()
                
                else:
                    # Step 1: GPS Detection using Streamlit Geolocation
                    st.markdown("**Step 1️⃣: Detect Your GPS Location**")
                    
                    # Import streamlit-geolocation
                    from streamlit_geolocation import streamlit_geolocation
                    
                    # Compact instruction box
                    st.markdown("""
                    <div style='background: linear-gradient(135deg, #2E8B57 0%, #3CB371 100%); 
                                padding: 12px 20px; 
                                border-radius: 10px; 
                                margin-bottom: 15px;
                                box-shadow: 0 4px 10px rgba(46, 139, 87, 0.3);
                                border: 2px solid #1d5d3a;'>
                        <p style='color: white; font-size: 15px; margin: 0; text-align: center; font-weight: 600;'>
                            📍 Click the Button Below to Detect GPS
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Get location from device - this creates a visible button
                    location = streamlit_geolocation()
                    
                    # Check if location was retrieved
                    if location and location.get('latitude') and location.get('longitude'):
                        st.session_state.gps_detected_lat = location['latitude']
                        st.session_state.gps_detected_lon = location['longitude']
                        st.success(f"✅ GPS Detected Successfully: {location['latitude']:.6f}, {location['longitude']:.6f}")
                    
                    # Step 2: Verify and Use Coordinates
                    if st.session_state.gps_detected_lat != 0.0 and st.session_state.gps_detected_lon != 0.0:
                        st.markdown("---")
                        st.markdown("**Step 2️⃣: Verify & Use Coordinates**")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("📍 Latitude", f"{st.session_state.gps_detected_lat:.6f}")
                        with col2:
                            st.metric("📍 Longitude", f"{st.session_state.gps_detected_lon:.6f}")
                        
                        if st.button("✅ Use These Coordinates to Find My Address", use_container_width=True, type="primary", key="use_gps_btn"):
                            with st.spinner("🔍 Finding your location address..."):
                                try:
                                    ai_client = AIClient()
                                    location_info = ai_client.get_location_from_coordinates(
                                        st.session_state.gps_detected_lat, 
                                        st.session_state.gps_detected_lon
                                    )
                                    
                                    if location_info and 'address' in location_info:
                                        # Save coordinates and location
                                        st.session_state.temp_coordinates = {
                                            'lat': st.session_state.gps_detected_lat, 
                                            'lon': st.session_state.gps_detected_lon
                                        }
                                        st.session_state.temp_location_name = location_info.get('address', 
                                            f"{st.session_state.gps_detected_lat}, {st.session_state.gps_detected_lon}")
                                        
                                        st.success("✅ **Location Found!**")
                                        
                                        # Show verification in a nice box
                                        st.markdown("---")
                                        st.markdown("**🔍 Please verify this is your farm location:**")
                                        
                                        with st.container():
                                            st.markdown(f"**📍 Address:** {location_info.get('address', 'Unknown')}")
                                            
                                            if 'city' in location_info or 'state' in location_info or 'country' in location_info:
                                                col1, col2, col3 = st.columns(3)
                                                with col1:
                                                    if 'city' in location_info:
                                                        st.write(f"🏘️ {location_info.get('city', 'N/A')}")
                                                with col2:
                                                    if 'state' in location_info:
                                                        st.write(f"🗺️ {location_info.get('state', 'N/A')}")
                                                with col3:
                                                    if 'country' in location_info:
                                                        st.write(f"🌏 {location_info.get('country', 'N/A')}")
                                        
                                        st.info("✅ If this is correct, click 'Next' below to continue!")
                                        st.rerun()
                                    else:
                                        st.error("❌ Could not determine location. Please try again or use manual entry.")
                                except Exception as e:
                                    st.error(f"❌ Error: {str(e)}")
                    else:
                        st.info("👆 Click the 'Detect My Location Now' button above to start")
            
            # Navigation buttons
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Back", use_container_width=True, key="step2_back"):
                    st.session_state.reg_step = 1
                    st.session_state.temp_coordinates = None
                    st.session_state.temp_location_name = None
                    st.rerun()
            
            with col2:
                if st.button("Next: Complete Registration →", use_container_width=True, type="primary", key="step2_next"):
                    # Validation
                    errors = []
                    
                    if farm_size <= 0:
                        errors.append("Farm size must be greater than 0")
                    
                    if not st.session_state.temp_coordinates or not st.session_state.temp_location_name:
                        errors.append("Please set your location and get GPS coordinates first")
                    
                    if errors:
                        for error in errors:
                            st.error(f"❌ {error}")
                    else:
                        # Save all data including coordinates
                        st.session_state.reg_data['location'] = st.session_state.temp_location_name
                        st.session_state.reg_data['weather_location'] = st.session_state.temp_location_name
                        st.session_state.reg_data['farm_size'] = farm_size
                        st.session_state.reg_data['farm_unit'] = farm_unit
                        st.session_state.reg_data['latitude'] = st.session_state.temp_coordinates['lat']
                        st.session_state.reg_data['longitude'] = st.session_state.temp_coordinates['lon']
                        
                        # Clear temp data
                        st.session_state.temp_coordinates = None
                        st.session_state.temp_location_name = None
                        
                        # Move to completion step
                        st.session_state.reg_step = 3
                        st.rerun()
        
        # ========================================
        # STEP 3: ACCOUNT CREATION & COMPLETION
        # ========================================
        elif st.session_state.reg_step == 3:
            st.markdown("#### 🎉 Step 3: Create Your Account")
            
            st.info("✅ **Review your information before creating your account**")
            
            # Display collected information
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**👤 Personal Information**")
                st.text(f"Name: {st.session_state.reg_data.get('name', 'N/A')}")
                st.text(f"Contact: {st.session_state.reg_data.get('contact', 'N/A')}")
                st.text(f"Password: {'*' * len(st.session_state.reg_data.get('password', ''))}")
            
            with col2:
                st.markdown("**🚜 Farm Information**")
                st.text(f"Farm Size: {st.session_state.reg_data.get('farm_size', 0)} {st.session_state.reg_data.get('farm_unit', 'Acres')}")
                st.text(f"Location: {st.session_state.reg_data.get('location', 'N/A')}")
            
            st.markdown("**📍 GPS Coordinates**")
            st.text(f"Latitude: {st.session_state.reg_data.get('latitude', 0.0):.6f}")
            st.text(f"Longitude: {st.session_state.reg_data.get('longitude', 0.0):.6f}")
            
            st.success("🗺️ **Your location is ready!** These coordinates will be used for weather, market prices, and location services.")
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Back to Edit", use_container_width=True, key="step3_back"):
                    st.session_state.reg_step = 2
                    st.rerun()
            
            with col2:
                if st.button("🎉 Create My Account", use_container_width=True, type="primary", key="create_account_btn"):
                    # Show progress
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Save to database
                    status_text.text("💾 Creating your profile...")
                    progress_bar.progress(50)
                    
                    farmer_data = (
                        st.session_state.reg_data['name'],
                        st.session_state.reg_data['location'],
                        st.session_state.reg_data['farm_size'],
                        st.session_state.reg_data['farm_unit'],
                        st.session_state.reg_data['contact'],
                        st.session_state.reg_data['weather_location'],
                        st.session_state.reg_data['latitude'],
                        st.session_state.reg_data['longitude'],
                        st.session_state.reg_data['password']
                    )
                    
                    try:
                        add_data("farmers", farmer_data)
                        progress_bar.progress(100)
                        status_text.text("✅ Profile created successfully!")
                        
                        # Move to completion step
                        st.session_state.reg_step = 4
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error creating profile: {str(e)}")
                        st.error("This name may already be registered. Please try a different name.")
        
        # ========================================
        # STEP 4: COMPLETION
        # ========================================
        elif st.session_state.reg_step == 4:
            st.markdown("#### 🎉 Registration Complete!")
            
            st.success("✅ **Welcome to Smart Farmer Marketplace!**")
            st.write("Your account has been created successfully. You can now:")
            st.write("- ✅ List tools and crops in the marketplace")
            st.write("- ✅ Check weather forecasts for your location")
            st.write("- ✅ Plan farming activities using the calendar")
            st.write("- ✅ Track market prices")
            st.write("- ✅ Connect with other farmers")
            
            st.markdown("### 📋 Your Profile Summary")
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**👤 Name:** {st.session_state.reg_data['name']}")
                st.info(f"**📍 Location:** {st.session_state.reg_data['location']}")
                st.info(f"**🌍 Weather Location:** {st.session_state.reg_data['weather_location']}")
            with col2:
                st.info(f"**🚜 Farm Size:** {st.session_state.reg_data['farm_size']} {st.session_state.reg_data['farm_unit']}")
                st.info(f"**📞 Contact:** {st.session_state.reg_data['contact']}")
            
            if st.button("🌱 Go to Login", use_container_width=True, type="primary"):
                # Clear registration data and switch to login tab
                st.session_state.reg_step = 1
                st.session_state.reg_data = {}
                st.session_state.auth_mode = "login"  # Switch to login tab
                st.rerun()
    
    # ========================================
    # ADMIN LOGIN SECTION
    # ========================================
    st.markdown("---")
    st.markdown("### 👨‍💼 Admin Access")
    
    with st.expander("🔐 Admin Login", expanded=False):
        with st.form("admin_login_form"):
            admin_password = st.text_input(
                "Admin Password",
                type="password",
                placeholder="Enter admin password"
            )
            
            admin_login = st.form_submit_button("Login as Admin", use_container_width=True)
            
            if admin_login:
                if admin_password == "admin":
                    st.session_state.logged_in = True
                    st.session_state.role = "Admin"
                    st.session_state.farmer_name = "Admin"
                    st.success("✅ Logged in as Admin!")
                    st.rerun()
                elif admin_password:
                    st.error("❌ Incorrect admin password")


