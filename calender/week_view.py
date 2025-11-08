"""Week view component for calendar"""

import streamlit as st
from datetime import datetime, timedelta
from calender.utils import localize_number, get_events_for_date
from calender.config import MONTH_NAMES, DAY_NAMES, TRANSLATIONS


def get_week_dates(year, month, day):
    """Get the start and end dates of the week containing the given date"""
    current_date = datetime(year, month, day)
    # Get Monday of the current week (weekday() returns 0 for Monday)
    start_of_week = current_date - timedelta(days=current_date.weekday())
    week_dates = [start_of_week + timedelta(days=i) for i in range(7)]
    return week_dates


def render_week_view(year, month, day, events, lang):
    """Render week view showing 7 days with events"""
    
    # Get week dates
    week_dates = get_week_dates(year, month, day)
    start_date = week_dates[0]
    end_date = week_dates[6]
    
    # Week navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("← Previous Week", key="prev_week", use_container_width=True):
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
        
        st.markdown(
            f"<h2 style='text-align: center; color: #2E7D32;'>Week: {week_label}</h2>", 
            unsafe_allow_html=True
        )
    
    with col3:
        if st.button("Next Week →", key="next_week", use_container_width=True):
            new_date = end_date + timedelta(days=1)
            st.session_state.current_year = new_date.year
            st.session_state.current_month = new_date.month
            st.session_state.current_day = new_date.day
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
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
            
            # Styling based on state
            if is_today:
                bg_color = '#FFEB3B'  # Yellow for today
                border_color = '#F57C00'
                header_color = '#E65100'
            elif day_events:
                bg_color = '#E8F5E9'  # Light green for events
                border_color = '#4CAF50'
                header_color = '#2E7D32'
            else:
                bg_color = '#FFFFFF'  # White for empty days
                border_color = '#BDBDBD'
                header_color = '#616161'
            
            # Create day card
            st.markdown(
                f"""
                <div style='background-color: {bg_color}; padding: 10px; border-radius: 10px; 
                            border: 3px solid {border_color}; min-height: 400px; max-height: 400px;
                            overflow: hidden; display: flex; flex-direction: column;'>
                    <div style='text-align: center; border-bottom: 2px solid {border_color}; padding-bottom: 8px; margin-bottom: 10px;'>
                        <div style='font-weight: bold; color: {header_color}; font-size: 16px;'>{day_name}</div>
                        <div style='font-size: 24px; font-weight: bold; color: {header_color};'>{day_num}</div>
                        <div style='font-size: 12px; color: {header_color};'>{month_name}</div>
                    </div>
                    <div style='flex: 1; overflow-y: auto; overflow-x: hidden;'>
                """,
                unsafe_allow_html=True
            )
            
            # Display events
            if day_events:
                # Sort events by time
                day_events_sorted = sorted(day_events, key=lambda x: x.get('extendedProps', {}).get('time', '09:00'))
                
                for event_idx, event in enumerate(day_events_sorted):
                    event_time = event.get('extendedProps', {}).get('time', '09:00')
                    event_title = event['extendedProps']['heading']
                    
                    # Truncate title for display
                    display_title = event_title if len(event_title) <= 25 else event_title[:25] + "..."
                    
                    # Event button with time
                    if st.button(
                        f"🕐 {event_time}\n📝 {display_title}",
                        key=f"week_event_{event['id']}_{idx}_{event_idx}",
                        use_container_width=True,
                        help=f"{event_time} - {event_title}"
                    ):
                        st.session_state.selected_event = event
                        st.rerun()
                    
                    st.markdown("<div style='margin: 4px 0;'></div>", unsafe_allow_html=True)
            else:
                st.markdown(
                    "<div style='text-align: center; color: #999; padding: 20px; font-size: 14px;'>No events</div>",
                    unsafe_allow_html=True
                )
            
            # Close the divs
            st.markdown("</div></div>", unsafe_allow_html=True)
            
            # Button to add event for this day
            if st.button("➕ Add Event", key=f"add_week_{date_obj.strftime('%Y%m%d')}", use_container_width=True):
                st.session_state.add_event_date = date_str
                st.session_state.current_day = date_obj.day
                st.session_state.current_month = date_obj.month
                st.session_state.current_year = date_obj.year
                st.session_state.calendar_view = "day"
                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Week summary
    total_events = sum(1 for e in events if any(e['start'].startswith(d.strftime('%Y-%m-%d')) for d in week_dates))
    
    if total_events > 0:
        st.info(f"📊 Total events this week: {total_events}")
    else:
        st.info(f"ℹ️ {TRANSLATIONS[lang]['no_events']} this week")
