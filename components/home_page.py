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
    /* Professional Action Cards */
    .action-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 25px 20px;
        border-radius: 12px;
        text-align: center;
        border: 2px solid #e0e0e0;
        margin: 8px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
    }
    
    .action-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(46,139,87,0.15);
        border-color: #4CAF50;
    }
    
    .action-icon {
        font-size: 48px;
        margin-bottom: 12px;
        display: block;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
    }
    
    .action-title {
        font-size: 18px;
        font-weight: 600;
        color: #2E8B57;
        margin: 8px 0 4px 0;
        line-height: 1.3;
    }
    
    .action-desc {
        font-size: 13px;
        color: #666;
        line-height: 1.4;
    }
    
    /* Info Cards */
    .info-card {
        background: linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%);
        padding: 24px;
        border-radius: 12px;
        border-left: 4px solid #4CAF50;
        margin: 20px 0;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    }
    
    .stat-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #e8e8e8;
    }
    
    .stat-number {
        font-size: 32px;
        font-weight: bold;
        color: #2E8B57;
        margin: 8px 0;
    }
    
    .stat-label {
        font-size: 14px;
        color: #666;
        font-weight: 500;
    }
    
    /* Feature Highlight */
    .feature-highlight {
        background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%);
        padding: 24px;
        border-radius: 12px;
        margin: 20px 0;
        text-align: center;
        box-shadow: 0 4px 16px rgba(255,152,0,0.3);
        border: 2px solid #E65100;
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .action-icon { font-size: 40px; }
        .action-title { font-size: 16px; }
        .action-desc { font-size: 12px; }
        .stat-number { font-size: 28px; }
        
        [data-testid="column"] {
            min-width: 100% !important;
            margin-bottom: 12px;
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
    
    # Professional welcome banner
    from components.translation_utils import translate_location, convert_numbers_to_local
    location = farmer_profile.get('location', 'Not set')
    localized_location = translate_location(location)
    
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #4CAF50 0%, #2E8B57 100%); 
                padding: 30px 25px; border-radius: 16px; color: white; text-align: center; 
                margin-bottom: 32px; box-shadow: 0 6px 20px rgba(46,139,87,0.25);'>
        <div style='font-size: 48px; margin-bottom: 8px;'>{emoji}</div>
        <h1 style='color: white; margin: 0; font-size: 28px; font-weight: 600;'>{greeting}, {farmer_name}!</h1>
        <p style='margin: 12px 0 0 0; font-size: 15px; opacity: 0.95;'>
            📍 {localized_location} • {datetime.now().strftime('%d %B %Y')}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Actions Section
    st.markdown(f"""
    <div style='margin: 24px 0 16px 0;'>
        <h2 style='color: #2E8B57; font-size: 24px; font-weight: 600; margin: 0;'>
            🎯 {t('What do you need today?')}
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # URGENT FEATURE HIGHLIGHT - Worker Board
    st.markdown(f"""
    <div class='feature-highlight'>
        <div style='font-size: 28px; margin-bottom: 8px;'>🔥</div>
        <h3 style='color: white; margin: 0 0 8px 0; font-size: 20px; font-weight: 600;'>
            {t('NEW! MOST NEEDED FEATURE')}
        </h3>
        <p style='color: white; margin: 0 0 4px 0; font-size: 18px; font-weight: 600;'>
            👷 {t('FIND WORKERS / POST JOBS')}
        </p>
        <p style='color: rgba(255,255,255,0.95); margin: 0; font-size: 14px;'>
            {t('Harvest time? Need workers? Workers need jobs? Click below!')} ⬇️
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Worker Board Button - MOST PROMINENT
    if st.button("👷 WORKER BOARD - FIND WORKERS NOW!", key="worker_board_btn", use_container_width=True, type="primary"):
        st.session_state.nav_history.append(st.session_state.selected_menu)
        st.session_state.nav_forward = []
        st.session_state.selected_menu = "👷 Worker Board"
        st.rerun()
    
    st.markdown("<div style='margin: 28px 0;'></div>", unsafe_allow_html=True)
    
    # Row 1: Most critical daily actions
    col1, col2 = st.columns(2, gap="medium")
    
    with col1:
        st.markdown(f"""
        <div class='action-card'>
            <span class='action-icon'>💰</span>
            <div class='action-title'>{t('Check Today Price')}</div>
            <div class='action-desc'>{t('See mandi prices now')}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("View Prices", key="price_btn", use_container_width=True):
            st.session_state.nav_history.append(st.session_state.selected_menu)
            st.session_state.nav_forward = []
            st.session_state.selected_menu = "💰 Today's Market Price"
            st.rerun()
    
    with col2:
        st.markdown(f"""
        <div class='action-card'>
            <span class='action-icon'>🌤️</span>
            <div class='action-title'>{t('Weather Forecast')}</div>
            <div class='action-desc'>{t('Plan your farm work')}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Check Weather", key="weather_btn", use_container_width=True):
            st.session_state.nav_history.append(st.session_state.selected_menu)
            st.session_state.nav_forward = []
            st.session_state.selected_menu = "🌤️ Weather Forecast"
            st.rerun()
    
    st.markdown("<div style='margin: 16px 0;'></div>", unsafe_allow_html=True)
    
    # Row 2: Secondary actions
    col1, col2 = st.columns(2, gap="medium")
    
    with col1:
        st.markdown(f"""
        <div class='action-card'>
            <span class='action-icon'>🛍️</span>
            <div class='action-title'>{t('Browse Market')}</div>
            <div class='action-desc'>{t('See tools and crops')}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Browse Now", key="browse_btn", use_container_width=True):
            st.session_state.nav_history.append(st.session_state.selected_menu)
            st.session_state.nav_forward = []
            st.session_state.selected_menu = "🛍️ Browse Listings"
            st.rerun()
    
    with col2:
        st.markdown(f"""
        <div class='action-card'>
            <span class='action-icon'>➕</span>
            <div class='action-title'>{t('Sell/Rent')}</div>
            <div class='action-desc'>{t('List your crop or tool')}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Post Listing", key="post_btn", use_container_width=True):
            st.session_state.nav_history.append(st.session_state.selected_menu)
            st.session_state.nav_forward = []
            st.session_state.selected_menu = "➕ Post Listing"
            st.rerun()
    
    st.markdown("<div style='margin: 16px 0;'></div>", unsafe_allow_html=True)
    
    # Row 3: Money tracker and Help
    col1, col2 = st.columns(2, gap="medium")
    
    with col1:
        st.markdown(f"""
        <div class='action-card'>
            <span class='action-icon'>📒</span>
            <div class='action-title'>{t('My Money')}</div>
            <div class='action-desc'>{t('Track income/expense')}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Money Diary", key="money_btn_home", use_container_width=True):
            st.session_state.nav_history.append(st.session_state.selected_menu)
            st.session_state.nav_forward = []
            st.session_state.selected_menu = "💰 My Money Diary"
            st.rerun()
    
    with col2:
        st.markdown(f"""
        <div class='action-card'>
            <span class='action-icon'>🤖</span>
            <div class='action-title'>{t('Ask AI Advisor')}</div>
            <div class='action-desc'>{t('Find benefits for you')}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ask AI", key="ai_btn_home", use_container_width=True):
            st.session_state.nav_history.append(st.session_state.selected_menu)
            st.session_state.nav_forward = []
            st.session_state.selected_menu = "🤖 AI Chatbot"
            st.rerun()
    
    st.markdown("<div style='margin: 32px 0 24px 0;'><hr style='border: none; border-top: 2px solid #e0e0e0;'></div>", unsafe_allow_html=True)
    
    # Today's Tasks - Always visible, NO dropdown/expander
    st.markdown(f"""
    <div style='margin: 0 0 16px 0;'>
        <h2 style='color: #2E8B57; font-size: 22px; font-weight: 600; margin: 0;'>
            📋 {t('Today Tasks & Reminders')}
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
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
                
                st.markdown(f"""
                <div style='background: white; padding: 16px; border-radius: 8px; margin: 8px 0; 
                            border-left: 4px solid #4CAF50; box-shadow: 0 2px 6px rgba(0,0,0,0.06);'>
                    {icon} <strong style='color: #2E8B57;'>{event_time}</strong> - {event_title}
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<div style='margin: 16px 0;'></div>", unsafe_allow_html=True)
            if st.button(f"📅 {t('View All Tasks')}", key="view_all_tasks", use_container_width=True):
                st.session_state.nav_history.append(st.session_state.selected_menu)
                st.session_state.nav_forward = []
                st.session_state.selected_menu = "📅 My Calendar"
                st.rerun()
        else:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #E8F5E9 0%, #F1F8E9 100%); 
                        padding: 20px; border-radius: 10px; text-align: center; 
                        border: 2px solid #81C784;'>
                <div style='font-size: 36px; margin-bottom: 8px;'>✅</div>
                <p style='color: #2E7D32; font-weight: 500; margin: 0;'>
                    {t('No tasks scheduled for today. You are all set!')}
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<div style='margin: 12px 0;'></div>", unsafe_allow_html=True)
            if st.button(f"📅 {t('Visit Calendar to plan your day')}", key="add_task_home", use_container_width=True, type="primary"):
                st.session_state.nav_history.append(st.session_state.selected_menu)
                st.session_state.nav_forward = []
                st.session_state.selected_menu = "📅 My Calendar"
                st.rerun()
    except Exception as e:
        st.info(f"📅 {t('Visit Calendar to plan your day')}")
        st.markdown("<div style='margin: 12px 0;'></div>", unsafe_allow_html=True)
        if st.button(f"📅 {t('Open Calendar')}", key="calendar_error", use_container_width=True, type="primary"):
            st.session_state.nav_history.append(st.session_state.selected_menu)
            st.session_state.nav_forward = []
            st.session_state.selected_menu = "📅 My Calendar"
            st.rerun()
    
    st.markdown("<div style='margin: 32px 0 24px 0;'><hr style='border: none; border-top: 2px solid #e0e0e0;'></div>", unsafe_allow_html=True)
    
    # My Listings Summary - Beautiful stats cards
    st.markdown(f"""
    <div style='margin: 0 0 20px 0;'>
        <h2 style='color: #2E8B57; font-size: 22px; font-weight: 600; margin: 0;'>
            📦 {t('My Listings')}
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
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
        col1, col2, col3 = st.columns(3, gap="medium")
        
        with col1:
            st.markdown(f"""
            <div class='stat-card'>
                <div style='font-size: 32px; margin-bottom: 8px;'>🔧</div>
                <div class='stat-number'>{my_tools}</div>
                <div class='stat-label'>{t('Tools')}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='stat-card'>
                <div style='font-size: 32px; margin-bottom: 8px;'>🌾</div>
                <div class='stat-number'>{my_crops}</div>
                <div class='stat-label'>{t('Crops')}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class='stat-card' style='border: 2px solid #4CAF50;'>
                <div style='font-size: 32px; margin-bottom: 8px;'>📊</div>
                <div class='stat-number'>{total_listings}</div>
                <div class='stat-label'>{t('Total')}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
        if st.button(f"👁️ {t('View My Listings')}", key="view_listings_btn", use_container_width=True):
            st.session_state.nav_history.append(st.session_state.selected_menu)
            st.session_state.nav_forward = []
            st.session_state.selected_menu = "📦 My Listings"
            st.rerun()
    else:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%); 
                    padding: 24px; border-radius: 12px; text-align: center; 
                    border: 2px solid #FFB74D;'>
            <div style='font-size: 48px; margin-bottom: 12px;'>📝</div>
            <p style='color: #E65100; font-weight: 500; font-size: 16px; margin: 0 0 8px 0;'>
                {t('You have not listed anything yet.')}
            </p>
            <p style='color: #F57C00; font-size: 14px; margin: 0;'>
                {t('Start selling or renting now!')}
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='margin: 16px 0;'></div>", unsafe_allow_html=True)
        if st.button(f"➕ {t('Create First Listing')}", key="first_listing_btn", use_container_width=True, type="primary"):
            st.session_state.nav_history.append(st.session_state.selected_menu)
            st.session_state.nav_forward = []
            st.session_state.selected_menu = "➕ Post Listing"
            st.rerun()
    
    st.markdown("<div style='margin: 24px 0;'></div>", unsafe_allow_html=True)


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


