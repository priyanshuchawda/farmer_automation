"""Event display and editing component"""

import streamlit as st
from calender.utils import localize_number, format_date, format_time
from calender.config import TRANSLATIONS


def render_event_details(event, lang, editing=False):
    """Render event details with edit/view mode"""
    
    if editing:
        st.subheader(f"✏️ {TRANSLATIONS[lang]['edit']}")
        
        # Edit heading
        new_heading = st.text_input(
            TRANSLATIONS[lang]["heading_label"],
            value=event["extendedProps"]["heading"],
            key="edit_heading"
        )
        
        # Edit plan steps
        st.write(f"**{TRANSLATIONS[lang]['plan_label']}**")
        for i, step in enumerate(event["extendedProps"]["plan"]):
            step_num = localize_number(step['step_number'], lang)
            step_label = TRANSLATIONS[lang]['step_label']
            
            with st.expander(f"{step_label} {step_num}: {step['title']}", expanded=True):
                event["extendedProps"]["plan"][i]['description'] = st.text_area(
                    "Description",
                    step['description'],
                    height=100,
                    key=f"edit_step_{i}",
                    label_visibility="collapsed"
                )
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button(TRANSLATIONS[lang]["save_changes"], use_container_width=True, type="primary"):
                event["extendedProps"]["heading"] = new_heading
                event["title"] = f"{new_heading} 📝"
                st.session_state.editing = False
                st.success(TRANSLATIONS[lang]["success_updated"])
                st.rerun()
        
        with col2:
            if st.button(TRANSLATIONS[lang]["cancel"], use_container_width=True):
                st.session_state.editing = False
                st.rerun()
        
        with col3:
            if st.button(TRANSLATIONS[lang]["delete"], use_container_width=True, type="secondary"):
                st.session_state.events = [
                    e for e in st.session_state.events if e["id"] != event["id"]
                ]
                st.session_state.editing = False
                st.session_state.selected_event = None
                st.success(TRANSLATIONS[lang]["success_deleted"])
                st.rerun()
    
    else:
        # View mode
        st.subheader(f"📋 {event['extendedProps']['heading']}")
        
        # Display date and time info
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**{TRANSLATIONS[lang]['date_label']}** {format_date(event['start'])}")
        with col2:
            st.info(f"**{TRANSLATIONS[lang]['time_label']}** {format_time(event['start'])} - {format_time(event['end'])}")
        
        st.divider()
        
        # Display plan steps
        st.write(f"**{TRANSLATIONS[lang]['plan_label']}**")
        for step in event["extendedProps"]["plan"]:
            step_num = localize_number(step['step_number'], lang)
            step_label = TRANSLATIONS[lang]['step_label']
            
            with st.expander(f"{step_label} {step_num}: {step['title']}", expanded=False):
                st.write(step['description'])
        
        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button(TRANSLATIONS[lang]["edit"], use_container_width=True, type="primary"):
                st.session_state.editing = True
                st.rerun()
        
        with col2:
            if st.button(TRANSLATIONS[lang]["close"], use_container_width=True):
                st.session_state.selected_event = None
                st.rerun()
