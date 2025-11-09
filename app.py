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
from components.welcome_screen import render_welcome_screen
from components.home_page import render_home_page, render_db_check
from components.tool_listings import render_tool_listing, render_tool_management
from components.crop_listings import render_crop_listing, render_crop_management
from components.profiles_page import render_profiles_page
from components.view_profile_page import render_view_profile_page
from components.weather_component import render_weather_component
from components.market_price_scraper import render_market_price
from components.price_prediction_page import render_price_prediction_page
from components.cache_admin_page import render_cache_admin_page
from components.government_schemes_page import render_government_schemes_page
from components.farm_finance_page import render_farm_finance_page
from components.translation_utils import render_language_selector, t
from calender.calendar_component import render_calendar
from calender.config import TRANSLATIONS
from calender.utils import get_events_for_date

# ----------------------------------------
# --- CONFIGURATION AND SETUP ---
# ----------------------------------------

# 1. Database Initialization
if 'db_initialized' not in st.session_state:
    init_db()
    st.session_state.db_initialized = True

# 2. Page Config
st.set_page_config(page_title="Smart Farmer Marketplace", page_icon="favicon.ico", layout="wide")

# 3. Custom CSS for styling
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

    body { 
        font-family: 'Roboto', sans-serif;
        background-color: #f5f5f5;
    }
    h1,h2,h3 { 
        color:#2E8B57; 
        text-align:center; 
        font-weight:700; 
    }
    .stApp {
        background-color: #f5f5f5;
    }
    [data-testid="stSidebar"] { 
        background-color:#FFFFFF; 
        border-right:2px solid #E0E0E0; 
        padding-top:20px; 
    }
    
    /* Button Styling */
    .stButton>button { 
        background-color:#2E8B57; 
        color:white; 
        border-radius:8px; 
        padding:10px 20px; 
        font-weight:bold; 
        border:none; 
        box-shadow:0 2px 4px rgba(0,0,0,0.1); 
        width:100%; 
        transition: all 0.3s ease;
    }
    .stButton>button:hover { 
        background-color:#3CB371; 
        box-shadow:0 4px 8px rgba(0,0,0,0.2);
        transform: translateY(-2px);
    }
    
    /* Card Styling */
    .card { 
        background-color:#ffffff; 
        padding:30px; 
        margin-bottom:25px; 
        border-radius:15px; 
        box-shadow:0 8px 16px rgba(0,0,0,0.1); 
        border-left:7px solid #2E8B57; 
    }
    
    footer { 
        visibility:hidden; 
    }
    .stDataFrame, .stDataEditor { 
        border:1px solid #E0E0E0; 
        border-radius:10px; 
        padding:10px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
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
# --- FIRST-TIME USER WELCOME SCREEN (OPTIONAL) ---
# ----------------------------------------
# Skip welcome screen - go directly to home page after login
# Welcome screen can be accessed via a separate menu item if needed
# if st.session_state.get('role') == 'Farmer':
#     if 'show_welcome' not in st.session_state:
#         st.session_state.show_welcome = True
#     
#     if st.session_state.get('show_welcome', False):
#         render_welcome_screen()
#         st.stop()

# ----------------------------------------
# --- MAIN APPLICATION (After Login) ---
# ----------------------------------------
st.title("Smart Farmer Marketplace")

st.markdown("""
<div style='background-color:#E8F5E9;padding:12px;border-radius:10px;text-align:center;margin-bottom:20px;border: 1px dashed #3CB371;'>
    <h4>Empowering Farmers, Connecting Communities</h4>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------
# --- REORGANIZED MENU STRUCTURE ---
# ----------------------------------------
# ----------------------------------------
# --- NAVIGATION HISTORY (DOUBLY LINKED LIST APPROACH) ---
# ----------------------------------------
# Initialize navigation history stack
if 'nav_history' not in st.session_state:
    st.session_state.nav_history = []
if 'nav_forward' not in st.session_state:
    st.session_state.nav_forward = []

# Build menu based on user role - Define structure first
user_role = st.session_state.get("role", "User")

if user_role == "Farmer":
    # Farmer Menu - Organized by sections
    menu_structure = [
        ("🏠 DASHBOARD", ["🏠 Home"]),
        ("👤 MY ACCOUNT", ["👤 My Profile", "📦 My Listings"]),
        ("🛍️ MARKETPLACE", ["🛍️ Browse Listings", "➕ Create New Listing"]),
        ("📊 PLANNING & INSIGHTS", ["📅 Farming Calendar", "🌤️ Weather Forecast", "💰 Market Prices", "🤖 AI Price Prediction"]),
        ("🗺️ LOCATION SERVICES", ["🗺️ Nearby Places & Services"]),
        ("🏛️ GOVERNMENT", ["🏛️ Government Schemes"]),
        ("💰 FINANCE", ["💰 Farm Finance Management"]),
        ("🤖 ASSISTANCE", ["🤖 AI Chatbot", "🔔 Notifications & Alerts"])
    ]
else:
    # Admin Menu - Same as farmer but with admin section added
    menu_structure = [
        ("🏠 DASHBOARD", ["🏠 Home"]),
        ("👨‍💼 ADMIN TOOLS", ["👥 Manage Farmers", "🗄️ Database Viewer", "💾 Cache Management"]),
        ("👤 MY ACCOUNT", ["👤 My Profile", "📦 My Listings"]),
        ("🛍️ MARKETPLACE", ["🛍️ Browse Listings", "➕ Create New Listing"]),
        ("📊 PLANNING & INSIGHTS", ["📅 Farming Calendar", "🌤️ Weather Forecast", "💰 Market Prices", "🤖 AI Price Prediction"]),
        ("🗺️ LOCATION SERVICES", ["🗺️ Nearby Places & Services"]),
        ("🏛️ GOVERNMENT", ["🏛️ Schemes & Financial Tools"]),
        ("💰 FINANCE", ["💰 Farm Finance Management"])
    ]

# ----------------------------------------
# --- SIDEBAR: LANGUAGE, USER INFO, MENU & LOGOUT ---
# ----------------------------------------
with st.sidebar:
    # Language Selector at the very top
    render_language_selector()
    
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
    
    # Add current page to history before navigation
    if st.session_state.selected_menu != mapped_selection:
        if not st.session_state.nav_history or st.session_state.nav_history[-1] != st.session_state.selected_menu:
            st.session_state.nav_history.append(st.session_state.selected_menu)
        st.session_state.nav_forward = []  # Clear forward history on new navigation
    
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
            if st.button(translated_item, key=f"menu_{item}", use_container_width=True, 
                        type="primary" if st.session_state.selected_menu == item else "secondary"):
                # Add current page to history before navigation
                if st.session_state.selected_menu != item:
                    if not st.session_state.nav_history or st.session_state.nav_history[-1] != st.session_state.selected_menu:
                        st.session_state.nav_history.append(st.session_state.selected_menu)
                    st.session_state.nav_forward = []  # Clear forward history on new navigation
                
                st.session_state.selected_menu = item
                st.rerun()
        
        st.markdown("")  # Spacing between sections
    
    st.markdown("---")
    
    # Logout button at bottom
    if st.button(f"🔐 {t('Logout')}", use_container_width=True, type="secondary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("✅ Logged out successfully!")
        st.rerun()

# Get selected menu
menu = st.session_state.selected_menu

# ----------------------------------------
# --- BACK/FORWARD NAVIGATION BUTTONS ---
# ----------------------------------------
# Create navigation bar with back/forward buttons
nav_col1, nav_col2, nav_col3 = st.columns([1, 8, 1])

with nav_col1:
    # Back button
    if len(st.session_state.nav_history) > 0:
        if st.button("⬅️ Back", use_container_width=True, help="Go to previous page"):
            # Move current page to forward history
            st.session_state.nav_forward.append(st.session_state.selected_menu)
            # Get previous page from history
            previous_page = st.session_state.nav_history.pop()
            st.session_state.selected_menu = previous_page
            st.rerun()

with nav_col3:
    # Forward button (if user went back)
    if len(st.session_state.nav_forward) > 0:
        if st.button("➡️", use_container_width=True, help="Go forward"):
            # Move current page to history
            st.session_state.nav_history.append(st.session_state.selected_menu)
            # Get next page from forward history
            next_page = st.session_state.nav_forward.pop()
            st.session_state.selected_menu = next_page
            st.rerun()

st.markdown("---")

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
            st.dataframe(my_tools, use_container_width=True)
            st.success(f"✅ You have {len(my_tools)} tool(s) listed")
        else:
            st.info("📝 You haven't listed any tools yet.")
            if st.button("➕ List Your First Tool"):
                # Add to navigation history
                if not st.session_state.nav_history or st.session_state.nav_history[-1] != st.session_state.selected_menu:
                    st.session_state.nav_history.append(st.session_state.selected_menu)
                st.session_state.nav_forward = []
                st.session_state.selected_menu = "➕ Create New Listing"
                st.rerun()
    
    with tab2:
        if not my_crops.empty:
            st.dataframe(my_crops, use_container_width=True)
            st.success(f"✅ You have {len(my_crops)} crop(s) listed")
        else:
            st.info("📝 You haven't listed any crops yet.")
            if st.button("➕ List Your First Crop"):
                # Add to navigation history
                if not st.session_state.nav_history or st.session_state.nav_history[-1] != st.session_state.selected_menu:
                    st.session_state.nav_history.append(st.session_state.selected_menu)
                st.session_state.nav_forward = []
                st.session_state.selected_menu = "➕ Create New Listing"
                st.rerun()

elif menu == "🛍️ Browse Listings":
    st.header("🛍️ Browse Marketplace")
    st.markdown("Explore tools and crops available in your area")
    
    tab1, tab2 = st.tabs(["🔧 Tools for Rent", "🌾 Crops for Sale"])
    
    with tab1:
        render_tool_management(st.session_state.tools, st.session_state.get("farmer_name", None))
    with tab2:
        render_crop_management(st.session_state.crops, st.session_state.get("farmer_name", None))

elif menu == "➕ Create New Listing":
    st.header("➕ Create a New Listing")
    st.markdown("List your tools or crops to connect with other farmers")
    
    tab_tool, tab_crop = st.tabs(["🔧 List a Tool", "🌾 List a Crop"])
    
    with tab_tool:
        render_tool_listing(st.session_state.get("farmer_name", ""))
    with tab_crop:
        render_crop_listing(st.session_state.get("farmer_name", ""))

elif menu == "📅 Farming Calendar":
    from components.calendar_integration import render_integrated_calendar
    
    if st.session_state.get("logged_in") and st.session_state.get("farmer_name"):
        render_integrated_calendar(st.session_state.farmer_name)
    else:
        st.warning("⚠️ Please login as a Farmer to access the calendar feature.")
        st.info("💡 The calendar integrates with your profile location to show weather alerts and forecasts.")

elif menu == "🌤️ Weather Forecast":
    render_weather_component()

elif menu == "💰 Market Prices":
    render_market_price()

elif menu == "🤖 AI Price Prediction":
    render_price_prediction_page()

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

elif menu == "💰 Farm Finance Management":
    render_farm_finance_page()

elif menu == "🤖 AI Chatbot":
    from components.ai_chatbot_page import render_ai_chatbot_page
    render_ai_chatbot_page()

elif menu == "🔔 Notifications & Alerts":
    from components.notifications_page import render_notifications_page
    render_notifications_page()


# ----------------------------------------
# --- FOOTER ---
# ----------------------------------------
st.markdown("""
<hr style='border-top: 2px solid #3CB371; margin-top: 30px;'>
<div style='text-align:center;color:#696969;padding:10px;'>
    <small>© 2025 Smart Farmer Marketplace | Prototype by Team AgroLink</small>
</div>
""", unsafe_allow_html=True)


