"""Enhanced calendar with weather integration"""

import streamlit as st
from datetime import datetime, timedelta
from database.db_functions import get_farmer_profile, add_data, get_farmer_events, delete_event
from weather.weather_assistant import get_weather_forecast_for_query
from weather.combined_forecast import get_weather_forecast
from calender.ai_service import AIService
from calender.config import TRANSLATIONS as CAL_TRANSLATIONS
from calender.calendar_component import render_calendar

def get_weather_for_event(farmer_profile, event_date):
    """Get weather forecast for a specific date and farmer location"""
    if not farmer_profile or 'weather_location' not in farmer_profile:
        return None
    
    location = farmer_profile['weather_location']
    lat = farmer_profile.get('latitude')
    lon = farmer_profile.get('longitude')
    
    try:
        # Get forecast for the location
        forecast = get_weather_forecast(location, lat=lat, lon=lon)
        
        if forecast:
            # Find forecast for the specific date
            event_date_obj = datetime.strptime(event_date, '%Y-%m-%d').date()
            
            for day in forecast:
                if isinstance(day['date'], str):
                    forecast_date = datetime.strptime(day['date'], '%Y-%m-%d').date()
                elif isinstance(day['date'], datetime):
                    forecast_date = day['date'].date()
                else:
                    forecast_date = day['date']
                
                if forecast_date == event_date_obj:
                    return {
                        'temperature': day.get('temperature'),
                        'rainfall': day.get('rainfall'),
                        'wind_speed': day.get('wind_speed')
                    }
    except Exception as e:
        print(f"Error getting weather for event: {e}")
    
    return None

def create_weather_alert(weather_data):
    """Create weather alert message based on weather conditions"""
    if not weather_data:
        return ""
    
    temp = weather_data.get('temperature', 0)
    rain = weather_data.get('rainfall', 0)
    wind = weather_data.get('wind_speed', 0)
    
    alerts = []
    
    if rain > 10:
        alerts.append("⚠️ Heavy rain expected - postpone outdoor activities")
    elif rain > 2:
        alerts.append("🌧️ Light rain expected - plan accordingly")
    
    if temp > 35:
        alerts.append("🔥 Very hot - ensure proper irrigation")
    elif temp < 15:
        alerts.append("❄️ Cold weather - protect sensitive crops")
    
    if wind > 25:
        alerts.append("💨 Strong winds - secure equipment and structures")
    
    if not alerts:
        if temp >= 20 and temp <= 30 and rain == 0:
            return "✅ Good weather for farming activities"
        else:
            return f"☀️ Weather: {temp}°C, {rain}mm rain, {wind} km/h wind"
    
    return " | ".join(alerts)

