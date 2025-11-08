"""Custom calendar component"""

import streamlit as st
import calendar as cal
from calender.utils import localize_number, get_events_for_date, truncate_text
from calender.config import MONTH_NAMES, DAY_NAMES, TRANSLATIONS


def render_calendar(year, month, events, lang):
    """Render custom calendar view"""
    
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
                    if day_events:
                        has_events = True
                        # Create larger cell with better visibility
                        cell_content = f"""
                        <div style='background-color: #E8F5E9; padding: 10px; border-radius: 8px; 
                                    min-height: 120px; border: 3px solid #4CAF50;'>
                            <div style='text-align: center; font-size: 20px; font-weight: bold; 
                                        color: #1B5E20; margin-bottom: 8px;'>{day_localized}</div>
                        """
                        st.markdown(cell_content, unsafe_allow_html=True)
                        
                        # Show event buttons with better text display
                        for idx, event in enumerate(day_events):
                            event_title = event['extendedProps']['heading']
                            
                            # Create a styled button-like div for better text display
                            button_html = f"""
                            <style>
                                .event-btn-{event['id']}-{day} {{
                                    background-color: #4CAF50;
                                    color: white;
                                    padding: 8px;
                                    border-radius: 5px;
                                    margin: 4px 0;
                                    cursor: pointer;
                                    font-size: 13px;
                                    word-wrap: break-word;
                                    line-height: 1.3;
                                    min-height: 45px;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                    text-align: center;
                                }}
                                .event-btn-{event['id']}-{day}:hover {{
                                    background-color: #45a049;
                                }}
                            </style>
                            """
                            st.markdown(button_html, unsafe_allow_html=True)
                            
                            # Use regular button but with better formatting
                            display_title = event_title if len(event_title) <= 25 else event_title[:25] + "..."
                            if st.button(
                                f"📝\n{display_title}", 
                                key=f"event_{event['id']}_{day}_{idx}",
                                width='stretch',
                                help=event_title
                            ):
                                st.session_state.selected_event = event
                                st.rerun()
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        # Regular day with bigger size and dark text
                        st.markdown(
                            f"""<div style='text-align: center; padding: 20px; min-height: 120px; 
                                          border: 2px solid #BDBDBD; border-radius: 8px; 
                                          background-color: #FAFAFA; font-size: 20px; font-weight: bold; 
                                          color: #212121;'>{day_localized}</div>""", 
                            unsafe_allow_html=True
                        )
        
        # Add spacing between weeks
        if week_num < len(month_calendar) - 1:
            st.markdown("<div style='margin: 10px 0;'></div>", unsafe_allow_html=True)
    
    # Show message if no events
    if not has_events:
        st.info(f"ℹ️ {TRANSLATIONS[lang]['no_events']}")
