# components/home_page.py

import streamlit as st
import pandas as pd
from database.db_functions import get_data
from datetime import datetime
from calender.utils import get_events_for_date
from components.onboarding_component import (
    render_onboarding_checklist, 
    check_and_update_listing_task,
    check_and_update_calendar_task
)

def render_home_page():
    """
    Personalized dashboard for logged-in farmers
    Shows quick actions, today's tasks, weather alerts, and recent activity
    """
    farmer_name = st.session_state.get("farmer_name", "Farmer")
    farmer_profile = st.session_state.get("farmer_profile", {})
    user_role = st.session_state.get("role", "Farmer")
    
    # Personalized Welcome Header
    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = "Good Morning"
        emoji = "🌅"
    elif current_hour < 17:
        greeting = "Good Afternoon"
        emoji = "☀️"
    else:
        greeting = "Good Evening"
        emoji = "🌙"
    
    st.markdown(f"## {emoji} {greeting}, {farmer_name}!")
    
    # Location and basic info
    location = farmer_profile.get('location', 'Not set')
    farm_size = farmer_profile.get('farm_size', 'N/A')
    farm_unit = farmer_profile.get('farm_unit', '')
    
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        st.markdown(f"📍 **Location:** {location}")
    with col2:
        st.markdown(f"🚜 **Farm Size:** {farm_size} {farm_unit}")
    with col3:
        st.markdown(f"📅 **Today:** {datetime.now().strftime('%B %d, %Y')}")
    
    st.markdown("---")
    
    # Interactive Onboarding Checklist (only for farmers, not admin)
    if user_role == "Farmer":
        try:
            # Check and update tasks automatically (with error handling)
            check_and_update_listing_task(farmer_name)
        except Exception as e:
            print(f"Non-critical error checking listings: {e}")
        
        try:
            check_and_update_calendar_task(farmer_name)
        except Exception as e:
            print(f"Non-critical error checking calendar: {e}")
        
        try:
            # Render onboarding checklist
            render_onboarding_checklist(farmer_name)
        except Exception as e:
            print(f"Non-critical error rendering checklist: {e}")
        
        st.markdown("---")
    
    # Quick Actions Section
    st.markdown("### 🚀 Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📝 List Tool", use_container_width=True, type="primary"):
            st.session_state.menu_selection = "New Listing"
            st.rerun()
        st.caption("Add tools for rent")
    
    with col2:
        if st.button("🌾 List Crop", use_container_width=True, type="primary"):
            st.session_state.menu_selection = "New Listing"
            st.rerun()
        st.caption("Post crops for sale")
    
    with col3:
        if st.button("📅 Plan Day", use_container_width=True, type="primary"):
            st.session_state.menu_selection = "Calendar"
            st.rerun()
        st.caption("Schedule activities")
    
    with col4:
        if st.button("🛍️ Browse Market", use_container_width=True, type="primary"):
            st.session_state.menu_selection = "View Listings"
            st.rerun()
        st.caption("View all listings")
    
    st.markdown("")
    
    # Two column layout for tasks and weather
    col_left, col_right = st.columns([3, 2])
    
    with col_left:
        # Today's Tasks Section
        st.markdown("### 📋 Today's Tasks")
        
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
                st.info("📅 No tasks scheduled for today.\n\nVisit the Calendar to plan your farming activities!")
                if st.button("➕ Add Task", key="add_task_home"):
                    st.session_state.menu_selection = "Calendar"
                    st.rerun()
        except Exception as e:
            st.info("📅 No tasks scheduled for today.\n\nVisit the Calendar to plan your farming activities!")
    
    with col_right:
        # Weather Alert Section
        st.markdown("### 🌤️ Weather Update")
        
        weather_location = farmer_profile.get('weather_location', location)
        latitude = farmer_profile.get('latitude')
        longitude = farmer_profile.get('longitude')
        
        if latitude and longitude:
            try:
                from weather.ai_client import AIClient
                ai_client = AIClient()
                forecast = ai_client.get_weather_forecast(latitude, longitude)
                
                if forecast and len(forecast) > 0:
                    today_weather = forecast[0]
                    temp = today_weather.get('temperature', 'N/A')
                    condition = today_weather.get('condition', 'N/A')
                    
                    st.success(f"**{temp}°C** - {condition}")
                    st.caption(f"📍 {weather_location}")
                    
                    # Check for alerts
                    if 'rain' in condition.lower():
                        st.warning("⚠️ Rain expected - Plan accordingly!")
                    elif 'storm' in condition.lower() or 'thunder' in condition.lower():
                        st.error("⛈️ Storm alert - Take precautions!")
                    
                    if st.button("🌤️ View Full Forecast", key="weather_home"):
                        st.session_state.menu_selection = "Weather"
                        st.rerun()
                else:
                    st.info("Weather data not available")
            except:
                st.info(f"📍 {weather_location}\n\nVisit Weather section for detailed forecast")
        else:
            st.info(f"📍 {weather_location}\n\nVisit Weather section for detailed forecast")
    
    st.markdown("---")
    
    # My Activity Section
    st.markdown("### 📊 My Activity")
    
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
        st.metric("🔧 My Tools Listed", my_tools)
        if st.button("View My Tools", key="my_tools_btn"):
            st.session_state.menu_selection = "My Listings"
            st.rerun()
    
    with col2:
        st.metric("🌾 My Crops Listed", my_crops)
        if st.button("View My Crops", key="my_crops_btn"):
            st.session_state.menu_selection = "My Listings"
            st.rerun()
    
    with col3:
        total_listings = my_tools + my_crops
        st.metric("📦 Total Listings", total_listings)
        if st.button("Create New Listing", key="new_listing_btn"):
            st.session_state.menu_selection = "New Listing"
            st.rerun()
    
    st.markdown("")
    
    # Help Section
    st.markdown("### 💡 Need Help?")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("**📖 How to Use**\n\nNew to the platform? Check out our guide!")
    with col2:
        st.success("**🤖 AI Assistant**\n\nGet farming tips from our AI calendar!")
    with col3:
        st.warning("**💰 Market Prices**\n\nCheck current rates before selling!")


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


