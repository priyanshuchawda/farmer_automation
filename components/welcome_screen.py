# components/welcome_screen.py
"""
Welcome screen for first-time users after registration/login
Part of Phase 1: Authentication Overhaul
"""

import streamlit as st

def render_welcome_screen():
    """Render welcome screen for first-time users"""
    
    # Add sidebar info on welcome screen
    farmer_name = st.session_state.get('farmer_name', 'Farmer')
    with st.sidebar:
        st.success(f"✅ Logged in as **{farmer_name}**")
        st.markdown("---")
        st.info("**🎉 First Time Here?**\n\nWelcome to your farming dashboard! Take a moment to explore the features.")
        
        if st.button("⏭️ Skip Welcome", use_container_width=True):
            st.session_state.show_welcome = False
            st.rerun()
    
    st.markdown("""
    <style>
    .welcome-container {
        background: linear-gradient(135deg, #2E8B57 0%, #3CB371 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 10px 40px rgba(46, 139, 87, 0.3);
    }
    
    .welcome-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .welcome-subtitle {
        font-size: 1.5rem;
        opacity: 0.95;
        margin-bottom: 2rem;
    }
    
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        text-align: center;
        height: 100%;
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.15);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .feature-title {
        color: #2E8B57;
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .feature-description {
        color: #666;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    .getting-started {
        background: #E8F5E9;
        padding: 2rem;
        border-radius: 15px;
        border-left: 5px solid #2E8B57;
        margin: 2rem 0;
    }
    
    .step-item {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 3px 10px rgba(0,0,0,0.05);
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .step-number {
        background: #2E8B57;
        color: white;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 1.2rem;
        flex-shrink: 0;
    }
    
    .step-content {
        flex: 1;
        text-align: left;
    }
    
    .step-title {
        color: #2E8B57;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }
    
    .step-desc {
        color: #666;
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main welcome banner
    farmer_name = st.session_state.get('farmer_name', 'Farmer')
    
    st.title(f"🎉 Welcome, {farmer_name}!")
    st.subheader(f"{t('You are now part of the')} {t('Smart Farmer Marketplace')} {t('family')}")
    st.markdown("---")
    
    st.markdown("### 🌟 What You Can Do Here")
    
    # Feature cards using native Streamlit
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📝 List & Trade")
        st.write("List your tools for rent and crops for sale. Connect with other farmers in your area.")
    
    with col2:
        st.markdown("#### 🌤️ Weather Forecasts")
        st.write("Get accurate 7-day weather predictions tailored to your farm location.")
    
    with col3:
        st.markdown("#### 📅 Smart Calendar")
        st.write("Plan farming activities with AI assistance and weather-integrated alerts.")
    
    st.markdown("")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 💰 Market Prices")
        st.write("Check current market prices for crops and make informed selling decisions.")
    
    with col2:
        st.markdown("#### 🤖 AI Assistance")
        st.write("Get AI-powered farming plans and personalized recommendations.")
    
    with col3:
        st.markdown("#### 🤝 Community")
        st.write("Connect with fellow farmers and build a supportive network.")
    
    # Getting started section
    st.markdown("---")
    st.markdown("### 🎯 Get Started in 4 Easy Steps")
    
    step_col1, step_col2 = st.columns([1, 10])
    with step_col1:
        st.success("**1️⃣**")
    with step_col2:
        st.markdown("**Complete Your Profile**")
        st.caption("Go to 'View Profile' to review and update your information")
    
    step_col1, step_col2 = st.columns([1, 10])
    with step_col1:
        st.info("**2️⃣**")
    with step_col2:
        st.markdown("**Check Today's Weather**")
        st.caption("Visit 'Weather' to see forecasts for your farm location")
    
    step_col1, step_col2 = st.columns([1, 10])
    with step_col1:
        st.warning("**3️⃣**")
    with step_col2:
        st.markdown("**Create Your First Listing**")
        st.caption("Go to 'New Listing' to list a tool or crop")
    
    step_col1, step_col2 = st.columns([1, 10])
    with step_col1:
        st.error("**4️⃣**")
    with step_col2:
        st.markdown("**Plan Your Week**")
        st.caption("Use 'Calendar' to schedule farming activities with AI help")
    
    # Action buttons
    st.markdown("### 🚀 Ready to Begin?")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("👤 View Profile", use_container_width=True, type="primary"):
            st.session_state.show_welcome = False
            st.session_state.menu_selection = "View Profile"
            st.rerun()
    
    with col2:
        if st.button("🌤️ Check Weather", use_container_width=True, type="primary"):
            st.session_state.show_welcome = False
            st.session_state.menu_selection = "Weather"
            st.rerun()
    
    with col3:
        if st.button("📝 Create Listing", use_container_width=True, type="primary"):
            st.session_state.show_welcome = False
            st.session_state.menu_selection = "New Listing"
            st.rerun()
    
    with col4:
        if st.button("📅 Open Calendar", use_container_width=True, type="primary"):
            st.session_state.show_welcome = False
            st.session_state.menu_selection = "Calendar"
            st.rerun()
    
    st.markdown("")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("⏭️ Skip Tutorial - Go to Dashboard", use_container_width=True):
            st.session_state.show_welcome = False
            st.rerun()
    
    # Tip box at the bottom
    st.markdown("---")
    st.info("💡 **Pro Tip:** You can always access these features from the menu on the left sidebar!")


