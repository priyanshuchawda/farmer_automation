"""Custom calendar component"""

import streamlit as st
import calendar as cal
from calender.utils import localize_number, get_events_for_date, truncate_text
from calender.config import MONTH_NAMES, DAY_NAMES, TRANSLATIONS


def render_calendar(year, month, events, lang):
    """Render custom calendar view"""
    
    # Google Calendar-style responsive CSS
    st.markdown("""
    <style>
    /* Desktop: Full calendar view */
    div[data-testid="column"] button {
        font-size: 12px !important;
        padding: 4px 8px !important;
        min-height: 30px !important;
        line-height: 1.2 !important;
    }
    
    .calendar-cell {
        background-color: #ffffff;
        padding: 8px;
        border-radius: 8px;
        min-height: 120px;
        max-height: 120px;
        border: 2px solid;
        overflow: hidden;
        display: flex;
        flex-direction: column;
    }
    
    .calendar-day-number {
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        color: #1B5E20;
        margin-bottom: 6px;
    }
    
    .calendar-day-header {
        text-align: center;
        font-weight: bold;
        color: #0D47A1;
        padding: 15px;
        font-size: 17px;
        background-color: #BBDEFB;
        border-radius: 5px;
        border: 2px solid #1976D2;
    }
    
    /* Tablet: Medium-sized calendar */
    @media (max-width: 1024px) and (min-width: 769px) {
        .calendar-cell {
            min-height: 100px !important;
            max-height: 100px !important;
            padding: 6px !important;
        }
        
        .calendar-day-number {
            font-size: 16px !important;
        }
        
        .calendar-day-header {
            padding: 12px !important;
            font-size: 15px !important;
        }
        
        div[data-testid="column"] button {
            font-size: 11px !important;
            padding: 3px 6px !important;
        }
    }
    
    /* Mobile: Compact Google Calendar style (768px and below) */
    @media (max-width: 768px) {
        /* Remove column padding for tighter grid */
        div[data-testid="column"] {
            padding: 1px !important;
        }
        
        /* Compact calendar cells - Google Calendar mobile size */
        .calendar-cell {
            min-height: 70px !important;
            max-height: 70px !important;
            padding: 4px !important;
            border-radius: 6px !important;
            border-width: 1px !important;
        }
        
        /* Day numbers - prominent but compact */
        .calendar-day-number {
            font-size: 16px !important;
            margin-bottom: 3px !important;
        }
        
        /* Day headers - compact */
        .calendar-day-header {
            padding: 8px 2px !important;
            font-size: 12px !important;
            border-width: 1px !important;
        }
        
        /* Event buttons - Google Calendar style pills */
        div[data-testid="column"] button {
            font-size: 8px !important;
            padding: 2px 4px !important;
            min-height: 16px !important;
            line-height: 1 !important;
            border-radius: 8px !important;
            margin: 1px 0 !important;
        }
        
        /* Month navigation */
        .stButton>button {
            padding: 8px 10px !important;
            font-size: 14px !important;
        }
        
        /* Month title */
        h2 {
            font-size: 1.3rem !important;
        }
    }
    
    /* Small phones: Ultra-compact (480px and below) */
    @media (max-width: 480px) {
        /* Even more compact cells */
        .calendar-cell {
            min-height: 55px !important;
            max-height: 55px !important;
            padding: 3px !important;
            border-radius: 4px !important;
        }
        
        /* Smaller day numbers */
        .calendar-day-number {
            font-size: 13px !important;
            margin-bottom: 2px !important;
        }
        
        /* Ultra-compact day headers */
        .calendar-day-header {
            padding: 5px 1px !important;
            font-size: 10px !important;
            border-radius: 3px !important;
        }
        
        /* Tiny event indicators - just dots or very short text */
        div[data-testid="column"] button {
            font-size: 7px !important;
            padding: 1px 2px !important;
            min-height: 12px !important;
            margin: 0.5px 0 !important;
        }
        
        /* Smaller month navigation */
        .stButton>button {
            padding: 6px 8px !important;
            font-size: 12px !important;
        }
        
        /* Smaller month title */
        h2 {
            font-size: 1.1rem !important;
        }
    }
    
    /* Landscape mobile: Optimize for horizontal space */
    @media (max-width: 900px) and (orientation: landscape) {
        .calendar-cell {
            min-height: 50px !important;
            max-height: 50px !important;
        }
        
        .calendar-day-number {
            font-size: 12px !important;
        }
        
        div[data-testid="column"] button {
            font-size: 7px !important;
            padding: 1px 3px !important;
        }
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
            f"<div class='calendar-day-header'>{day}</div>", 
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
                    <div class='calendar-cell' style='background-color: {box_bg}; border-color: {box_border};'>
                        <div class='calendar-day-number'>{day_localized}</div>
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


