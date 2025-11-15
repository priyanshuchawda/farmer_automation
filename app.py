import streamlit as st
import pandas as pd
from datetime import date
from dotenv import load_dotenv
import os

# Smart environment loading: Works both locally and on Streamlit Cloud
# Locally → .env is used
# On Cloud → Streamlit Secrets are used
if os.getenv("STREAMLIT_RUNTIME") is None:
    load_dotenv()  # Load .env only if running locally

# ----------------------------------------
# --- 0. MODULE IMPORTS ---
# ----------------------------------------
from database.db_functions import (
    init_db, get_data, add_data, get_farmer_profile, verify_farmer_login,
    get_onboarding_progress, update_onboarding_progress
)
from components.auth_page import render_auth_page
from components.home_page import render_home_page, render_db_check
from components.tool_listings import render_tool_listing, render_tool_management
from components.crop_listings import render_crop_listing, render_crop_management
from components.labor_board import render_labor_board
from components.profiles_page import render_profiles_page
from components.view_profile_page import render_view_profile_page
from components.weather_component import render_weather_component
from components.market_price_scraper import render_market_price
from components.simple_price_advisor import render_simple_price_advisor
from components.cache_admin_page import render_cache_admin_page
from components.government_schemes_page import render_government_schemes_page
from components.simple_finance_page import render_simple_finance_page
from components.translation_utils import render_language_selector, t
from components.pwa_component import inject_pwa_code
from components.offline_manager import render_offline_status
from components.performance_optimizer import init_performance_optimizations
from components.notification_manager import init_notifications
from components.voice_chatbot import render_voice_chatbot
from calender.calendar_component import render_calendar
from calender.config import TRANSLATIONS
from calender.utils import get_events_for_date

# ----------------------------------------
# --- CONFIGURATION AND SETUP ---
# ----------------------------------------

# 1. Database Initialization
if 'db_initialized' not in st.session_state:
    init_db()
    init_performance_optimizations()
    st.session_state.db_initialized = True

