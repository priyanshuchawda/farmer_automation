"""Day view component for calendar"""

import streamlit as st
from datetime import datetime, timedelta
from calender.utils import localize_number
from calender.config import MONTH_NAMES, DAY_NAMES, TRANSLATIONS


def render_day_view(year, month, day, events, lang):
    """Render day view showing hourly schedule"""
    
    # Date navigation
    col1, col2, col3, col4 = st.columns([1, 1, 2, 1])
    
    current_date = datetime(year, month, day)
    
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
            f"<h2 style='text-align: center; color: #2E7D32;'>{day_name}, {day_localized} {month_name} {year_localized}</h2>", 
            unsafe_allow_html=True
        )
    
    with col4:
        if st.button("Next Day →", key="next_day", use_container_width=True):
            new_date = current_date + timedelta(days=1)
            st.session_state.current_year = new_date.year
            st.session_state.current_month = new_date.month
            st.session_state.current_day = new_date.day
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Filter events for this specific day
    date_str = f"{year:04d}-{month:02d}-{day:02d}"
    day_events = [e for e in events if e['start'].startswith(date_str)]
    
    if day_events:
        st.markdown(f"### 📅 Events for Today ({len(day_events)})")
        
        # Sort events by time
        day_events_sorted = sorted(day_events, key=lambda x: x.get('extendedProps', {}).get('time', '09:00'))
        
        for event in day_events_sorted:
            event_time = event.get('extendedProps', {}).get('time', '09:00')
            event_title = event['extendedProps']['heading']
            event_desc = event['extendedProps'].get('description', '')
            weather_alert = event['extendedProps'].get('weather_alert', '')
            
            with st.container():
                st.markdown(
                    f"""
                    <div style='background-color: #E8F5E9; padding: 20px; border-radius: 10px; 
                                margin-bottom: 15px; border-left: 5px solid #4CAF50;'>
                        <h3 style='color: #2E7D32; margin: 0;'>🕐 {event_time} - {event_title}</h3>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(event_desc)
                    if weather_alert:
                        st.info(f"🌦️ {weather_alert}")
                
                with col2:
                    if st.button("📝 View Details", key=f"view_event_{event['id']}", use_container_width=True):
                        st.session_state.selected_event = event
                        st.rerun()
    else:
        st.info(f"ℹ️ {TRANSLATIONS[lang]['no_events']}")
        st.markdown(
            """
            <div style='text-align: center; padding: 50px; color: #888;'>
                <h1 style='font-size: 80px;'>📅</h1>
                <p style='font-size: 18px;'>No events scheduled for this day</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Quick add event button
    st.divider()
    if st.button("➕ Add Event for This Day", use_container_width=True, type="primary"):
        st.session_state.add_event_date = date_str
        st.session_state.show_add_event = True
        st.rerun()
