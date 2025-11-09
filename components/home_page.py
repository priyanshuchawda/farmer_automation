# components/home_page.py

import streamlit as st
import pandas as pd
from database.db_functions import get_data
from datetime import datetime
from calender.utils import get_events_for_date
from components.translation_utils import t

def render_home_page():
    """
    Personalized dashboard for logged-in farmers
    Shows quick actions, today's tasks, weather alerts, and recent activity
    """
    # Mobile responsive CSS for home page
    st.markdown("""
    <style>
    /* Home page mobile responsiveness */
    @media (max-width: 768px) {
        /* Quick action buttons - stack on mobile */
        [data-testid="column"] {
            min-width: 100% !important;
            margin-bottom: 10px;
        }
        
        /* Smaller captions */
        .stCaption {
            font-size: 0.75rem !important;
        }
        
        /* Header adjustments */
        h2 {
            font-size: 1.5rem !important;
        }
        
        h3 {
            font-size: 1.2rem !important;
        }
    }
    
    @media (max-width: 480px) {
        h2 {
            font-size: 1.3rem !important;
        }
        
        h3 {
            font-size: 1.1rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    farmer_name = st.session_state.get("farmer_name", "Farmer")
    farmer_profile = st.session_state.get("farmer_profile", {})
    user_role = st.session_state.get("role", "Farmer")
    
    # Personalized Welcome Header
    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = t("Good Morning")
        emoji = "🌅"
    elif current_hour < 17:
        greeting = t("Good Afternoon")
        emoji = "☀️"
    else:
        greeting = t("Good Evening")
        emoji = "🌙"
    
    # Greeting with listen button
    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown(f"## {emoji} {greeting}, {farmer_name}!")
    with col2:
        from components.text_to_speech_widget import speak_button
        speak_button(f"{greeting} {farmer_name}", "🔊", key_suffix="greeting")
    
    # Location and basic info
    location = farmer_profile.get('location', 'Not set')
    farm_size = farmer_profile.get('farm_size', 'N/A')
    farm_unit = farmer_profile.get('farm_unit', '')
    
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        from components.translation_utils import translate_location
        localized_location = translate_location(location)
        st.markdown(f"📍 **{t('Location')}:** {localized_location}")
    with col2:
        from components.translation_utils import convert_numbers_to_local
        translated_unit = t(farm_unit) if farm_unit else farm_unit
        localized_farm_size = convert_numbers_to_local(str(farm_size))
        st.markdown(f"🚜 **{t('Farm Size')}:** {localized_farm_size} {translated_unit}")
    with col3:
        from components.translation_utils import format_date_localized
        localized_date = format_date_localized(datetime.now())
        localized_date = convert_numbers_to_local(localized_date)
        st.markdown(f"📅 **{t('Today')}:** {localized_date}")
    
    st.markdown("---")
    
    # Quick Actions Section
    st.markdown(f"### 🚀 {t('Quick Actions')}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button(f"📝 {t('List Tool')}", width="stretch", type="primary"):
            if not st.session_state.nav_history or st.session_state.nav_history[-1] != st.session_state.selected_menu:
                st.session_state.nav_history.append(st.session_state.selected_menu)
            st.session_state.nav_forward = []
            st.session_state.selected_menu = "➕ Create New Listing"
            st.rerun()
        st.caption(t("Add tools for rent"))
    
    with col2:
        if st.button(f"🌾 {t('List Crop')}", width="stretch", type="primary"):
            if not st.session_state.nav_history or st.session_state.nav_history[-1] != st.session_state.selected_menu:
                st.session_state.nav_history.append(st.session_state.selected_menu)
            st.session_state.nav_forward = []
            st.session_state.selected_menu = "➕ Create New Listing"
            st.rerun()
        st.caption(t("Post crops for sale"))
    
    with col3:
        if st.button(f"📅 {t('Plan Day')}", width="stretch", type="primary"):
            if not st.session_state.nav_history or st.session_state.nav_history[-1] != st.session_state.selected_menu:
                st.session_state.nav_history.append(st.session_state.selected_menu)
            st.session_state.nav_forward = []
            st.session_state.selected_menu = "📅 Farming Calendar"
            st.rerun()
        st.caption(t("Schedule activities"))
    
    with col4:
        if st.button(f"🛍️ {t('Browse Market')}", width="stretch", type="primary"):
            if not st.session_state.nav_history or st.session_state.nav_history[-1] != st.session_state.selected_menu:
                st.session_state.nav_history.append(st.session_state.selected_menu)
            st.session_state.nav_forward = []
            st.session_state.selected_menu = "🛍️ Browse Listings"
            st.rerun()
        st.caption(t("View all listings"))
    
    st.markdown("")
    
    # Voice input section - Disabled due to mic_recorder compatibility issues
    # from components.voice_button import render_voice_quick_input
    # render_voice_quick_input()
    
    st.divider()
    
    # Two column layout for tasks and weather
    col_left, col_right = st.columns([3, 2])
    
    with col_left:
        # Today's Tasks Section
        st.markdown(f"### 📋 {t('Today\'s Tasks')}")
        
        try:
            today = datetime.now().date()
            events = get_events_for_date(farmer_name, today)
            
            if events and len(events) > 0:
                for event in events[:5]:  # Show up to 5 tasks
                    event_time = event.get('time', 'All day')
                    event_title = event.get('title', 'Untitled task')
                    event_type = event.get('type', 'general')
                    
                    # Choose emoji based on event type
                    if 'irrigation' in event_title.lower():
                        icon = "💧"
                    elif 'fertilizer' in event_title.lower() or 'fertiliz' in event_title.lower():
                        icon = "🌱"
                    elif 'harvest' in event_title.lower():
                        icon = "🌾"
                    elif 'plant' in event_title.lower():
                        icon = "🌿"
                    else:
                        icon = "📌"
                    
                    st.markdown(f"{icon} **{event_time}** - {event_title}")
            else:
                st.info(f"📅 {t('No tasks scheduled for today.')}\n\n{t('Visit the Calendar to plan your farming activities!')}")
                if st.button(f"📅 {t('Open Calendar')}", key="add_task_home", width="stretch", type="primary"):
                    # Add to navigation history
                    if not st.session_state.nav_history or st.session_state.nav_history[-1] != st.session_state.selected_menu:
                        st.session_state.nav_history.append(st.session_state.selected_menu)
                    st.session_state.nav_forward = []
                    st.session_state.selected_menu = "📅 Farming Calendar"
                    st.rerun()
        except Exception as e:
            st.info(f"📅 {t('No tasks scheduled for today.')}\n\n{t('Visit the Calendar to plan your farming activities!')}")
            if st.button(f"📅 {t('Open Calendar')}", key="add_task_error", width="stretch", type="primary"):
                # Add to navigation history
                if not st.session_state.nav_history or st.session_state.nav_history[-1] != st.session_state.selected_menu:
                    st.session_state.nav_history.append(st.session_state.selected_menu)
                st.session_state.nav_forward = []
                st.session_state.selected_menu = "📅 Farming Calendar"
                st.rerun()
    
    with col_right:
        # Weather Section
        st.markdown(f"### 🌤️ {t('Weather Update')}")
        
        weather_location = farmer_profile.get('weather_location', location)
        localized_weather_location = translate_location(weather_location)
        
        st.info(f"📍 {localized_weather_location}\n\n{t('Visit Weather section for detailed forecast')}")
        
        if st.button(f"🌤️ {t('View Weather Forecast')}", key="weather_home", width="stretch", type="primary"):
            # Add to navigation history
            if not st.session_state.nav_history or st.session_state.nav_history[-1] != st.session_state.selected_menu:
                st.session_state.nav_history.append(st.session_state.selected_menu)
            st.session_state.nav_forward = []
            st.session_state.selected_menu = "🌤️ Weather Forecast"
            st.rerun()
    
    st.markdown("---")
    
    # My Activity Section
    st.markdown(f"### 📊 {t('My Activity')}")
    
    col1, col2, col3 = st.columns(3)
    
    # Count user's listings
    tools_df = st.session_state.get('tools', pd.DataFrame())
    crops_df = st.session_state.get('crops', pd.DataFrame())
    
    if not tools_df.empty and 'Farmer' in tools_df.columns:
        my_tools = len(tools_df[tools_df['Farmer'] == farmer_name])
    else:
        my_tools = 0
    
    if not crops_df.empty and 'Farmer' in crops_df.columns:
        my_crops = len(crops_df[crops_df['Farmer'] == farmer_name])
    else:
        my_crops = 0
    
    with col1:
        st.metric(f"🔧 {t('My Tools Listed')}", my_tools)
        if st.button(t("View My Tools"), key="my_tools_btn"):
            if not st.session_state.nav_history or st.session_state.nav_history[-1] != st.session_state.selected_menu:
                st.session_state.nav_history.append(st.session_state.selected_menu)
            st.session_state.nav_forward = []
            st.session_state.selected_menu = "📦 My Listings"
            st.rerun()
    
    with col2:
        st.metric(f"🌾 {t('My Crops Listed')}", my_crops)
        if st.button(t("View My Crops"), key="my_crops_btn"):
            if not st.session_state.nav_history or st.session_state.nav_history[-1] != st.session_state.selected_menu:
                st.session_state.nav_history.append(st.session_state.selected_menu)
            st.session_state.nav_forward = []
            st.session_state.selected_menu = "📦 My Listings"
            st.rerun()
    
    with col3:
        total_listings = my_tools + my_crops
        st.metric(f"📦 {t('Total Listings')}", total_listings)
        if st.button(t("Create New Listing"), key="new_listing_btn"):
            if not st.session_state.nav_history or st.session_state.nav_history[-1] != st.session_state.selected_menu:
                st.session_state.nav_history.append(st.session_state.selected_menu)
            st.session_state.nav_forward = []
            st.session_state.selected_menu = "➕ Create New Listing"
            st.rerun()
    
    st.markdown("")
    
    # Help Section
    st.markdown(f"### 💡 {t('Need Help?')}")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"**📖 {t('How to Use')}**\n\n{t('New to the platform? Check out our guide!')}")
        if st.button(f"📖 {t('View Profile')}", key="guide_btn", width="stretch"):
            # Add to navigation history
            if not st.session_state.nav_history or st.session_state.nav_history[-1] != st.session_state.selected_menu:
                st.session_state.nav_history.append(st.session_state.selected_menu)
            st.session_state.nav_forward = []
            st.session_state.selected_menu = "👤 My Profile"
            st.rerun()
    
    with col2:
        st.success(f"**🤖 {t('AI Assistant')}**\n\n{t('Get farming tips from our AI calendar!')}")
        if st.button(f"🤖 {t('Open AI Chat')}", key="ai_btn", width="stretch"):
            # Add to navigation history
            if not st.session_state.nav_history or st.session_state.nav_history[-1] != st.session_state.selected_menu:
                st.session_state.nav_history.append(st.session_state.selected_menu)
            st.session_state.nav_forward = []
            st.session_state.selected_menu = "🤖 AI Chatbot"
            st.rerun()
    
    with col3:
        st.warning(f"**💰 {t('Market Prices')}**\n\n{t('Check current rates before selling!')}")
        if st.button(f"💰 {t('View Prices')}", key="prices_btn", width="stretch"):
            # Add to navigation history
            if not st.session_state.nav_history or st.session_state.nav_history[-1] != st.session_state.selected_menu:
                st.session_state.nav_history.append(st.session_state.selected_menu)
            st.session_state.nav_forward = []
            st.session_state.selected_menu = "💰 Market Prices"
            st.rerun()


def render_db_check():
    """
    Displays a read-only view of the 'tools' and 'crops' tables.
    Uses tabs for each table and shows success/error messages with record counts.
    """
    st.session_state  # Ensure session state is accessible

    # Tabs for tools and crops
    tab_tools, tab_crops = st.tabs(["Tools Table", "Crops Table"])

    # Tools Table
    with tab_tools:
        try:
            tools_df = get_data("tools")
            if tools_df.empty:
                st.warning("No records found in the 'tools' table.")
            else:
                st.dataframe(tools_df)
                st.success(f"Loaded {len(tools_df)} records from 'tools'.")
        except Exception as e:
            st.error(f"Error loading 'tools' table: {e}")

    # Crops Table
    with tab_crops:
        try:
            crops_df = get_data("crops")
            if crops_df.empty:
                st.warning("No records found in the 'crops' table.")
            else:
                st.dataframe(crops_df)
                st.success(f"Loaded {len(crops_df)} records from 'crops'.")
        except Exception as e:
            st.error(f"Error loading 'crops' table: {e}")


