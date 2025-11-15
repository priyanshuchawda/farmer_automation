# components/home_page.py

import streamlit as st
import pandas as pd
import os
from database.db_functions import get_data
from datetime import datetime
from calender.utils import get_events_for_date
from components.translation_utils import t

def render_home_page():
    """
    SIMPLIFIED dashboard for farmers - Clean, Big buttons, Easy to understand
    """
    # Minimal CSS for professional design
    st.markdown("""
    <style>
    .action-card {
        background: white;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #ddd;
        margin: 8px 0;
    }
    
    .action-card:hover {
        border-color: #4CAF50;
    }
    
    .action-icon {
        font-size: 36px;
        margin-bottom: 8px;
        display: block;
    }
    
    .action-title {
        font-size: 16px;
        font-weight: 600;
        color: #2E8B57;
        margin: 4px 0;
    }
    
    .action-desc {
        font-size: 12px;
        color: #666;
    }
    
    .stat-card {
        background: white;
        padding: 16px;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #ddd;
    }
    
    .stat-number {
        font-size: 28px;
        font-weight: bold;
        color: #2E8B57;
        margin: 4px 0;
    }
    
    .stat-label {
        font-size: 13px;
        color: #666;
    }
    
    @media (max-width: 768px) {
        .action-icon { font-size: 32px; }
        .action-title { font-size: 15px; }
    }
    </style>
    """, unsafe_allow_html=True)
    
    farmer_name = st.session_state.get("farmer_name", "Farmer")
    farmer_profile = st.session_state.get("farmer_profile", {})
    
    # NEW: Climate Risk Alert Banner
    if farmer_profile and farmer_profile.get('latitude'):
        try:
            from weather.climate_analyzer import ClimateAnalyzer
            
            location = farmer_profile.get('weather_location', 'Unknown')
            lat = farmer_profile.get('latitude')
            lon = farmer_profile.get('longitude')
            
            analyzer = ClimateAnalyzer(location, lat, lon)
            risk_data = analyzer.get_overall_risk()
            
            overall_score = risk_data['overall_score']
            highest_risk = risk_data['highest_risk']
            
            # Show banner only if risk is HIGH or CRITICAL
            if overall_score >= 60:
                if overall_score >= 80:
                    bg_color = "#FFEBEE"
                    border_color = "#D32F2F"
                    emoji = "🔴"
                    level = "CRITICAL"
                else:
                    bg_color = "#FFF3E0"
                    border_color = "#F57C00"
                    emoji = "🟠"
                    level = "HIGH"
                
                st.markdown(f"""
                <div style='background: {bg_color}; padding: 15px; border-radius: 10px; 
                            border-left: 5px solid {border_color}; margin: 20px 0;'>
                    <h4 style='color: {border_color}; margin: 0 0 10px 0;'>
                        {emoji} CLIMATE ALERT - {level} RISK
                    </h4>
                    <p style='margin: 0; color: #333; font-size: 15px;'>
                        <strong>{highest_risk['type']} Risk: {highest_risk['score']}/100</strong>
                    </p>
                    <p style='margin: 5px 0 0 0; color: #666; font-size: 14px;'>
                        Immediate action recommended to protect your crops.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns([3, 2])
                with col1:
                    if st.button("📊 View Full Climate Analysis", type="primary", use_container_width=True):
                        st.session_state.selected_menu = "🌡️ Climate Risk Dashboard"
                        st.rerun()
                with col2:
                    if st.button("🌾 Get Climate-Smart Crops", use_container_width=True):
                        st.session_state.selected_menu = "🌾 Climate-Smart Crops"
                        st.rerun()
                
                st.divider()
        except Exception as e:
            print(f"Climate alert error: {e}")
            # Silently fail - don't disrupt user experience
    
    # AI FEATURE HERO SECTION - Farm + Tech Hybrid
    import streamlit.components.v1 as components
    
    # Hero section with visual design
    st.markdown("""
    <style>
    .ai-hero-section {
        background: linear-gradient(135deg, #2E8B57 0%, #3CB371 100%);
        padding: 30px 20px 20px 20px;
        border-radius: 15px;
        margin: 20px 0;
        text-align: center;
    }
    
    .hero-heading {
        color: white;
        font-size: 28px;
        font-weight: 600;
        margin: 0 0 10px 0;
    }
    
    .hero-subheading {
        color: rgba(255, 255, 255, 0.9);
        font-size: 15px;
        margin: 0 0 20px 0;
    }
    
    .chat-input-box {
        max-width: 600px;
        margin: -10px auto 0 auto;
        padding: 15px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    @media (max-width: 768px) {
        .hero-heading { font-size: 22px; }
        .hero-subheading { font-size: 14px; }
    }
    </style>
    
    <div class="ai-hero-section">
        <h1 class="hero-heading">🌾 Smart Farming Assistant</h1>
        <p class="hero-subheading">
            Get instant help with crops, weather, and farming decisions
        </p>
        <div class="chat-input-box">
    """, unsafe_allow_html=True)
    
    # Initialize chat
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    
    # API setup
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    
    if api_key:
        from google import genai
        from streamlit_mic_recorder import mic_recorder
        
        client = genai.Client(api_key=api_key)
        farmer_name = st.session_state.get("farmer_name", "Farmer")
        farmer_profile = st.session_state.get("farmer_profile", {})
        location = farmer_profile.get('location', 'India')
        
        # All in one row: Text input + Mic + Language + Send
        col_text, col_mic, col_lang = st.columns([6, 1, 1])
        
        with col_text:
            user_input = st.text_input("", 
                                       placeholder="💬 Ask about your crops...", 
                                       key="hero_input",
                                       label_visibility="collapsed")
        
        with col_mic:
            audio = mic_recorder(
                start_prompt="🎤",
                stop_prompt="⏹️",
                just_once=False,
                use_container_width=True,
                key="hero_mic"
            )
        
        with col_lang:
            lang = st.selectbox("Language", ["en", "hi", "mr"],
                              format_func=lambda x: {"en":"🇬🇧","hi":"🇮🇳","mr":"🇮🇳"}[x],
                              key="hero_lang", 
                              label_visibility="collapsed")
        
        # Process voice if recorded
        if audio:
            with st.spinner("🔄 Processing voice..."):
                try:
                    audio_file = client.files.upload(path_or_bytes=audio['bytes'], mime_type="audio/wav")
                    response = client.models.generate_content(
                        model="gemini-2.0-flash-exp",
                        contents=[f"Transcribe this {lang} audio accurately:", audio_file]
                    )
                    if response and response.text:
                        transcribed = response.text.strip()
                        st.success(f"📝 You said: **{transcribed}**")
                        
                        # Add to chat
                        st.session_state.chat_messages.append({"role": "user", "content": transcribed})
                        
                        # Get AI response
                        with st.spinner("🤖 Getting answer..."):
                            system_prompt = f"You are a farming advisor. Farmer: {farmer_name}, Location: {location}. Reply in {lang} language. Be concise (3-5 sentences)."
                            messages = [system_prompt] + [f"{m['role']}: {m['content']}" for m in st.session_state.chat_messages]
                            
                            ai_response = client.models.generate_content(
                                model="gemini-2.0-flash-exp",
                                contents="\n".join(messages)
                            )
                            
                            if ai_response and ai_response.text:
                                st.session_state.chat_messages.append({"role": "assistant", "content": ai_response.text})
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Voice error: {str(e)}")
        
        # Process text input
        if user_input:
            st.session_state.chat_messages.append({"role": "user", "content": user_input})
            
            with st.spinner("🤖 AI is thinking..."):
                try:
                    system_prompt = f"You are a helpful farming advisor. Farmer: {farmer_name}, Location: {location}. Be concise (3-5 sentences)."
                    messages = [system_prompt] + [f"{m['role']}: {m['content']}" for m in st.session_state.chat_messages]
                    
                    response = client.models.generate_content(
                        model="gemini-2.0-flash-exp",
                        contents="\n".join(messages)
                    )
                    
                    if response and response.text:
                        st.session_state.chat_messages.append({"role": "assistant", "content": response.text})
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        # Clear button
        if st.session_state.chat_messages:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.chat_messages = []
                st.rerun()
    else:
        st.warning("⚠️ AI not configured")
    
    st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Display chat history below hero
    if st.session_state.get('chat_messages'):
        st.markdown("### 💬 Conversation")
        for msg in st.session_state.chat_messages[-6:]:
            if msg["role"] == "user":
                st.markdown(f"""
                <div style='background: #E3F2FD; padding: 12px; border-radius: 8px; margin: 8px 0; border-left: 3px solid #2196F3;'>
                    <strong>🧑‍🌾 You:</strong> {msg['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='background: #E8F5E9; padding: 12px; border-radius: 8px; margin: 8px 0; border-left: 3px solid #4CAF50;'>
                    <strong>🤖 Advisor:</strong> {msg['content']}
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)
    
    # Quick Stats Section (NEW)
    st.markdown(f"""
    <div style='margin: 20px 0 16px 0;'>
        <h2 style='color: #2E8B57; font-size: 20px; font-weight: 600; margin: 0;'>
            📊 {t('Quick Overview')}
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Get quick stats data
    try:
        today = datetime.now().date()
        events = get_events_for_date(farmer_name, today)
        tasks_count = len(events) if events else 0
    except:
        tasks_count = 0
    
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
    
    # Quick stats in one row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style='background: #E3F2FD; padding: 12px; border-radius: 8px; text-align: center; border-left: 3px solid #2196F3;'>
            <div style='font-size: 24px; font-weight: bold; color: #1976D2;'>{tasks_count}</div>
            <div style='font-size: 13px; color: #666;'>📅 {t('Tasks Today')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style='background: #E8F5E9; padding: 12px; border-radius: 8px; text-align: center; border-left: 3px solid #4CAF50;'>
            <div style='font-size: 24px; font-weight: bold; color: #388E3C;'>{my_tools + my_crops}</div>
            <div style='font-size: 13px; color: #666;'>📦 {t('My Listings')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style='background: #FFF3E0; padding: 12px; border-radius: 8px; text-align: center; border-left: 3px solid #FF9800;'>
            <div style='font-size: 24px; font-weight: bold; color: #F57C00;'>🌤️</div>
            <div style='font-size: 13px; color: #666;'>{t('Check Weather')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin: 24px 0;'></div>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style='margin: 24px 0 16px 0;'>
        <h2 style='color: #2E8B57; font-size: 20px; font-weight: 600; margin: 0;'>
            🎯 {t('Quick Actions')}
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
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
            
            
            st.session_state.selected_menu = "💰 My Money Diary"
            st.rerun()
    
    with col2:
        st.markdown(f"""
        <div class='action-card'>
            <span class='action-icon'>📅</span>
            <div class='action-title'>{t('My Calendar')}</div>
            <div class='action-desc'>{t('View farm schedule')}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Calendar", key="calendar_btn_home", use_container_width=True):
            
            
            st.session_state.selected_menu = "📅 My Calendar"
            st.rerun()
    
    st.markdown("<div style='margin: 24px 0;'><hr style='border: none; border-top: 2px solid #e0e0e0;'></div>", unsafe_allow_html=True)
    
    # Today's Tasks - Compact version
    st.markdown(f"""
    <div style='margin: 0 0 12px 0;'>
        <h2 style='color: #2E8B57; font-size: 20px; font-weight: 600; margin: 0;'>
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
                <div style='background: white; padding: 10px 14px; border-radius: 6px; margin: 6px 0; 
                            border-left: 3px solid #4CAF50; box-shadow: 0 1px 3px rgba(0,0,0,0.05);'>
                    {icon} <strong style='color: #2E8B57; font-size: 14px;'>{event_time}</strong> - <span style='font-size: 14px;'>{event_title}</span>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<div style='margin: 10px 0;'></div>", unsafe_allow_html=True)
            if st.button(f"📅 {t('View All Tasks')}", key="view_all_tasks", use_container_width=True):
                st.session_state.selected_menu = "📅 My Calendar"
                st.rerun()
        else:
            st.markdown(f"""
            <div style='background: #E8F5E9; padding: 16px; border-radius: 8px; text-align: center; border: 1px solid #81C784;'>
                <div style='font-size: 32px; margin-bottom: 6px;'>✅</div>
                <p style='color: #2E7D32; font-weight: 500; font-size: 14px; margin: 0;'>
                    {t('No tasks scheduled for today. You are all set!')}
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<div style='margin: 10px 0;'></div>", unsafe_allow_html=True)
            if st.button(f"📅 {t('Visit Calendar to plan your day')}", key="add_task_home", use_container_width=True, type="primary"):
                st.session_state.selected_menu = "📅 My Calendar"
                st.rerun()
    except Exception as e:
        st.info(f"📅 {t('Visit Calendar to plan your day')}")
        st.markdown("<div style='margin: 10px 0;'></div>", unsafe_allow_html=True)
        if st.button(f"📅 {t('Open Calendar')}", key="calendar_error", use_container_width=True, type="primary"):
            st.session_state.selected_menu = "📅 My Calendar"
            st.rerun()
    
    st.markdown("<div style='margin: 24px 0;'><hr style='border: none; border-top: 2px solid #e0e0e0;'></div>", unsafe_allow_html=True)
    
    # My Listings - Simplified to single summary card
    st.markdown(f"""
    <div style='margin: 0 0 12px 0;'>
        <h2 style='color: #2E8B57; font-size: 20px; font-weight: 600; margin: 0;'>
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
        # Single summary card
        st.markdown(f"""
        <div style='background: white; padding: 16px; border-radius: 8px; border: 1px solid #ddd; text-align: center;'>
            <div style='font-size: 32px; margin-bottom: 8px;'>📦</div>
            <div style='font-size: 18px; font-weight: 600; color: #2E8B57; margin-bottom: 4px;'>
                {t('You have')} {my_tools} {t('tools')} & {my_crops} {t('crops')}
            </div>
            <div style='font-size: 13px; color: #666;'>{t('Total')}: {total_listings} {t('listings')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='margin: 10px 0;'></div>", unsafe_allow_html=True)
        if st.button(f"👁️ {t('View My Listings')}", key="view_listings_btn", use_container_width=True):
            st.session_state.selected_menu = "📦 My Listings"
            st.rerun()
    else:
        st.markdown(f"""
        <div style='background: #FFF3E0; padding: 20px; border-radius: 8px; text-align: center; border: 1px solid #FFB74D;'>
            <div style='font-size: 40px; margin-bottom: 10px;'>📝</div>
            <p style='color: #E65100; font-weight: 500; font-size: 15px; margin: 0 0 6px 0;'>
                {t('You have not listed anything yet.')}
            </p>
            <p style='color: #F57C00; font-size: 13px; margin: 0;'>
                {t('Start selling or renting now!')}
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='margin: 10px 0;'></div>", unsafe_allow_html=True)
        if st.button(f"➕ {t('Create First Listing')}", key="first_listing_btn", use_container_width=True, type="primary"):
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


