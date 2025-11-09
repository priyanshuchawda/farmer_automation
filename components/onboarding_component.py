# components/onboarding_component.py
"""
Interactive Onboarding Checklist Component
Shows step-by-step first actions for new farmers
"""

import streamlit as st
from database.db_functions import get_onboarding_progress, update_onboarding_progress, get_farmer_profile

def calculate_onboarding_completion(progress):
    """Calculate onboarding completion percentage."""
    tasks = [
        progress.get('profile_completed', 0),
        progress.get('first_listing_created', 0),
        progress.get('calendar_event_added', 0),
        progress.get('weather_checked', 0),
        progress.get('market_prices_viewed', 0)
    ]
    completed = sum(tasks)
    total = len(tasks)
    percentage = int((completed / total) * 100)
    return percentage, completed, total

def render_onboarding_checklist(farmer_name):
    """Render the interactive onboarding checklist."""
    
    # Get progress
    progress = get_onboarding_progress(farmer_name)
    
    # Check if dismissed
    if progress.get('onboarding_dismissed', 0) == 1:
        return
    
    # Calculate completion
    percentage, completed, total = calculate_onboarding_completion(progress)
    
    # If 100% complete, show celebration and option to dismiss
    if percentage == 100:
        st.balloons()
        st.success("🎉 **Congratulations!** You've completed all starter tasks!")
        if st.button("✅ Dismiss Getting Started Guide", width="stretch"):
            update_onboarding_progress(farmer_name, onboarding_dismissed=1)
            st.rerun()
        return
    
    # Custom CSS for onboarding widget
    st.markdown("""
    <style>
    .onboarding-card {
        background: linear-gradient(135deg, #E8F5E9 0%, #F1F8E9 100%);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 6px 20px rgba(46, 139, 87, 0.15);
        margin-bottom: 25px;
        border: 2px solid #4CAF50;
    }
    .onboarding-progress {
        height: 30px;
        background: #E0E0E0;
        border-radius: 15px;
        overflow: hidden;
        margin: 15px 0;
    }
    .onboarding-fill {
        height: 100%;
        background: linear-gradient(90deg, #2E8B57, #4CAF50);
        transition: width 0.5s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 14px;
    }
    .task-item {
        background: white;
        padding: 15px;
        margin: 10px 0;
        border-radius: 10px;
        border-left: 4px solid;
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: all 0.3s ease;
    }
    .task-item:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transform: translateX(5px);
    }
    .task-complete {
        border-color: #4CAF50;
        background: #F1F8E9;
    }
    .task-incomplete {
        border-color: #FF9800;
        background: white;
    }
    .task-icon {
        font-size: 24px;
        margin-right: 15px;
    }
    .task-content {
        flex: 1;
    }
    .task-title {
        font-weight: 600;
        color: #333;
        margin-bottom: 3px;
    }
    .task-subtitle {
        font-size: 13px;
        color: #666;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Onboarding Card Header
    st.markdown(f"""
    <div class='onboarding-card'>
        <h3 style='color: #2E8B57; margin-bottom: 10px;'>🎯 GET STARTED WITH THESE STEPS</h3>
        <p style='color: #666; margin-bottom: 15px;'>Complete these tasks to unlock the full potential of your farming dashboard!</p>
        <div class='onboarding-progress'>
            <div class='onboarding-fill' style='width: {percentage}%;'>{completed} of {total} completed</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Task 1: Complete Profile
    task_class = "task-complete" if progress.get('profile_completed', 0) else "task-incomplete"
    task_icon = "✅" if progress.get('profile_completed', 0) else "1️⃣"
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"""
        <div class='task-item {task_class}'>
            <span class='task-icon'>{task_icon}</span>
            <div class='task-content'>
                <div class='task-title'>Complete Your Profile</div>
                <div class='task-subtitle'>Add your farm details and location for personalized features</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        if not progress.get('profile_completed', 0):
            if st.button("View Profile", key="onboard_profile", width="stretch"):
                st.session_state.selected_menu = "👤 My Profile"
                # Check if profile is complete
                farmer_profile = get_farmer_profile(farmer_name)
                if farmer_profile and farmer_profile.get('latitude') and farmer_profile.get('longitude'):
                    update_onboarding_progress(farmer_name, profile_completed=1)
                st.rerun()
    
    # Task 2: Check Weather
    task_class = "task-complete" if progress.get('weather_checked', 0) else "task-incomplete"
    task_icon = "✅" if progress.get('weather_checked', 0) else "2️⃣"
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"""
        <div class='task-item {task_class}'>
            <span class='task-icon'>{task_icon}</span>
            <div class='task-content'>
                <div class='task-title'>Check Today's Weather</div>
                <div class='task-subtitle'>Get real-time weather updates for your farm location</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        if not progress.get('weather_checked', 0):
            if st.button("View Weather", key="onboard_weather", width="stretch"):
                update_onboarding_progress(farmer_name, weather_checked=1)
                st.session_state.selected_menu = "🌤️ Weather Forecast"
                st.rerun()
    
    # Task 3: Create First Listing
    task_class = "task-complete" if progress.get('first_listing_created', 0) else "task-incomplete"
    task_icon = "✅" if progress.get('first_listing_created', 0) else "3️⃣"
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"""
        <div class='task-item {task_class}'>
            <span class='task-icon'>{task_icon}</span>
            <div class='task-content'>
                <div class='task-title'>Create Your First Listing</div>
                <div class='task-subtitle'>List a tool or crop to start trading with other farmers</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        if not progress.get('first_listing_created', 0):
            if st.button("Create Listing", key="onboard_listing", width="stretch"):
                st.session_state.selected_menu = "➕ Create New Listing"
                st.rerun()
    
    # Task 4: Plan Your Week
    task_class = "task-complete" if progress.get('calendar_event_added', 0) else "task-incomplete"
    task_icon = "✅" if progress.get('calendar_event_added', 0) else "4️⃣"
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"""
        <div class='task-item {task_class}'>
            <span class='task-icon'>{task_icon}</span>
            <div class='task-content'>
                <div class='task-title'>Plan Your Week</div>
                <div class='task-subtitle'>Add farming activities to your smart calendar</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        if not progress.get('calendar_event_added', 0):
            if st.button("Open Calendar", key="onboard_calendar", width="stretch"):
                st.session_state.selected_menu = "📅 Farming Calendar"
                st.rerun()
    
    # Task 5: Check Market Prices
    task_class = "task-complete" if progress.get('market_prices_viewed', 0) else "task-incomplete"
    task_icon = "✅" if progress.get('market_prices_viewed', 0) else "5️⃣"
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"""
        <div class='task-item {task_class}'>
            <span class='task-icon'>{task_icon}</span>
            <div class='task-content'>
                <div class='task-title'>Check Market Prices</div>
                <div class='task-subtitle'>View current market rates for crops in your area</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        if not progress.get('market_prices_viewed', 0):
            if st.button("View Prices", key="onboard_market", width="stretch"):
                update_onboarding_progress(farmer_name, market_prices_viewed=1)
                st.session_state.selected_menu = "💰 Market Prices"
                st.rerun()
    
    # Dismiss button
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("❌ I'll do this later", width="stretch"):
            update_onboarding_progress(farmer_name, onboarding_dismissed=1)
            st.rerun()

def check_and_update_listing_task(farmer_name):
    """Check if farmer has created their first listing and update progress."""
    from database.db_functions import get_data
    progress = get_onboarding_progress(farmer_name)
    
    if not progress.get('first_listing_created', 0):
        # Check if farmer has any listings
        tools = get_data("tools")
        crops = get_data("crops")
        
        has_tools = not tools.empty and farmer_name in tools['Farmer'].values
        has_crops = not crops.empty and farmer_name in crops['Farmer'].values
        
        if has_tools or has_crops:
            update_onboarding_progress(farmer_name, first_listing_created=1)
            return True
    return False

def check_and_update_calendar_task(farmer_name):
    """Check if farmer has added a calendar event and update progress."""
    try:
        from database.db_functions import get_farmer_events
        progress = get_onboarding_progress(farmer_name)
        
        if not progress.get('calendar_event_added', 0):
            # Check if farmer has any calendar events
            events = get_farmer_events(farmer_name)
            
            if not events.empty:
                update_onboarding_progress(farmer_name, calendar_event_added=1)
                return True
        return False
    except Exception as e:
        print(f"Error in check_and_update_calendar_task: {e}")
        # Don't block the app
        return False


