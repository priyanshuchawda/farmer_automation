"""Smart Farming Calendar Assistant - Main Application"""

import streamlit as st
from datetime import datetime
from .config import TRANSLATIONS, LANGUAGE_OPTIONS
from .utils import localize_number, create_event_id
from .ai_service import AIService
from .calendar_component import render_calendar
from .event_component import render_event_details
from .translation_service import TranslationService

# --- Page Configuration ---
st.set_page_config(
    page_title="Smart Farming Calendar",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for better UI ---
st.markdown("""
<style>
    /* Light background for main content for better visibility */
    .main {
        background-color: #F1F8E9 !important;
    }
    
    /* Ensure main content text is always dark for readability */
    .main > div {
        color: #212121 !important;
    }
    
    .main h1, .main h2, .main h3, .main p, .main span, .main div {
        color: #212121 !important;
    }
    
    /* Buttons with good contrast */
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
        font-size: 14px;
        padding: 10px 12px;
        white-space: pre-wrap !important;
        word-wrap: break-word !important;
        height: auto !important;
        min-height: 50px !important;
        line-height: 1.4 !important;
        overflow-wrap: break-word !important;
        background-color: #4CAF50 !important;
        color: white !important;
        border: 2px solid #2E7D32 !important;
    }
    
    .stButton>button:hover {
        background-color: #45a049 !important;
        border-color: #1B5E20 !important;
    }
    
    .stButton>button p {
        white-space: pre-wrap !important;
        word-wrap: break-word !important;
        color: white !important;
    }
    
    /* Input fields with dark text */
    .stTextInput>div>div>input {
        border-radius: 10px;
        font-size: 16px;
        background-color: white !important;
        color: #212121 !important;
        border: 2px solid #BDBDBD !important;
    }
    
    .stTextArea>div>div>textarea {
        border-radius: 10px;
        font-size: 16px;
        background-color: white !important;
        color: #212121 !important;
        border: 2px solid #BDBDBD !important;
    }
    
    /* Headers with strong contrast */
    h1 {
        color: #1B5E20 !important;
        text-align: center;
        padding: 20px 0;
        font-size: 3rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    h2 {
        color: #2E7D32 !important;
        font-size: 2rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    h3 {
        color: #388E3C !important;
        font-size: 1.5rem;
    }
    
    /* Alerts with better visibility */
    .stAlert {
        border-radius: 10px;
        font-size: 16px;
        border: 2px solid !important;
    }
    
    /* Success alert */
    .stAlert[data-baseweb="notification"] {
        background-color: #E8F5E9 !important;
        border-color: #4CAF50 !important;
    }
    
    /* Info alert */
    .stInfo {
        background-color: #E3F2FD !important;
        border-color: #2196F3 !important;
        color: #0D47A1 !important;
    }
    
    /* Warning alert */
    .stWarning {
        background-color: #FFF3E0 !important;
        border-color: #FF9800 !important;
        color: #E65100 !important;
    }
    
    /* Error alert */
    .stError {
        background-color: #FFEBEE !important;
        border-color: #F44336 !important;
        color: #B71C1C !important;
    }
    
    /* Make calendar cells bigger */
    .element-container {
        margin-bottom: 8px;
    }
    
    /* Sidebar styling - adapt to theme */
    [data-testid="stSidebar"] {
        background-color: transparent !important;
    }
    
    /* Sidebar in light mode */
    [data-testid="stSidebar"][data-theme="light"] {
        background-color: #F5F5F5 !important;
    }
    
    /* Sidebar text should be readable */
    [data-testid="stSidebar"] * {
        color: inherit !important;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: inherit !important;
    }
    
    /* Metric values */
    [data-testid="stMetricValue"] {
        font-weight: bold !important;
    }
    
    /* Sidebar metrics in light mode */
    [data-testid="stSidebar"] [data-testid="stMetricValue"] {
        color: #2E7D32 !important;
    }
    
    /* Improve button text wrapping */
    button[kind="secondary"] {
        white-space: normal !important;
        word-wrap: break-word !important;
    }
    
    /* Expander headers */
    .streamlit-expanderHeader {
        background-color: #C8E6C9 !important;
        color: #1B5E20 !important;
        font-weight: bold !important;
    }
    
    /* Date/time inputs */
    input[type="date"], input[type="time"] {
        background-color: white !important;
        color: #212121 !important;
        border: 2px solid #BDBDBD !important;
    }
    
    /* Select boxes */
    .stSelectbox > div > div {
        background-color: white !important;
        color: #212121 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Initialize Session State ---
if 'lang' not in st.session_state:
    st.session_state.lang = "en"

if 'events' not in st.session_state:
    st.session_state.events = []

if 'selected_event' not in st.session_state:
    st.session_state.selected_event = None

if 'current_month' not in st.session_state:
    st.session_state.current_month = datetime.now().month

if 'current_year' not in st.session_state:
    st.session_state.current_year = datetime.now().year

if 'editing' not in st.session_state:
    st.session_state.editing = False

if 'original_events' not in st.session_state:
    st.session_state.original_events = []

if 'plan_original_lang' not in st.session_state:
    st.session_state.plan_original_lang = None

# --- Initialize Services ---
ai_service = AIService()
translation_service = TranslationService()

# --- Sidebar: Language Selection ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/628/628283.png", width=100)
    st.title(TRANSLATIONS[st.session_state.lang]["language_select"])
    
    st.caption("🌐 Auto-translation powered by Deep Translator")
    
    # Find current language display name
    current_lang_display = [k for k, v in LANGUAGE_OPTIONS.items() if v == st.session_state.lang][0]
    
    selected_lang_display = st.selectbox(
        "Select Language / भाषा चुनें / भाषा निवडा",
        list(LANGUAGE_OPTIONS.keys()),
        index=list(LANGUAGE_OPTIONS.keys()).index(current_lang_display),
        label_visibility="collapsed"
    )
    
    # Update language if changed
    new_lang = LANGUAGE_OPTIONS[selected_lang_display]
    if new_lang != st.session_state.lang:
        old_lang = st.session_state.lang
        st.session_state.lang = new_lang
        
        # Translate current plan if exists
        if 'plan_data' in st.session_state:
            with st.spinner("Translating plan..."):
                st.session_state.plan_data = translation_service.translate_plan(
                    st.session_state.plan_data, 
                    new_lang,
                    old_lang  # Pass source language
                )
        
        # Translate all events
        if st.session_state.events:
            with st.spinner("Translating events..."):
                translated_events = []
                for event in st.session_state.events:
                    translated_event = translation_service.translate_event(
                        event, 
                        new_lang,
                        old_lang  # Pass source language
                    )
                    translated_events.append(translated_event)
                st.session_state.events = translated_events
        
        st.rerun()
    
    st.divider()
    
    # Quick stats
    st.metric("Total Events", len(st.session_state.events))
    
    # Today's date
    today = datetime.now()
    today_str = f"{today.year}-{today.month:02d}-{today.day:02d}"
    today_events = [e for e in st.session_state.events if e["start"].startswith(today_str)]
    st.metric("Today's Tasks", len(today_events))

# --- Main Content ---
lang = st.session_state.lang

# Title and subtitle
st.title(TRANSLATIONS[lang]["title"])
st.markdown(f"<p style='text-align: center; color: #424242; font-size: 20px; font-weight: 500;'>{TRANSLATIONS[lang]['subtitle']}</p>", unsafe_allow_html=True)

st.divider()

# --- Section 1: Create Farming Plan ---
with st.expander(f"### {TRANSLATIONS[lang]['get_plan_header']}", expanded=True):
    st.write(TRANSLATIONS[lang]["get_plan_write"])
    
    # Show examples in an info box
    st.info(TRANSLATIONS[lang]["get_plan_example"])
    
    # User input
    prompt = st.text_area(
        TRANSLATIONS[lang]["enter_question"],
        height=100,
        placeholder="Type your farming question here...",
        key="user_prompt"
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(TRANSLATIONS[lang]["get_plan_button"], width="stretch", type="primary"):
            if prompt.strip():
                with st.spinner(TRANSLATIONS[lang]["loading"]):
                    plan_data, error = ai_service.generate_farming_plan(prompt, lang)
                    
                    if plan_data:
                        # Store the plan and translate if not in English
                        if lang != 'en':
                            # Translate to selected language
                            st.session_state.plan_data = translation_service.translate_plan(
                                plan_data, 
                                lang,
                                'en'  # AI generates in English
                            )
                        else:
                            st.session_state.plan_data = plan_data
                        
                        st.success("✅ Plan generated successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ {error}")
            else:
                st.warning("⚠️ Please enter a question first.")

# --- Section 2: Display Generated Plan ---
if 'plan_data' in st.session_state:
    st.divider()
    st.subheader(TRANSLATIONS[lang]["generated_plan_header"])
    
    # Display heading
    col1, col2 = st.columns([3, 1])
    with col1:
        edited_heading = st.text_input(
            TRANSLATIONS[lang]["heading_label"],
            st.session_state.plan_data['heading'],
            key="plan_heading"
        )
    
    # Display plan steps in cards
    st.write(f"**{TRANSLATIONS[lang]['plan_label']}**")
    for i, step in enumerate(st.session_state.plan_data['plan']):
        step_num = localize_number(step['step_number'], lang)
        step_label = TRANSLATIONS[lang]['step_label']
        
        with st.expander(f"**{step_label} {step_num}: {step['title']}**", expanded=True):
            st.session_state.plan_data['plan'][i]['description'] = st.text_area(
                "Description",
                step['description'],
                height=80,
                key=f"step_{i}",
                label_visibility="collapsed"
            )
    
    st.divider()
    
    # Schedule event
    st.write("### 📅 Schedule this plan")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        event_date = st.date_input(TRANSLATIONS[lang]["select_date"])
    
    with col2:
        start_time = st.time_input(TRANSLATIONS[lang]["select_start_time"])
    
    with col3:
        end_time = st.time_input(TRANSLATIONS[lang]["select_end_time"])
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(TRANSLATIONS[lang]["add_event_button"], width="stretch", type="primary"):
            event_start = f"{event_date}T{start_time}"
            event_end = f"{event_date}T{end_time}"
            event_id = create_event_id(st.session_state.events)
            
            event = {
                "id": event_id,
                "title": f"{edited_heading} 📝",
                "start": event_start,
                "end": event_end,
                "extendedProps": {
                    "plan": st.session_state.plan_data['plan'],
                    "heading": edited_heading
                }
            }
            
            st.session_state.events.append(event)
            del st.session_state.plan_data
            st.success(TRANSLATIONS[lang]["success_added"])
            st.rerun()

# --- Section 3: Calendar View ---
st.divider()
st.header(TRANSLATIONS[lang]["calendar_header"])

# Render custom calendar
render_calendar(
    st.session_state.current_year,
    st.session_state.current_month,
    st.session_state.events,
    lang
)

# --- Section 4: Event Details ---
if st.session_state.selected_event:
    st.divider()
    render_event_details(
        st.session_state.selected_event,
        lang,
        st.session_state.editing
    )

# --- Footer ---
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>🌾 Smart Farming Calendar Assistant | Powered by AI</p>
    <p style='font-size: 12px;'>Made with ❤️ for Farmers</p>
</div>
""", unsafe_allow_html=True)


