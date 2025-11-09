"""Week view component for calendar"""

import streamlit as st
from datetime import datetime, timedelta
from calender.utils import localize_number, get_events_for_date
from calender.config import MONTH_NAMES, DAY_NAMES, TRANSLATIONS
from weather.combined_forecast import get_weather_forecast
from database.db_functions import get_farmer_profile


def get_week_dates(year, month, day):
    """Get the start and end dates of the week containing the given date"""
    current_date = datetime(year, month, day)
    # Get Monday of the current week (weekday() returns 0 for Monday)
    start_of_week = current_date - timedelta(days=current_date.weekday())
    week_dates = [start_of_week + timedelta(days=i) for i in range(7)]
    return week_dates


def render_week_view(year, month, day, events, lang):
    """Render week view showing 7 days with events"""
    
    # Mobile responsive CSS for week view
    st.markdown("""
    <style>
    @media (max-width: 768px) {
        /* Stack week columns on mobile */
        [data-testid="column"] {
            min-width: 100% !important;
            margin-bottom: 10px;
        }
        
        /* Compact navigation */
        .stButton>button {
            padding: 8px 12px !important;
            font-size: 0.85rem !important;
        }
        
        /* Smaller week headers */
        h3 {
            font-size: 1.1rem !important;
        }
        
        /* Day cards */
        .week-day-card {
            padding: 10px !important;
            margin-bottom: 10px !important;
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
        
        .week-day-card {
            padding: 8px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Get week dates
    week_dates = get_week_dates(year, month, day)
    start_date = week_dates[0]
    end_date = week_dates[6]
    
    # Get farmer profile and weather
    farmer_name = st.session_state.get("farmer_name")
    farmer_profile = get_farmer_profile(farmer_name) if farmer_name else None
    
    # Get weather forecast
    weather_dict = {}
    if farmer_profile:
        try:
            forecast = get_weather_forecast(
                farmer_profile.get('weather_location'),
                lat=farmer_profile.get('latitude'),
                lon=farmer_profile.get('longitude')
            )
            if forecast:
                for day_weather in forecast:
                    date_str = str(day_weather['date']) if isinstance(day_weather['date'], str) else day_weather['date'].strftime('%Y-%m-%d')
                    weather_dict[date_str] = day_weather
        except:
            pass
    
    # Week navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("← Previous Week", key="prev_week", width="stretch"):
            new_date = start_date - timedelta(days=7)
            st.session_state.current_year = new_date.year
            st.session_state.current_month = new_date.month
            st.session_state.current_day = new_date.day
            st.rerun()
    
    with col2:
        # Display week range
        start_month = MONTH_NAMES[lang][start_date.month - 1]
        end_month = MONTH_NAMES[lang][end_date.month - 1]
        
        start_day = localize_number(start_date.day, lang)
        end_day = localize_number(end_date.day, lang)
        
        if start_date.month == end_date.month:
            week_label = f"{start_day} - {end_day} {start_month} {localize_number(year, lang)}"
        else:
            week_label = f"{start_day} {start_month} - {end_day} {end_month} {localize_number(year, lang)}"
        
        st.markdown(f"### :green[Week: {week_label}]")
    
    with col3:
        if st.button("Next Week →", key="next_week", width="stretch"):
            new_date = end_date + timedelta(days=1)
            st.session_state.current_year = new_date.year
            st.session_state.current_month = new_date.month
            st.session_state.current_day = new_date.day
            st.rerun()
    
    st.divider()
    
    # Display week in columns
    cols = st.columns(7)
    
    today = datetime.now().date()
    
    for idx, date_obj in enumerate(week_dates):
        with cols[idx]:
            day_name = DAY_NAMES[lang][date_obj.weekday()]
            day_num = localize_number(date_obj.day, lang)
            month_name = MONTH_NAMES[lang][date_obj.month - 1][:3]  # Short month name
            
            # Check if this is today
            is_today = date_obj.date() == today
            
            # Get events for this date
            date_str = date_obj.strftime('%Y-%m-%d')
            day_events = [e for e in events if e['start'].startswith(date_str)]
            
            # Get weather for this day
            day_weather = weather_dict.get(date_str)
            weather_icon = ""
            weather_temp = ""
            if day_weather:
                temp = day_weather.get('temperature', 0)
                rain = day_weather.get('rainfall', 0)
                
                if rain > 10:
                    weather_icon = "⛈️"
                elif rain > 2:
                    weather_icon = "🌧️"
                elif rain > 0:
                    weather_icon = "🌦️"
                elif temp > 32:
                    weather_icon = "☀️"
                elif temp < 15:
                    weather_icon = "❄️"
                else:
                    weather_icon = "⛅"
                
                weather_temp = f"{temp:.0f}°C"
            
            # Day card container with conditional styling
            if is_today:
                container_type = st.container(border=True)
                with container_type:
                    st.markdown(f"#### :orange[{day_name}]")
                    st.markdown(f"# :orange[{day_num}]")
                    st.caption(month_name)
                    if weather_icon and weather_temp:
                        st.markdown(f"## {weather_icon}")
                        st.markdown(f"**:blue[{weather_temp}]**")
                    st.markdown("---")
                    
                    # Display events
                    if day_events:
                        # Sort events by time
                        day_events_sorted = sorted(day_events, key=lambda x: x.get('extendedProps', {}).get('time', '09:00'))
                        
                        for event_idx, event in enumerate(day_events_sorted[:4]):  # Show max 4 events
                            event_time = event.get('extendedProps', {}).get('time', '09:00')
                            event_title = event['extendedProps']['heading']
                            
                            # Truncate title for display
                            display_title = event_title if len(event_title) <= 20 else event_title[:20] + "..."
                            
                            st.success(f"🕐 **{event_time}**  \n{display_title}", icon="✅")
                        
                        # Show indicator if more events
                        if len(day_events) > 4:
                            st.caption(f"_+ {len(day_events) - 4} more events_")
                    else:
                        st.info("📭 No events", icon="ℹ️")
            
            elif day_events:
                container_type = st.container(border=True)
                with container_type:
                    st.markdown(f"#### :green[{day_name}]")
                    st.markdown(f"# :green[{day_num}]")
                    st.caption(month_name)
                    if weather_icon and weather_temp:
                        st.markdown(f"## {weather_icon}")
                        st.markdown(f"**:blue[{weather_temp}]**")
                    st.markdown("---")
                    
                    # Display events
                    day_events_sorted = sorted(day_events, key=lambda x: x.get('extendedProps', {}).get('time', '09:00'))
                    
                    for event_idx, event in enumerate(day_events_sorted[:4]):  # Show max 4 events
                        event_time = event.get('extendedProps', {}).get('time', '09:00')
                        event_title = event['extendedProps']['heading']
                        
                        # Truncate title for display
                        display_title = event_title if len(event_title) <= 20 else event_title[:20] + "..."
                        
                        st.success(f"🕐 **{event_time}**  \n{display_title}", icon="🌱")
                    
                    # Show indicator if more events
                    if len(day_events) > 4:
                        st.caption(f"_+ {len(day_events) - 4} more events_")
            
            else:
                container_type = st.container(border=True)
                with container_type:
                    st.markdown(f"#### {day_name}")
                    st.markdown(f"# {day_num}")
                    st.caption(month_name)
                    if weather_icon and weather_temp:
                        st.markdown(f"## {weather_icon}")
                        st.markdown(f"**:blue[{weather_temp}]**")
                    st.markdown("---")
                    st.info("📭 No events", icon="ℹ️")
            
            # Buttons for actions
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button(
                    "📅 Day", 
                    key=f"view_day_{date_obj.strftime('%Y%m%d')}", 
                    help="Check hourly schedule",
                    width="stretch"
                ):
                    # Set all session state variables for day view
                    st.session_state.current_day = date_obj.day
                    st.session_state.current_month = date_obj.month
                    st.session_state.current_year = date_obj.year
                    st.session_state.calendar_view = "day"
                    st.rerun()
            
            with col_b:
                if st.button(
                    "➕", 
                    key=f"add_week_{date_obj.strftime('%Y%m%d')}", 
                    help="Add event",
                    width="stretch"
                ):
                    st.session_state.current_day = date_obj.day
                    st.session_state.current_month = date_obj.month
                    st.session_state.current_year = date_obj.year
                    st.session_state.show_quick_add = True
                    st.rerun()
    
    st.divider()
    
    # Week summary
    total_events = sum(1 for e in events if any(e['start'].startswith(d.strftime('%Y-%m-%d')) for d in week_dates))
    
    if total_events > 0:
        st.info(f"📊 Total events this week: **{total_events}**")
    else:
        st.info(f"ℹ️ {TRANSLATIONS[lang]['no_events']} this week")


