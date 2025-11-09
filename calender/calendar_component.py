"""Custom calendar component"""

import streamlit as st
import calendar as cal
from calender.utils import localize_number, get_events_for_date, truncate_text
from calender.config import MONTH_NAMES, DAY_NAMES, TRANSLATIONS


def render_calendar(year, month, events, lang):
    """Render custom calendar view"""
    
    # Add custom CSS for uniform day boxes and green buttons
    st.markdown("""
    <style>
    /* Ensure event buttons are compact and green */
    div[data-testid="column"] button {
        font-size: 12px !important;
        padding: 4px 8px !important;
        min-height: 30px !important;
        line-height: 1.2 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Month navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button(TRANSLATIONS[lang]["previous"], width='stretch'):
            st.session_state.current_month -= 1
            if st.session_state.current_month < 1:
                st.session_state.current_month = 12
                st.session_state.current_year -= 1
            st.rerun()
    
    with col2:
        month_name = MONTH_NAMES[lang][month - 1]
        year_localized = localize_number(year, lang)
        st.markdown(
            f"<h2 style='text-align: center; color: #2E7D32;'>{month_name} {year_localized}</h2>", 
            unsafe_allow_html=True
        )
    
    with col3:
        if st.button(TRANSLATIONS[lang]["next"], width='stretch'):
            st.session_state.current_month += 1
            if st.session_state.current_month > 12:
                st.session_state.current_month = 1
                st.session_state.current_year += 1
            st.rerun()
    
    # Get calendar for current month
    month_calendar = cal.monthcalendar(year, month)
    
    # Add some spacing
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Day headers with styling
    cols = st.columns(7)
    for i, day in enumerate(DAY_NAMES[lang]):
        cols[i].markdown(
            f"<div style='text-align: center; font-weight: bold; color: #0D47A1; padding: 15px; font-size: 17px; background-color: #BBDEFB; border-radius: 5px; border: 2px solid #1976D2;'>{day}</div>", 
            unsafe_allow_html=True
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Display calendar days
    has_events = False
    for week_num, week in enumerate(month_calendar):
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                cols[i].write("")
            else:
                day_events = get_events_for_date(events, year, month, day)
                day_localized = localize_number(day, lang)
                
                with cols[i]:
                    # Uniform box styling for all days
                    box_bg = '#E8F5E9' if day_events else '#FFFFFF'
                    box_border = '#4CAF50' if day_events else '#BDBDBD'
                    
                    # Create uniform cell with fixed height
                    cell_content = f"""
                    <div style='background-color: {box_bg}; padding: 8px; border-radius: 8px; 
                                min-height: 120px; max-height: 120px; border: 2px solid {box_border};
                                overflow: hidden; display: flex; flex-direction: column;'>
                        <div style='text-align: center; font-size: 18px; font-weight: bold; 
                                    color: #1B5E20; margin-bottom: 6px;'>{day_localized}</div>
                        <div style='flex: 1; overflow-y: auto; overflow-x: hidden;'>
                    """
                    st.markdown(cell_content, unsafe_allow_html=True)
                    
                    if day_events:
                        has_events = True
                        # Show limited event buttons inside the box (max 2)
                        for idx, event in enumerate(day_events[:2]):
                            event_title = event['extendedProps']['heading']
                            
                            # Compact event display
                            display_title = event_title if len(event_title) <= 18 else event_title[:18] + "..."
                            if st.button(
                                f"📝 {display_title}", 
                                key=f"event_{event['id']}_{day}_{idx}",
                                use_container_width=True,
                                help=event_title
                            ):
                                st.session_state.selected_event = event
                                st.rerun()
                        
                        # Show "more" indicator if there are more than 2 events
                        if len(day_events) > 2:
                            st.caption(f"+ {len(day_events) - 2} more")
                    
                    # Always show View Day button
                    view_day_clicked = st.button(
                        "📅 View Day",
                        key=f"day_{day}_{week_num}",
                        type="secondary",
                        help="Check hourly schedule"
                    )
                    if view_day_clicked:
                        st.session_state.current_day = day
                        st.session_state.current_month = month
                        st.session_state.current_year = year
                        st.session_state.calendar_view = "day"
                        st.rerun()
                    
                    # Close the divs
                    st.markdown("</div></div>", unsafe_allow_html=True)
        
        # Add spacing between weeks
        if week_num < len(month_calendar) - 1:
            st.markdown("<div style='margin: 8px 0;'></div>", unsafe_allow_html=True)
    
    # Show message if no events
    if not has_events:
        st.info(f"ℹ️ {TRANSLATIONS[lang]['no_events']}")