def render_integrated_calendar(farmer_name):
    """Render calendar with weather integration for logged-in farmer"""
    
    # Get farmer profile
    farmer_profile = get_farmer_profile(farmer_name)
    
    if not farmer_profile:
        st.warning("⚠️ Please create your farmer profile first to use weather-integrated calendar.")
        return
    
    # Display farmer info and weather location
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"### 👨‍🌾 {farmer_name}'s Calendar")
        st.caption(f"📍 Farm: {farmer_profile.get('location', 'N/A')} | 🌍 Weather: {farmer_profile.get('weather_location', 'N/A')}")
    
    with col2:
        if st.button("🔄 Refresh Weather Data", use_container_width=True):
            st.rerun()
    
    st.divider()
    
    # Initialize session state
    if "current_month" not in st.session_state:
        st.session_state.current_month = datetime.now().month
    if "current_year" not in st.session_state:
        st.session_state.current_year = datetime.now().year
    
    # AI-Powered Plan Generation
    ai_service = AIService()
    lang = "en"
    
    with st.expander("🤖 AI Farming Plan Generator", expanded=False):
        st.write("Ask AI to create a farming schedule for you!")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            prompt = st.text_area(
                "Your farming question:",
                height=80,
                placeholder="E.g., Create a 10-day wheat planting schedule for November",
                key="ai_calendar_prompt"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🌱 Generate", use_container_width=True, type="primary"):
                if prompt.strip():
                    with st.spinner("🔄 Creating plan..."):
                        plan_data, error = ai_service.generate_farming_plan(prompt, lang)
                        
                        if plan_data:
                            st.session_state.ai_plan = plan_data
                            st.success("✅ Plan ready!")
                            st.rerun()
                        else:
                            st.error(f"❌ {error}")
    
    # Display and save AI-generated plan
    if 'ai_plan' in st.session_state:
        plan = st.session_state.ai_plan
        
        st.subheader(f"📋 {plan['heading']}")
        
        for step in plan['plan']:
            st.markdown(f"**{step['step_number']}. {step['title']}**")
            st.write(step['description'])
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📅 Add All to Calendar with Weather Alerts", type="primary", use_container_width=True):
                base_date = datetime.now()
                added = 0
                
                for idx, step in enumerate(plan['plan']):
                    event_date = (base_date + timedelta(days=idx)).strftime('%Y-%m-%d')
                    
                    # Get weather for this date
                    weather_data = get_weather_for_event(farmer_profile, event_date)
                    weather_alert = create_weather_alert(weather_data)
                    
                    # Save to database
                    event_data = (
                        farmer_name,
                        event_date,
                        step['title'],
                        step['description'],
                        weather_alert,
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    )
                    add_data("calendar_events", event_data)
                    added += 1
                
                st.success(f"✅ Added {added} events with weather alerts!")
                del st.session_state.ai_plan
                st.rerun()
        
        with col2:
            if st.button("❌ Cancel", use_container_width=True):
                del st.session_state.ai_plan
                st.rerun()
    
    st.divider()
    
    # Load farmer's events from database
    events_df = get_farmer_events(farmer_name)
    
    # Convert to calendar format
    calendar_events = []
    for _, row in events_df.iterrows():
        calendar_events.append({
            "id": row['id'],
            "start": f"{row['event_date']}T09:00:00",
            "extendedProps": {
                "heading": row['event_title'],
                "description": row['event_description'],
                "weather_alert": row.get('weather_alert', '')
            }
        })
    
    # Display current month weather summary
    st.subheader(f"🌤️ Weather Summary for {farmer_profile.get('weather_location')}")
    
    try:
        forecast = get_weather_forecast(
            farmer_profile.get('weather_location'),
            lat=farmer_profile.get('latitude'),
            lon=farmer_profile.get('longitude')
        )
        
        if forecast:
            cols = st.columns(min(7, len(forecast)))
            for idx, day in enumerate(forecast[:7]):
                with cols[idx]:
                    date_str = day['date'] if isinstance(day['date'], str) else day['date'].strftime('%Y-%m-%d')
                    st.metric(
                        date_str[-5:],
                        f"{day['temperature']}°C",
                        f"{day['rainfall']}mm"
                    )
    except Exception as e:
        st.warning(f"Unable to load weather summary: {str(e)}")
    
    st.divider()
    
    # Render calendar
    render_calendar(
        st.session_state.current_year,
        st.session_state.current_month,
        calendar_events,
        lang
    )
    
    # Show selected event details with weather
    if st.session_state.get('selected_event'):
        event = st.session_state.selected_event
        
        st.divider()
        st.subheader("📝 Event Details")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"### {event['extendedProps']['heading']}")
            st.write(event['extendedProps'].get('description', 'No description'))
            
            if event['extendedProps'].get('weather_alert'):
                st.info(f"🌦️ {event['extendedProps']['weather_alert']}")
        
        with col2:
            event_date = event['start'].split('T')[0]
            st.metric("📅 Date", event_date)
            
            if st.button("🗑️ Delete Event", use_container_width=True, type="secondary"):
                delete_event(event['id'])
                st.session_state.selected_event = None
                st.success("✅ Event deleted!")
                st.rerun()