# 2. Page Config
st.set_page_config(
    page_title="AI Climate-Smart Agriculture", 
    page_icon="🌍", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2.5 Inject PWA Support
inject_pwa_code()

# 2.6 Initialize Notifications
init_notifications()

# 3. Custom CSS for styling with mobile responsiveness
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    body { 
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #f8f9fa;
    }
    h1,h2,h3 { 
        color:#2E8B57; 
        text-align:center; 
        font-weight:600; 
        letter-spacing: -0.02em;
    }
    .stApp {
        background-color: #f8f9fa;
    }
    [data-testid="stSidebar"] { 
        background-color:#FFFFFF; 
        border-right:1px solid #E8E8E8; 
        padding-top:20px;
        box-shadow: 2px 0 8px rgba(0,0,0,0.04);
    }
    
    /* Button Styling */
    .stButton>button { 
        background-color:#2E8B57; 
        color:white; 
        border-radius:10px; 
        padding:12px 24px; 
        font-weight:600; 
        border:none; 
        box-shadow:0 2px 8px rgba(46,139,87,0.15); 
        width:100%; 
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        font-size: 15px;
    }
    .stButton>button:hover { 
        background-color:#3CB371; 
        box-shadow:0 4px 16px rgba(46,139,87,0.25);
        transform: translateY(-2px);
    }
    
    /* Primary Button */
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #4CAF50 0%, #2E8B57 100%);
        box-shadow:0 4px 12px rgba(46,139,87,0.3);
    }
    
    /* Card Styling */
    .card { 
        background-color:#ffffff; 
        padding:28px; 
        margin-bottom:20px; 
        border-radius:12px; 
        box-shadow:0 2px 12px rgba(0,0,0,0.08); 
        border-left:4px solid #4CAF50; 
        transition: all 0.3s ease;
    }
    
    .card:hover {
        box-shadow:0 4px 20px rgba(0,0,0,0.12);
    }
    
    footer { 
        visibility:hidden; 
    }
    .stDataFrame, .stDataEditor { 
        border:1px solid #E8E8E8; 
        border-radius:10px; 
        padding:12px; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    
    /* Input styling */
    .stTextInput>div>div>input, .stSelectbox>div>div>select, .stTextArea>div>div>textarea {
        border-radius: 8px;
        border: 1px solid #E0E0E0;
        padding: 10px;
        font-size: 15px;
    }
    
    /* Mobile Responsive Styles */
    @media (max-width: 768px) {
        /* Adjust titles for mobile */
        h1 { 
            font-size: 1.75rem !important; 
            padding: 10px 5px !important;
        }
        h2 { 
            font-size: 1.4rem !important; 
        }
        h3 { 
            font-size: 1.2rem !important; 
        }
        
        /* Card padding adjustment */
        .card { 
            padding: 18px !important; 
            margin-bottom: 16px !important;
            border-radius: 10px !important;
            border-left-width: 3px !important;
        }
        
        /* Button adjustments */
        .stButton>button { 
            padding: 10px 18px !important; 
            font-size: 14px !important;
        }
        
        /* Sidebar adjustments */
        [data-testid="stSidebar"] { 
            padding: 10px !important;
        }
        
        /* Column layouts - stack on mobile */
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }
        
        /* Tables and dataframes */
        .stDataFrame, .stDataEditor { 
            overflow-x: auto !important;
            font-size: 0.85rem !important;
        }
        
        /* Input fields */
        .stTextInput>div>div>input,
        .stTextArea>div>div>textarea,
        .stSelectbox>div>div>select {
            font-size: 16px !important; /* Prevents zoom on iOS */
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 5px !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 8px 12px !important;
            font-size: 0.9rem !important;
        }
        
        /* Metrics */
        [data-testid="stMetricValue"] {
            font-size: 1.5rem !important;
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            font-size: 0.95rem !important;
        }
    }
    
    /* Tablet adjustments */
    @media (min-width: 769px) and (max-width: 1024px) {
        h1 { font-size: 2rem !important; }
        h2 { font-size: 1.7rem !important; }
        
        .card { 
            padding: 20px !important; 
        }
    }
    
    /* Extra small devices (phones in portrait) */
    @media (max-width: 480px) {
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.3rem !important; }
        h3 { font-size: 1.1rem !important; }
        
        .card { 
            padding: 10px !important;
            border-radius: 8px !important;
        }
        
        .stButton>button { 
            padding: 6px 12px !important; 
            font-size: 0.85rem !important;
        }
    }
    
    /* Ensure touch-friendly interactive elements */
    @media (hover: none) and (pointer: coarse) {
        .stButton>button,
        .stSelectbox,
        .stTextInput,
        [data-baseweb="tab"] {
            min-height: 44px !important; /* Apple's recommended touch target */
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 4. Persistent Database Loading
st.session_state.tools = get_data("tools")
st.session_state.crops = get_data("crops")


# ----------------------------------------
# --- AUTHENTICATION CHECK ---
# ----------------------------------------
# Check if user is logged in
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    # Show authentication page
    render_auth_page()
    st.stop()  # Stop execution here if not logged in

# ----------------------------------------
# --- MAIN APPLICATION (After Login) ---
# ----------------------------------------
st.title("🌍 AI Climate-Smart Agriculture Platform")

st.markdown("""
<div style='background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
            padding: 16px; border-radius: 12px; text-align: center; margin-bottom: 20px; 
            border: 2px solid #1976D2; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
    <h4 style='color: #0D47A1; margin: 0 0 8px 0; font-weight: 700;'>
        🤖 Multi-Modal AI • 🌡️ Climate Risk Detection • 🛰️ Satellite Integration • SDG 13 Aligned
    </h4>
    <p style='color: #1565C0; margin: 0; font-size: 14px;'>
        Helping farmers adapt to climate change through intelligent agriculture technology
    </p>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------
# --- REORGANIZED MENU STRUCTURE ---
# ----------------------------------------
# ----------------------------------------
# --- MENU STRUCTURE ---
# ----------------------------------------
# Build menu based on user role - Define structure first
user_role = st.session_state.get("role", "User")

if user_role == "Farmer":
    # Farmer Menu - CLIMATE-FIRST ORGANIZATION
    menu_structure = [
        ("🌍 CLIMATE INTELLIGENCE", [
            "🏠 Home",
            "🌡️ Climate Risk Dashboard",
            "🌾 Climate-Smart Crops",
            "💧 Water & Carbon Tracker"
        ]),
        ("🤖 AI TOOLS", [
            "🗣️ Ask Advisor",
            "🌤️ Weather Forecast",
            "💰 Today's Market Price",
            "🤔 Should I Sell?"
        ]),
        ("🛍️ MARKETPLACE", [
            "🛍️ Browse Listings",
            "➕ Post Listing",
            "🎤 Voice Listing (NEW)"
        ]),
        ("📅 MY FARM", [
            "📅 My Calendar",
            "📒 My Money Diary",
            "👤 My Profile",
            "📦 My Listings"
        ]),
        ("ℹ️ HELP", [
            "🏛️ Government Schemes"
        ])
    ]
else:
    # Admin Menu - Keep climate focus for admins too
    menu_structure = [
        ("🏠 DASHBOARD", ["🏠 Home"]),
        ("🌍 CLIMATE TOOLS", [
            "🌡️ Climate Risk Dashboard",
            "🌾 Climate-Smart Crops",
            "💧 Water & Carbon Tracker"
        ]),
        ("🤖 AI TOOLS", [
            "🗣️ Ask Advisor",
            "🌤️ Weather Forecast",
            "💰 Today's Market Price",
            "🤔 Should I Sell?"
        ]),
        ("👨‍💼 ADMIN TOOLS", [
            "👥 Manage Farmers", 
            "🗄️ Database Viewer", 
            "💾 Cache Management"
        ]),
        ("🛍️ MARKETPLACE", [
            "🛍️ Browse Listings",
            "➕ Post Listing"
        ]),
        ("👤 MY ACCOUNT", [
            "👤 My Profile",
            "📦 My Listings"
        ]),
        ("ℹ️ HELP", [
            "🏛️ Government Schemes"
        ])
    ]

# ----------------------------------------
# --- SIDEBAR: LANGUAGE, USER INFO, MENU & LOGOUT ---
# ----------------------------------------
with st.sidebar:
    # Language Selector at the very top
    render_language_selector()
    
    st.markdown("---")
    
    # Voice shortcuts section - Disabled
    # from components.voice_button import add_voice_shortcuts
    # add_voice_shortcuts()
    
    st.markdown("---")
    
    # User info box
    user_name = st.session_state.get("farmer_name", "User")
    
    if user_role == "Farmer":
        farmer_profile = st.session_state.get("farmer_profile", {})
        location = farmer_profile.get('location', 'N/A')
        st.markdown(f"""
        <div style='background-color:#E8F5E9;padding:15px;border-radius:10px;margin-bottom:20px;border-left:4px solid #2E8B57;'>
            <strong>👤 {user_name}</strong><br>
            <small>📍 {location}</small><br>
            <small>🌾 {t("Farmer Account")}</small>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style='background-color:#E3F2FD;padding:15px;border-radius:10px;margin-bottom:20px;border-left:4px solid #1976D2;'>
            <strong>👨‍💼 {user_name}</strong><br>
            <small>🔐 {t("Admin Account")}</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")

# Build menu with proper grouping - Initialize menu state
if 'selected_menu' not in st.session_state:
    st.session_state.selected_menu = menu_structure[0][1][0]  # Default to first item

# Check if menu selection came from welcome screen
if 'menu_selection' in st.session_state and st.session_state.menu_selection:
    menu_map = {
        "Home": "🏠 Home",
        "View Profile": "👤 My Profile",
        "New Listing": "➕ Create New Listing",
        "View Listings": "🛍️ Browse Listings",
        "Calendar": "📅 Farming Calendar",
        "Weather": "🌤️ Weather Forecast",
        "Market Prices": "💰 Market Prices",
        "Profiles": "👥 Manage Farmers",
        "Database Check": "🗄️ Database Viewer"
    }
    mapped_selection = menu_map.get(st.session_state.menu_selection, st.session_state.menu_selection)
    st.session_state.selected_menu = mapped_selection
    st.session_state.menu_selection = None

# Render menu with sections
with st.sidebar:
    for section_title, section_items in menu_structure:
        # Section header (remove emoji for translation, keep emoji separate)
        section_text = section_title.split(' ', 1)[1] if ' ' in section_title else section_title
        section_emoji = section_title.split(' ', 1)[0] if ' ' in section_title else ""
        st.markdown(f"**{section_emoji} {t(section_text)}**")
        
        # Menu items as buttons
        for item in section_items:
            # Extract emoji and text
            item_text = item.split(' ', 1)[1] if ' ' in item else item
            item_emoji = item.split(' ', 1)[0] if ' ' in item else ""
            translated_item = f"{item_emoji} {t(item_text)}"
            
            # Create button for each menu item
            if st.button(translated_item, key=f"menu_{item}", width="stretch", 
                        type="primary" if st.session_state.selected_menu == item else "secondary"):
                # Add current page to history before navigation
                if st.session_state.selected_menu != item:
                    st.session_state.selected_menu = item
                    st.rerun()
        
        st.markdown("")  # Spacing between sections
    
    st.markdown("---")
    
    # Logout button at bottom
    if st.button(f"🔐 {t('Logout')}", width="stretch", type="secondary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("✅ Logged out successfully!")
        st.rerun()

# Get selected menu
menu = st.session_state.selected_menu

# ----------------------------------------
# --- HOME NAVIGATION BUTTON ---
# ----------------------------------------
# Simple home button to go back to dashboard
if st.session_state.selected_menu != "🏠 Home":
    if st.button("🏠 Home", use_container_width=True, help="Go to Home Dashboard"):
        st.session_state.selected_menu = "🏠 Home"
        st.rerun()

st.markdown("---")

# ----------------------------------------
# --- VOICE & AUDIO FEATURES (DISABLED) ---
# ----------------------------------------
# Disabled due to microphone compatibility issues on Streamlit Cloud
# from components.voice_button import render_floating_voice_button
# render_floating_voice_button()
# from components.text_to_speech_widget import add_listen_everywhere, add_page_narrator
# add_listen_everywhere()
# add_page_narrator()

# ----------------------------------------
# --- PAGE ROUTING ---
# ----------------------------------------

if menu == "🏠 Home":
    render_home_page()

elif menu == "👤 My Profile":
    render_view_profile_page()

elif menu == "📦 My Listings":
    st.header("📦 My Listings")
    st.markdown("View and manage all your listings in one place")
    
    farmer_name = st.session_state.get("farmer_name", "")
    tools_df = st.session_state.get('tools', pd.DataFrame())
    crops_df = st.session_state.get('crops', pd.DataFrame())
    
    # Filter only user's listings (database uses 'Farmer' column, not 'owner')
    if not tools_df.empty and 'Farmer' in tools_df.columns:
        my_tools = tools_df[tools_df['Farmer'] == farmer_name]
    else:
        my_tools = pd.DataFrame()
    
    if not crops_df.empty and 'Farmer' in crops_df.columns:
        my_crops = crops_df[crops_df['Farmer'] == farmer_name]
    else:
        my_crops = pd.DataFrame()
    
    tab1, tab2 = st.tabs(["🔧 My Tools", "🌾 My Crops"])
    
    with tab1:
        if not my_tools.empty:
            st.dataframe(my_tools, width="stretch")
            st.success(f"✅ You have {len(my_tools)} tool(s) listed")
        else:
            st.info("📝 You haven't listed any tools yet.")
            if st.button("➕ List Your First Tool"):
                # Add to navigation history
                if not st.session_state.nav_history or st.session_state.nav_history[-1] != st.session_state.selected_menu:
                    st.session_state.nav_history.append(st.session_state.selected_menu)
                st.session_state.nav_forward = []
                st.session_state.selected_menu = "➕ Post Listing"
                st.rerun()
    
    with tab2:
        if not my_crops.empty:
            st.dataframe(my_crops, width="stretch")
            st.success(f"✅ You have {len(my_crops)} crop(s) listed")
        else:
            st.info("📝 You haven't listed any crops yet.")
            if st.button("➕ List Your First Crop"):
                # Add to navigation history
                if not st.session_state.nav_history or st.session_state.nav_history[-1] != st.session_state.selected_menu:
                    st.session_state.nav_history.append(st.session_state.selected_menu)
                st.session_state.nav_forward = []
                st.session_state.selected_menu = "➕ Post Listing"
                st.rerun()

elif menu == "👷 Worker Board":
    render_labor_board()

elif menu == "🛍️ Browse Listings":
    # Check if showing detail view
    if st.session_state.get('show_listing_detail', False) and st.session_state.get('selected_listing'):
        from components.listing_detail_page import render_listing_detail
        
        listing_info = st.session_state.selected_listing
        render_listing_detail(listing_info['type'], listing_info['data'])
        
        # Reset detail view flag when done
        if st.button("⬅️ Back to Listings", key="back_to_listings"):
            st.session_state.show_listing_detail = False
            st.session_state.selected_listing = None
            st.rerun()
    else:
        st.header("🛍️ Browse Marketplace")
        st.markdown("Explore tools and crops available in your area")
        
        tab1, tab2 = st.tabs(["🔧 Tools for Rent", "🌾 Crops for Sale"])
        
        with tab1:
            render_tool_management(st.session_state.tools, st.session_state.get("farmer_name", None))
        with tab2:
            render_crop_management(st.session_state.crops, st.session_state.get("farmer_name", None))

elif menu == "➕ Create New Listing" or menu == "➕ Post Listing":
    st.header("➕ Create a New Listing")
    st.markdown("List your tools or crops to connect with other farmers")
    
    tab_tool, tab_crop = st.tabs(["🔧 List a Tool", "🌾 List a Crop"])
    
    with tab_tool:
        render_tool_listing(st.session_state.get("farmer_name", ""))
    with tab_crop:
        render_crop_listing(st.session_state.get("farmer_name", ""))

elif menu == "🎤 Voice Listing (NEW)":
    from components.voice_listing_creator import render_voice_listing_creator
    render_voice_listing_creator(st.session_state.get("farmer_name", ""))

elif menu == "📅 Farming Calendar" or menu == "📅 My Calendar":
    from components.calendar_integration import render_integrated_calendar
    
    if st.session_state.get("logged_in") and st.session_state.get("farmer_name"):
        render_integrated_calendar(st.session_state.farmer_name)
    else:
        st.warning("⚠️ Please login as a Farmer to access the calendar feature.")
        st.info("💡 The calendar integrates with your profile location to show weather alerts and forecasts.")

elif menu == "🌤️ Weather Forecast":
    render_weather_component()

elif menu == "💰 Market Prices" or menu == "💰 Today's Market Price":
    render_market_price()

elif menu == "🤖 AI Price Prediction" or menu == "🤔 Should I Sell?":
    render_simple_price_advisor()

elif menu == "🌡️ Climate Risk Dashboard":
    from components.climate_risk_dashboard import render_climate_risk_dashboard
    render_climate_risk_dashboard()

elif menu == "🌾 Climate-Smart Crops":
    from components.climate_smart_crops import render_climate_smart_crops
    render_climate_smart_crops()

elif menu == "💧 Water & Carbon Tracker":
    from components.sustainability_tracker import render_sustainability_tracker
    render_sustainability_tracker()

elif menu == "🗺️ Nearby Places & Services":
    from components.location_services_page import render_location_services_page
    render_location_services_page()

elif menu == "👥 Manage Farmers":
    render_profiles_page()

elif menu == "🗄️ Database Viewer":
    render_db_check()

elif menu == "💾 Cache Management":
    render_cache_admin_page()

elif menu == "🏛️ Government Schemes":
    render_government_schemes_page()

elif menu == "🏛️ Schemes & Financial Tools":
    render_government_schemes_page()

elif menu == "💰 Farm Finance Management" or menu == "💰 My Money Diary":
    render_simple_finance_page()

elif menu == "🤖 AI Chatbot":
    from components.ai_chatbot_page import render_ai_chatbot_page
    render_ai_chatbot_page()

elif menu == "🗣️ Ask Advisor":
    render_voice_chatbot()

# Voice Assistant removed due to microphone compatibility issues
# elif menu == "🎤 Voice Assistant":
#     from components.voice_assistant import render_voice_assistant_page
#     render_voice_assistant_page()

elif menu == "🔔 Notifications & Alerts":
    from components.notifications_page import render_notifications_page
    render_notifications_page()


# ----------------------------------------
# --- FOOTER ---
# ----------------------------------------
st.markdown(f"""
<hr style='border-top: 2px solid #1976D2; margin-top: 30px;'>
<div style='text-align:center; padding:15px; background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%); border-radius: 10px;'>
    <p style='color: #0D47A1; margin: 0 0 5px 0; font-weight: 600; font-size: 15px;'>
        🌍 AI Climate-Smart Agriculture Platform
    </p>
    <p style='color: #1565C0; margin: 0; font-size: 13px;'>
        🎯 SDG 13: Climate Action | 🤖 Multi-Modal AI | 🛰️ Satellite Integration
    </p>
    <small style='color: #1976D2; font-size: 12px;'>
        © 2025 {t("Prototype by Team AgroLink")} | Helping farmers adapt to climate change
    </small>
</div>
""", unsafe_allow_html=True)


