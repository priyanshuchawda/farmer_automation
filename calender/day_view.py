"""Day view component for calendar - Google Calendar style"""

import streamlit as st
from datetime import datetime, timedelta
from calender.utils import localize_number
from calender.config import MONTH_NAMES, DAY_NAMES, TRANSLATIONS
from weather.api_client import OpenWeatherAPI
from database.db_functions import get_farmer_profile


def get_hourly_weather(farmer_profile, date):
    """Get hourly weather forecast for specific date"""
    if not farmer_profile:
        return None
    
    lat = farmer_profile.get('latitude')
    lon = farmer_profile.get('longitude')
    
    if not lat or not lon:
        return None
    
    try:
        weather_api = OpenWeatherAPI()
        detailed_forecast = weather_api.get_detailed_forecast(lat, lon)
        
        if detailed_forecast is not None and not detailed_forecast.empty:
            # Filter for the specific date
            day_weather = detailed_forecast[detailed_forecast['date'] == date].copy()
            return day_weather
    except Exception as e:
        print(f"Error getting hourly weather: {e}")
        return None


def render_day_view(year, month, day, events, lang):
    """Render day view with hourly schedule like Google Calendar"""
    
    # Mobile responsive CSS for day view
    st.markdown("""
    <style>
    @media (max-width: 768px) {
        /* Stack navigation columns on mobile */
        [data-testid="column"] {
            min-width: 100% !important;
            margin-bottom: 5px;
        }
        
        /* Compact buttons */
        .stButton>button {
            padding: 8px 12px !important;
            font-size: 0.85rem !important;
        }
        
        /* Smaller headers */
        h3 {
            font-size: 1.1rem !important;
        }
        
        /* Compact time slots */
        .time-slot {
            padding: 8px !important;
            font-size: 0.85rem !important;
        }
    }
    
    @media (max-width: 480px) {
        .stButton>button {
            padding: 6px 10px !important;
            font-size: 0.8rem !important;
        }
        
        h3 {
            font-size: 1rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Date navigation
    col1, col2, col3, col4 = st.columns([1, 1, 2, 1])
    
    current_date = datetime(year, month, day)
    date_str = f"{year:04d}-{month:02d}-{day:02d}"
    
    with col1:
        if st.button("← Prev Day", key="prev_day", use_container_width=True):
            new_date = current_date - timedelta(days=1)
            st.session_state.current_year = new_date.year
            st.session_state.current_month = new_date.month
            st.session_state.current_day = new_date.day
            st.rerun()
    
    with col2:
        if st.button("📆 Week", key="to_week", use_container_width=True, help="Go to week view"):
            st.session_state.calendar_view = "week"
            st.rerun()
    
    with col3:
        month_name = MONTH_NAMES[lang][month - 1]
        day_name = DAY_NAMES[lang][current_date.weekday()]
        day_localized = localize_number(day, lang)
        year_localized = localize_number(year, lang)
        
        st.markdown(
            f"### :green[{day_name}, {day_localized} {month_name} {year_localized}]"
        )
    
    with col4:
        if st.button("Next Day →", key="next_day", use_container_width=True):
            new_date = current_date + timedelta(days=1)
            st.session_state.current_year = new_date.year
            st.session_state.current_month = new_date.month
            st.session_state.current_day = new_date.day
            st.rerun()
    
    st.divider()
    
    # Get farmer profile for weather
    farmer_name = st.session_state.get("farmer_name")
    farmer_profile = get_farmer_profile(farmer_name) if farmer_name else None
    
    # Get hourly weather for this day
    hourly_weather = get_hourly_weather(farmer_profile, current_date.date())
    
    # Filter events for this specific day
    day_events = [e for e in events if e['start'].startswith(date_str)]
    
    # Current time tracking
    current_hour = datetime.now().hour
    current_minute = datetime.now().minute
    current_day_is_today = current_date.date() == datetime.now().date()
    
    # Create time slots
    for hour in range(6, 23):  # 6 AM to 10 PM
        hour_12 = hour if hour <= 12 else hour - 12
        hour_12 = 12 if hour_12 == 0 else hour_12
        am_pm = "AM" if hour < 12 else "PM"
        time_label = f"{hour_12:02d}:00 {am_pm}"
        
        # Find events for this hour
        hour_events = []
        for event in day_events:
            event_time = event.get('extendedProps', {}).get('time', '09:00')
            try:
                event_hour = int(event_time.split(':')[0])
                if event_hour == hour:
                    hour_events.append(event)
            except (ValueError, IndexError):
                continue
        
        # Get weather for this hour
        weather_data = None
        if hourly_weather is not None and not hourly_weather.empty:
            for _, weather_row in hourly_weather.iterrows():
                weather_hour = weather_row['datetime'].hour
                if abs(weather_hour - hour) <= 1:
                    weather_data = weather_row
                    break
        
        # Render time slot
        col_time, col_content = st.columns([1, 5])
        
        with col_time:
            # Highlight current hour
            if current_day_is_today and hour == current_hour:
                st.markdown(f"**:red[{time_label}]**")
                st.caption(f":red[Now: {current_hour}:{current_minute:02d}]")
            else:
                st.markdown(f"**{time_label}**")
        
        with col_content:
            # Render events for this hour
            if hour_events:
                for event in hour_events:
                    event_title = event['extendedProps']['heading']
                    event_desc = event['extendedProps'].get('description', '')
                    event_time = event.get('extendedProps', {}).get('time', '09:00')
                    weather_alert = event['extendedProps'].get('weather_alert', '')
                    
                    # Truncate description
                    short_desc = event_desc[:80] + "..." if len(event_desc) > 80 else event_desc
                    
                    # Event container
                    with st.container(border=True):
                        st.markdown(f"🕐 **{event_time}** - :green[**{event_title}**]")
                        if short_desc:
                            st.caption(short_desc)
                        if weather_alert:
                            st.info(f"🌦️ {weather_alert}", icon="⚠️")
                        
                        # View button
                        if st.button("📝 View Details", key=f"view_{event['id']}_{hour}", use_container_width=True):
                            st.session_state.selected_event = event
                            st.rerun()
            
            # Show weather if no events
            elif weather_data is not None:
                temp = weather_data['temp']
                rain = weather_data['rain']
                humidity = weather_data['humidity']
                clouds = weather_data['clouds']
                
                # Weather icon
                if rain > 2:
                    weather_icon = "🌧️"
                elif clouds > 70:
                    weather_icon = "☁️"
                elif temp > 30:
                    weather_icon = "☀️"
                else:
                    weather_icon = "⛅"
                
                # Weather display
                weather_col1, weather_col2, weather_col3, weather_col4 = st.columns(4)
                with weather_col1:
                    st.metric(label="Temperature", value=f"{weather_icon} {temp:.0f}°C", label_visibility="collapsed")
                with weather_col2:
                    st.metric(label="Humidity", value=f"{humidity}%")
                with weather_col3:
                    st.metric(label="Clouds", value=f"{clouds}%")
                with weather_col4:
                    if rain > 0:
                        st.metric(label="Rain", value=f"{rain:.1f}mm")
            else:
                st.caption("_No events scheduled_")
        
        # Divider between hours
        if hour < 22:
            st.divider()
    
    # Add event button
    st.divider()
    col1, col2, col3 = st.columns([2, 2, 2])
    with col2:
        if st.button("➕ Add Event for This Day", use_container_width=True, type="primary"):
            st.session_state.show_quick_add = True
            st.rerun()
    
    # Show events summary at bottom
    if day_events:
        st.divider()
        st.markdown(f"### 📋 All Events Today ({len(day_events)})")
        
        # Sort events by time
        sorted_events = sorted(
            day_events, 
            key=lambda x: x.get('extendedProps', {}).get('time', '09:00')
        )
        
        for idx, event in enumerate(sorted_events):
            event_time = event.get('extendedProps', {}).get('time', '09:00')
            event_title = event['extendedProps']['heading']
            event_desc = event['extendedProps'].get('description', '')
            
            with st.expander(f"🕐 {event_time} - {event_title}"):
                if event_desc:
                    st.write(event_desc)
                else:
                    st.caption("_No description_")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📝 Edit", key=f"edit_summary_{event['id']}", use_container_width=True):
                        st.session_state.selected_event = event
                        st.session_state.edit_mode = True
                        st.rerun()
                with col2:
                    if st.button("🗑️ Delete", key=f"delete_summary_{event['id']}", use_container_width=True):
                        st.session_state.delete_event_id = event['id']
                        st.rerun()
    else:
        st.info("📅 No events scheduled for this day. Click 'Add Event' to create one!")


