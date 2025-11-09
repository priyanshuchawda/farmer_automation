# components/auth_page.py
"""
Dedicated Login and Registration Page for Smart Farmer Marketplace
Phase 1: Complete Login & Authentication Overhaul
"""

import streamlit as st
from database.db_functions import verify_farmer_login, add_data, get_farmer_profile
from weather.ai_client import AIClient
from datetime import datetime

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
        st.markdown("## 🌾 Welcome!")
        st.info("**Smart Farmer Marketplace**\n\nPlease login or register to continue.")
        st.markdown("---")
        st.markdown("### 🌟 Features")
        st.write("✅ Marketplace for tools & crops")
        st.write("🌤️ Weather forecasts")
        st.write("📅 Smart calendar")
        st.write("💰 Market prices")
        st.write("🤖 AI assistance")
    
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
    st.markdown("### Empowering Farmers, Connecting Communities")
    st.markdown("---")
    
    # Tabs for Login and Registration
    tab1, tab2 = st.tabs(["👤 Login", "🌱 New Farmer Registration"])
    
    # ========================================
    # TAB 1: EXISTING FARMER LOGIN
    # ========================================
    with tab1:
        # Centered login box with visual appeal
        st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h2 style='color: #2E8B57; margin-bottom: 0.5rem;'>🌾 FARMER LOGIN</h2>
            <p style='color: #666; font-size: 1rem;'>Enter your credentials to access your dashboard</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Initialize login state
        if 'login_state' not in st.session_state:
            st.session_state.login_state = 'idle'  # idle, loading, success, error
        
        with st.form("login_form"):
            farmer_name = st.text_input(
                "👤 Username",
                placeholder="Enter your name",
                help="Use the name you registered with",
                key="login_username"
            )
            
            farmer_password = st.text_input(
                "🔒 Password",
                type="password",
                placeholder="Enter your password",
                help="Enter your secure password",
                key="login_password"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            login_button = st.form_submit_button(
                "🌱 Login",
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
            ("2", "Farm Details"),
            ("3", "Weather Setup"),
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
        # STEP 2: FARM DETAILS
        # ========================================
        elif st.session_state.reg_step == 2:
            st.markdown("#### 🌾 Step 2: Farm Details")
            
            with st.form("step2_form"):
                st.info("🚜 **Tell us about your farm** - This helps us provide relevant information and connect you with nearby farmers")
                
                location = st.text_input(
                    "Farm Location *",
                    placeholder="e.g., Wadgaon Sheri, Pune",
                    help="Village/City where your farm is located",
                    value=st.session_state.reg_data.get('location', '')
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    farm_size = st.number_input(
                        "Farm Size *",
                        min_value=0.0,
                        format="%.2f",
                        help="Enter the size of your farm",
                        value=st.session_state.reg_data.get('farm_size', 0.0)
                    )
                
                with col2:
                    farm_unit = st.selectbox(
                        "Unit *",
                        ["Acres", "Hectares"],
                        help="Choose the unit of measurement",
                        index=0 if st.session_state.reg_data.get('farm_unit', 'Acres') == 'Acres' else 1
                    )
                
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    back_button = st.form_submit_button("← Back", use_container_width=True)
                with col2:
                    next_button = st.form_submit_button("Next: Weather Setup →", use_container_width=True)
                
                if back_button:
                    st.session_state.reg_step = 1
                    st.rerun()
                
                if next_button:
                    # Validation
                    errors = []
                    if not location or not location.strip():
                        errors.append("Farm location is required")
                    if farm_size <= 0:
                        errors.append("Farm size must be greater than 0")
                    
                    if errors:
                        for error in errors:
                            st.error(f"❌ {error}")
                    else:
                        # Save step 2 data
                        st.session_state.reg_data['location'] = location.strip()
                        st.session_state.reg_data['farm_size'] = farm_size
                        st.session_state.reg_data['farm_unit'] = farm_unit
                        st.session_state.reg_step = 3
                        st.rerun()
        
        # ========================================
        # STEP 3: WEATHER SETUP
        # ========================================
        elif st.session_state.reg_step == 3:
            st.markdown("#### 🌤️ Step 3: Weather Location Setup")
            
            with st.form("step3_form"):
                st.info("🌍 **Weather Integration** - We'll fetch weather forecasts for your location to help you plan farming activities")
                
                weather_location = st.text_input(
                    "Weather Location *",
                    placeholder="e.g., Pune, Maharashtra",
                    help="City/District for weather forecasts (can be same as farm location)",
                    value=st.session_state.reg_data.get('weather_location', st.session_state.reg_data.get('location', ''))
                )
                
                st.info("💡 **Tip:** Use the same location as your farm, or specify a nearby major city for more accurate weather data")
                
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    back_button = st.form_submit_button("← Back", use_container_width=True)
                with col2:
                    create_button = st.form_submit_button("🎉 Create My Account", use_container_width=True)
                
                if back_button:
                    st.session_state.reg_step = 2
                    st.rerun()
                
                if create_button:
                    if not weather_location or not weather_location.strip():
                        st.error("❌ Weather location is required")
                    else:
                        st.session_state.reg_data['weather_location'] = weather_location.strip()
                        
                        # Show progress
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        # Fetch coordinates
                        status_text.text("📍 Getting coordinates for your location...")
                        progress_bar.progress(30)
                        
                        latitude = None
                        longitude = None
                        
                        try:
                            ai_client = AIClient()
                            coords = ai_client.get_coordinates_from_google_search(weather_location.strip())
                            
                            if coords:
                                latitude = coords['lat']
                                longitude = coords['lon']
                                status_text.text(f"✅ Coordinates found: {latitude:.4f}, {longitude:.4f}")
                                progress_bar.progress(60)
                            else:
                                status_text.text("⚠️ Could not fetch coordinates, saving without them")
                                progress_bar.progress(60)
                        except Exception as e:
                            status_text.text(f"⚠️ Error: {str(e)}, saving without coordinates")
                            progress_bar.progress(60)
                        
                        # Save to database
                        status_text.text("💾 Creating your profile...")
                        progress_bar.progress(80)
                        
                        farmer_data = (
                            st.session_state.reg_data['name'],
                            st.session_state.reg_data['location'],
                            st.session_state.reg_data['farm_size'],
                            st.session_state.reg_data['farm_unit'],
                            st.session_state.reg_data['contact'],
                            st.session_state.reg_data['weather_location'],
                            latitude,
                            longitude,
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
                # Clear registration data
                st.session_state.reg_step = 1
                st.session_state.reg_data = {}
                st.success("✅ You can now login with your credentials!")
                st.balloons()
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


