# components/home_page.py

import streamlit as st
import pandas as pd
from database.db_functions import get_data
from datetime import datetime
from calender.utils import get_events_for_date
from components.translation_utils import t

def render_home_page():
    """
    SIMPLIFIED dashboard for farmers - Clean, Big buttons, Easy to understand
    """
    # Enhanced CSS for farmer-friendly design
    st.markdown("""
    <style>
    /* Big Button Cards */
    .big-action-card {
        background: linear-gradient(135deg, #E8F5E9 0%, #F1F8E9 100%);
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        border: 3px solid #4CAF50;
        margin: 10px 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .big-action-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        border-color: #2E8B57;
    }
    
    .big-action-emoji {
        font-size: 60px;
        margin-bottom: 10px;
    }
    
    .big-action-title {
        font-size: 24px;
        font-weight: bold;
        color: #2E8B57;
        margin: 10px 0;
    }
    
    .big-action-desc {
        font-size: 14px;
        color: #666;
    }
    
    /* Info Cards */
    .info-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #2E8B57;
        margin: 15px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .big-action-emoji { font-size: 50px; }
        .big-action-title { font-size: 20px; }
        .big-action-desc { font-size: 12px; }
        
        [data-testid="column"] {
            min-width: 100% !important;
            margin-bottom: 15px;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    farmer_name = st.session_state.get("farmer_name", "Farmer")
    farmer_profile = st.session_state.get("farmer_profile", {})
    
    # Personalized Welcome Header - Simpler
    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = t("Good Morning")
        emoji = "🌅"
    elif current_hour < 17:
        greeting = t("Good Afternoon")
        emoji = "☀️"
    else:
        greeting = t("Good Evening")
        emoji = "🌙"
    
    # Simple welcome banner
    from components.translation_utils import translate_location, convert_numbers_to_local
    location = farmer_profile.get('location', 'Not set')
    localized_location = translate_location(location)
    
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #4CAF50 0%, #2E8B57 100%); 
                padding: 25px; border-radius: 15px; color: white; text-align: center; 
                margin-bottom: 30px; box-shadow: 0 4px 12px rgba(0,0,0,0.2);'>
        <h2 style='color: white; margin: 0;'>{emoji} {greeting}, {farmer_name}!</h2>
        <p style='margin: 10px 0 0 0; font-size: 16px; opacity: 0.95;'>
            📍 {localized_location} • {datetime.now().strftime('%d %B %Y')}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # BIG ACTION BUTTONS - What farmers need DAILY
    st.markdown(f"## 🎯 {t('What do you need today?')}")
    
    # URGENT FEATURE HIGHLIGHT - Worker Board
    st.markdown("""
    <div style='background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%); 
                padding: 20px; border-radius: 12px; margin: 15px 0; 
                border: 3px solid #E65100; text-align: center;'>
        <h3 style='color: white; margin: 0;'>🔥 NEW! MOST NEEDED FEATURE 🔥</h3>
        <p style='color: white; margin: 10px 0 5px 0; font-size: 18px; font-weight: bold;'>
            👷 FIND WORKERS / POST JOBS
        </p>
        <p style='color: white; margin: 0; font-size: 14px;'>
            Harvest time? Need workers? Workers need jobs? Click below! ⬇️
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Worker Board Button - MOST PROMINENT
    if st.button("👷 WORKER BOARD - FIND WORKERS NOW!", key="worker_board_btn", use_container_width=True, type="primary"):
        st.session_state.nav_history.append(st.session_state.selected_menu)
        st.session_state.nav_forward = []
        st.session_state.selected_menu = "👷 Worker Board"
        st.rerun()
    
    st.markdown("---")
    st.markdown("")
    
    # Row 1: Most critical daily actions
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💰", key="price_btn", use_container_width=True):
            st.session_state.nav_history.append(st.session_state.selected_menu)
            st.session_state.nav_forward = []
            st.session_state.selected_menu = "💰 Today's Market Price"
            st.rerun()
        st.markdown(f"<div class='big-action-title'>{t('Check Today Price')}</div>", unsafe_allow_html=True)
        st.caption(t("See mandi prices now"))
    
    with col2:
        if st.button("🌤️", key="weather_btn", use_container_width=True):
            st.session_state.nav_history.append(st.session_state.selected_menu)
            st.session_state.nav_forward = []
            st.session_state.selected_menu = "🌤️ Weather Forecast"
            st.rerun()
        st.markdown(f"<div class='big-action-title'>{t('Weather Forecast')}</div>", unsafe_allow_html=True)
        st.caption(t("Plan your farm work"))
    
    st.markdown("")
    
    # Row 2: Secondary actions
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🛍️", key="browse_btn", use_container_width=True):
            st.session_state.nav_history.append(st.session_state.selected_menu)
            st.session_state.nav_forward = []
            st.session_state.selected_menu = "🛍️ Browse Listings"
            st.rerun()
        st.markdown(f"<div class='big-action-title'>{t('Browse Market')}</div>", unsafe_allow_html=True)
        st.caption(t("See tools and crops"))
    
    with col2:
        if st.button("➕", key="post_btn", use_container_width=True):
            st.session_state.nav_history.append(st.session_state.selected_menu)
            st.session_state.nav_forward = []
            st.session_state.selected_menu = "➕ Post Listing"
            st.rerun()
        st.markdown(f"<div class='big-action-title'>{t('Sell/Rent')}</div>", unsafe_allow_html=True)
        st.caption(t("List your crop or tool"))
    
    st.markdown("")
    
    # Row 3: Money tracker and Help
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📒", key="money_btn_home", use_container_width=True):
            st.session_state.nav_history.append(st.session_state.selected_menu)
            st.session_state.nav_forward = []
            st.session_state.selected_menu = "💰 My Money Diary"
            st.rerun()
        st.markdown(f"<div class='big-action-title'>{t('My Money')}</div>", unsafe_allow_html=True)
        st.caption(t("Track income/expense"))
    
    with col2:
        if st.button("🤖", key="ai_btn_home", use_container_width=True):
            st.session_state.nav_history.append(st.session_state.selected_menu)
            st.session_state.nav_forward = []
            st.session_state.selected_menu = "🤖 AI Chatbot"
            st.rerun()
        st.markdown(f"<div class='big-action-title'>{t('Ask AI Advisor')}</div>", unsafe_allow_html=True)
        st.caption(t("Find benefits for you"))
    
    st.divider()
    
    # Today's Tasks - Always visible, NO dropdown/expander
    st.markdown(f"## 📋 {t('Today Tasks & Reminders')}")
    
    try:
        today = datetime.now().date()
        events = get_events_for_date(farmer_name, today)
        
        if events and len(events) > 0:
            for event in events[:3]:  # Show only 3 tasks
                event_time = event.get('time', 'All day')
                event_title = event.get('title', 'Untitled task')
                
                # Choose emoji based on event type
                if 'irrigation' in event_title.lower() or 'water' in event_title.lower():
                    icon = "💧"
                elif 'fertilizer' in event_title.lower():
                    icon = "🌱"
                elif 'harvest' in event_title.lower():
                    icon = "🌾"
                elif 'plant' in event_title.lower():
                    icon = "🌿"
                else:
                    icon = "📌"
                
                st.markdown(f"{icon} **{event_time}** - {event_title}")
            
            st.markdown("")
            if st.button(f"📅 {t('View All Tasks')}", key="view_all_tasks", use_container_width=True):
                st.session_state.nav_history.append(st.session_state.selected_menu)
                st.session_state.nav_forward = []
                st.session_state.selected_menu = "📅 My Calendar"
                st.rerun()
        else:
            st.info(f"✅ {t('No tasks scheduled for today. You are all set!')}")
            st.markdown("")
            if st.button(f"📅 {t('Visit Calendar to plan your day')}", key="add_task_home", use_container_width=True, type="primary"):
                st.session_state.nav_history.append(st.session_state.selected_menu)
                st.session_state.nav_forward = []
                st.session_state.selected_menu = "📅 My Calendar"
                st.rerun()
    except Exception as e:
        st.info(f"📅 {t('Visit Calendar to plan your day')}")
        st.markdown("")
        if st.button(f"📅 {t('Open Calendar')}", key="calendar_error", use_container_width=True, type="primary"):
            st.session_state.nav_history.append(st.session_state.selected_menu)
            st.session_state.nav_forward = []
            st.session_state.selected_menu = "📅 My Calendar"
            st.rerun()
    
    st.divider()
    
    # My Listings Summary - Simple metrics
    tools_df = st.session_state.get('tools', pd.DataFrame())
    crops_df = st.session_state.get('crops', pd.DataFrame())
    
    if not tools_df.empty and 'Farmer' in tools_df.columns:
        my_tools = len(tools_df[tools_df['Farmer'] == farmer_name])
    else:
        my_tools = 0
    
    if not crops_df.empty and 'Farmer' in crops_df.columns:
        my_crops = len(crops_df[crops_df['Farmer'] == farmer_name])
    else:
        my_crops = 0
    
    total_listings = my_tools + my_crops
    
    if total_listings > 0:
        st.markdown(f"""
        <div class='info-card'>
            <h3 style='margin: 0 0 10px 0; color: #2E8B57;'>📦 {t('My Listings')}</h3>
            <p style='font-size: 18px; margin: 5px 0;'>
                🔧 {my_tools} {t('Tools')} • 🌾 {my_crops} {t('Crops')} • 
                <strong>Total: {total_listings}</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"👁️ {t('View My Listings')}", key="view_listings_btn", use_container_width=True):
            st.session_state.nav_history.append(st.session_state.selected_menu)
            st.session_state.nav_forward = []
            st.session_state.selected_menu = "📦 My Listings"
            st.rerun()
    else:
        st.info(f"📝 {t('You have not listed anything yet. Start selling or renting now!')}")
        if st.button(f"➕ {t('Create First Listing')}", key="first_listing_btn", use_container_width=True, type="primary"):
            st.session_state.nav_history.append(st.session_state.selected_menu)
            st.session_state.nav_forward = []
            st.session_state.selected_menu = "➕ Post Listing"
            st.rerun()
    
    st.markdown("")


def render_db_check():
    """
    Displays a read-only view of the 'tools' and 'crops' tables.
    Uses tabs for each table and shows success/error messages with record counts.
    """
    st.session_state  # Ensure session state is accessible

    # Tabs for tools and crops
    tab_tools, tab_crops = st.tabs(["Tools Table", "Crops Table"])

    # Tools Table
    with tab_tools:
        try:
            tools_df = get_data("tools")
            if tools_df.empty:
                st.warning("No records found in the 'tools' table.")
            else:
                st.dataframe(tools_df)
                st.success(f"Loaded {len(tools_df)} records from 'tools'.")
        except Exception as e:
            st.error(f"Error loading 'tools' table: {e}")

    # Crops Table
    with tab_crops:
        try:
            crops_df = get_data("crops")
            if crops_df.empty:
                st.warning("No records found in the 'crops' table.")
            else:
                st.dataframe(crops_df)
                st.success(f"Loaded {len(crops_df)} records from 'crops'.")
        except Exception as e:
            st.error(f"Error loading 'crops' table: {e}")


