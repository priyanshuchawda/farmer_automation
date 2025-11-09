"""Enhanced calendar with weather integration"""

import streamlit as st
from datetime import datetime, timedelta
from database.db_functions import get_farmer_profile, add_data, get_farmer_events, delete_event, update_event
from weather.weather_assistant import get_weather_forecast_for_query
from weather.combined_forecast import get_weather_forecast
from calender.ai_service import AIService
from calender.config import TRANSLATIONS as CAL_TRANSLATIONS
from calender.calendar_component import render_calendar
from calender.day_view import render_day_view
from calender.week_view import render_week_view

def get_weather_for_event(farmer_profile, event_date):
    """Get weather forecast for a specific date and farmer location"""
    if not farmer_profile or 'weather_location' not in farmer_profile:
        return None
    
    location = farmer_profile['weather_location']
    lat = farmer_profile.get('latitude')
    lon = farmer_profile.get('longitude')
    
    try:
        # Get forecast for the location
        forecast = get_weather_forecast(location, lat=lat, lon=lon)
        
        if forecast:
            # Find forecast for the specific date
            event_date_obj = datetime.strptime(event_date, '%Y-%m-%d').date()
            
            for day in forecast:
                if isinstance(day['date'], str):
                    forecast_date = datetime.strptime(day['date'], '%Y-%m-%d').date()
                elif isinstance(day['date'], datetime):
                    forecast_date = day['date'].date()
                else:
                    forecast_date = day['date']
                
                if forecast_date == event_date_obj:
                    return {
                        'temperature': day.get('temperature'),
                        'rainfall': day.get('rainfall'),
                        'wind_speed': day.get('wind_speed')
                    }
    except Exception as e:
        print(f"Error getting weather for event: {e}")
    
    return None

def create_weather_alert(weather_data):
    """Create weather alert message based on weather conditions"""
    if not weather_data:
        return ""
    
    temp = weather_data.get('temperature', 0)
    rain = weather_data.get('rainfall', 0)
    wind = weather_data.get('wind_speed', 0)
    
    alerts = []
    
    if rain > 10:
        alerts.append("⚠️ Heavy rain expected - postpone outdoor activities")
    elif rain > 2:
        alerts.append("🌧️ Light rain expected - plan accordingly")
    
    if temp > 35:
        alerts.append("🔥 Very hot - ensure proper irrigation")
    elif temp < 15:
        alerts.append("❄️ Cold weather - protect sensitive crops")
    
    if wind > 25:
        alerts.append("💨 Strong winds - secure equipment and structures")
    
    if not alerts:
        if temp >= 20 and temp <= 30 and rain == 0:
            return "✅ Good weather for farming activities"
        else:
            return f"☀️ Weather: {temp}°C, {rain}mm rain, {wind} km/h wind"
    
    return " | ".join(alerts)

def render_integrated_calendar(farmer_name):
    """Render calendar with weather integration for logged-in farmer"""
    
    # Get farmer profile
    farmer_profile = get_farmer_profile(farmer_name)
    
    if not farmer_profile:
        st.warning("⚠️ Please create your farmer profile first to use weather-integrated calendar.")
        return
    
    # Display farmer info and weather location
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"### 👨‍🌾 {farmer_name}'s Farming Calendar")
        st.caption(f"📍 Farm: {farmer_profile.get('location', 'N/A')} | 🌍 Weather: {farmer_profile.get('weather_location', 'N/A')}")
    
    with col2:
        if st.button("➕ Quick Add Task", use_container_width=True, type="primary"):
            st.session_state.show_quick_add = True
    
    with col3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    # Quick Add Task Form
    if st.session_state.get('show_quick_add', False):
        with st.form("quick_add_form"):
            st.subheader("➕ Add Farming Task")
            
            col1, col2 = st.columns(2)
            with col1:
                task_date = st.date_input("📅 Date", value=datetime.now().date())
            with col2:
                task_time = st.time_input("🕐 Time", value=datetime.strptime("09:00", '%H:%M').time())
            
            # Common farming tasks dropdown
            common_tasks = [
                "Custom Task",
                "🌱 Planting",
                "💧 Irrigation",
                "🌾 Harvesting",
                "🧪 Fertilizer Application",
                "🐛 Pest Control",
                "🚜 Plowing",
                "🌿 Weeding",
                "✂️ Pruning",
                "🔍 Crop Inspection",
                "📦 Market Delivery",
                "🌾 Seed Purchase",
                "🧰 Equipment Maintenance"
            ]
            
            task_type = st.selectbox("Task Type", common_tasks)
            
            if task_type == "Custom Task":
                task_title = st.text_input("Task Title *")
            else:
                task_title = st.text_input("Task Title *", value=task_type)
            
            task_description = st.text_area(
                "Description", 
                placeholder="Add details about this task...",
                height=100
            )
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("✅ Add Task", use_container_width=True, type="primary")
            with col2:
                cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
            
            if submit and task_title:
                # Get weather for this date
                event_date_str = task_date.strftime('%Y-%m-%d')
                weather_data = get_weather_for_event(farmer_profile, event_date_str)
                weather_alert = create_weather_alert(weather_data)
                
                # Save to database
                event_data = (
                    farmer_name,
                    event_date_str,
                    task_time.strftime('%H:%M'),
                    task_title,
                    task_description,
                    weather_alert,
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )
                add_data("calendar_events", event_data)
                st.success(f"✅ Task '{task_title}' added successfully!")
                st.session_state.show_quick_add = False
                st.rerun()
            
            if cancel:
                st.session_state.show_quick_add = False
                st.rerun()
    
    st.divider()
    
    # Initialize session state
    if "current_month" not in st.session_state:
        st.session_state.current_month = datetime.now().month
    if "current_year" not in st.session_state:
        st.session_state.current_year = datetime.now().year
    if "current_day" not in st.session_state:
        st.session_state.current_day = datetime.now().day
    if "calendar_view" not in st.session_state:
        st.session_state.calendar_view = "month"
    
    # AI-Powered Plan Generation
    ai_service = AIService()
    lang = "en"
    
    st.markdown("---")
    st.subheader("🤖 AI Farming Plan Generator")
    st.write("Ask AI to create a farming schedule for you!")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        prompt = st.text_area(
            "Your farming question:",
            height=80,
            placeholder="E.g., Create a 10-day wheat planting schedule for November",
            key="ai_calendar_prompt"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🌱 Generate", use_container_width=True, type="primary"):
            if prompt.strip():
                with st.spinner("🔄 Creating plan..."):
                    plan_data, error = ai_service.generate_farming_plan(prompt, lang)
                    
                    if plan_data:
                        st.session_state.ai_plan = plan_data
                        st.success("✅ Plan ready!")
                        st.rerun()
                    else:
                        st.error(f"❌ {error}")
    
    # Display and save AI-generated plan with editable dates and times
    if 'ai_plan' in st.session_state:
        plan = st.session_state.ai_plan
        
        st.subheader(f"📋 {plan['heading']}")
        st.info("✏️ Edit dates and times before saving to calendar")
        
        # Initialize editable plan if not exists
        if 'editable_plan' not in st.session_state:
            base_date = datetime.now()
            st.session_state.editable_plan = []
            for idx, step in enumerate(plan['plan']):
                st.session_state.editable_plan.append({
                    'step_number': step['step_number'],
                    'title': step['title'],
                    'description': step['description'],
                    'date': base_date + timedelta(days=idx),
                    'time': '09:00'
                })
        
        # Display editable plan
        for idx, step in enumerate(st.session_state.editable_plan):
            with st.expander(f"**{step['step_number']}. {step['title']}**", expanded=True):
                st.write(step['description'])
                
                col1, col2 = st.columns(2)
                with col1:
                    new_date = st.date_input(
                        "📅 Date",
                        value=step['date'],
                        key=f"date_{idx}"
                    )
                    st.session_state.editable_plan[idx]['date'] = new_date
                
                with col2:
                    new_time = st.time_input(
                        "🕐 Time",
                        value=datetime.strptime(step['time'], '%H:%M').time(),
                        key=f"time_{idx}"
                    )
                    st.session_state.editable_plan[idx]['time'] = new_time.strftime('%H:%M')
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📅 Add All to Calendar with Weather Alerts", type="primary", use_container_width=True):
                added = 0
                
                for step in st.session_state.editable_plan:
                    event_date = step['date'].strftime('%Y-%m-%d')
                    event_time = step['time']
                    
                    # Get weather for this date
                    weather_data = get_weather_for_event(farmer_profile, event_date)
                    weather_alert = create_weather_alert(weather_data)
                    
                    # Save to database
                    event_data = (
                        farmer_name,
                        event_date,
                        event_time,
                        step['title'],
                        step['description'],
                        weather_alert,
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    )
                    add_data("calendar_events", event_data)
                    added += 1
                
                st.success(f"✅ Added {added} events with weather alerts!")
                del st.session_state.ai_plan
                del st.session_state.editable_plan
                st.rerun()
        
        with col2:
            if st.button("❌ Cancel", use_container_width=True):
                del st.session_state.ai_plan
                if 'editable_plan' in st.session_state:
                    del st.session_state.editable_plan
                st.rerun()
    
    st.divider()
    
    # Load farmer's events from database
    events_df = get_farmer_events(farmer_name)
    
    # Convert to calendar format
    calendar_events = []
    for _, row in events_df.iterrows():
        event_time = row.get('event_time', '09:00')
        if not event_time:
            event_time = '09:00'
        
        calendar_events.append({
            "id": row['id'],
            "start": f"{row['event_date']}T{event_time}:00",
            "extendedProps": {
                "heading": row['event_title'],
                "description": row['event_description'],
                "weather_alert": row.get('weather_alert', ''),
                "time": event_time
            }
        })
    
    # Task Statistics and Upcoming Tasks
    st.subheader("📊 Quick Overview")
    
    # Get upcoming tasks (next 7 days)
    today = datetime.now().date()
    upcoming_tasks = []
    overdue_tasks = []
    
    for _, row in events_df.iterrows():
        event_date = datetime.strptime(row['event_date'], '%Y-%m-%d').date()
        if event_date >= today and event_date <= today + timedelta(days=7):
            upcoming_tasks.append(row)
        elif event_date < today:
            overdue_tasks.append(row)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📅 Total Tasks", len(events_df))
    with col2:
        st.metric("⏰ Upcoming (7 days)", len(upcoming_tasks))
    with col3:
        st.metric("⚠️ Overdue", len(overdue_tasks))
    with col4:
        today_tasks = len([t for t in upcoming_tasks if datetime.strptime(t['event_date'], '%Y-%m-%d').date() == today])
        st.metric("📌 Today", today_tasks)
    
    # Show today's tasks if any
    if today_tasks > 0:
        st.info("**Today's Tasks:**")
        for task in [t for t in upcoming_tasks if datetime.strptime(t['event_date'], '%Y-%m-%d').date() == today]:
            task_time = task.get('event_time', '09:00')
            st.markdown(f"- 🕐 **{task_time}** - {task['event_title']}")
    
    st.divider()
    
    # Display current month weather summary
    st.subheader(f"🌤️ 7-Day Weather Outlook")
    
    try:
        forecast = get_weather_forecast(
            farmer_profile.get('weather_location'),
            lat=farmer_profile.get('latitude'),
            lon=farmer_profile.get('longitude')
        )
        
        if forecast:
            cols = st.columns(min(7, len(forecast)))
            for idx, day in enumerate(forecast[:7]):
                with cols[idx]:
                    date_str = day['date'] if isinstance(day['date'], str) else day['date'].strftime('%Y-%m-%d')
                    day_name = datetime.strptime(date_str, '%Y-%m-%d').strftime('%a')
                    
                    # Weather emoji
                    if day['rainfall'] > 10:
                        emoji = "⛈️"
                    elif day['rainfall'] > 2:
                        emoji = "🌧️"
                    elif day['temperature'] > 32:
                        emoji = "☀️"
                    else:
                        emoji = "⛅"
                    
                    st.markdown(f"**{day_name}** {emoji}")
                    st.metric(
                        date_str[-5:],
                        f"{day['temperature']:.0f}°C",
                        f"{day['rainfall']:.0f}mm"
                    )
    except Exception as e:
        st.warning(f"Unable to load weather summary: {str(e)}")
    
    st.divider()
    
    # View selector dropdown - positioned above navigation
    st.markdown("""
    <style>
    /* Style the selectbox to be green */
    div[data-baseweb="select"] > div {
        background-color: #4CAF50 !important;
        border: 2px solid #2E7D32 !important;
        border-radius: 8px !important;
    }
    
    div[data-baseweb="select"] > div:hover {
        background-color: #45a049 !important;
        border-color: #1B5E20 !important;
    }
    
    div[data-baseweb="select"] span {
        color: white !important;
        font-weight: bold !important;
    }
    
    div[data-baseweb="select"] svg {
        fill: white !important;
    }
    
    /* Style the dropdown options */
    [role="listbox"] {
        background-color: #E8F5E9 !important;
    }
    
    [role="option"] {
        color: #1B5E20 !important;
    }
    
    [role="option"]:hover {
        background-color: #C8E6C9 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Get current view
    current_view = st.session_state.get('calendar_view', 'month')
    
    # View options with icons
    view_options = {
        "📅 Month View": "month",
        "📆 Week View": "week",
        "📋 Day View": "day"
    }
    
    # Find current selection
    current_label = [k for k, v in view_options.items() if v == current_view][0]
    
    # Dropdown positioned above navigation
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col3:
        selected_view = st.selectbox(
            "Calendar View",
            options=list(view_options.keys()),
            index=list(view_options.keys()).index(current_label),
            key="view_selector",
            label_visibility="collapsed"
        )
        
        # Update view if changed
        new_view = view_options[selected_view]
        if new_view != current_view:
            st.session_state.calendar_view = new_view
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Render appropriate calendar view
    if st.session_state.calendar_view == "day":
        render_day_view(
            st.session_state.current_year,
            st.session_state.current_month,
            st.session_state.current_day,
            calendar_events,
            lang
        )
    elif st.session_state.calendar_view == "week":
        render_week_view(
            st.session_state.current_year,
            st.session_state.current_month,
            st.session_state.current_day,
            calendar_events,
            lang
        )
    else:  # month view
        render_calendar(
            st.session_state.current_year,
            st.session_state.current_month,
            calendar_events,
            lang
        )
    
    # Show selected event details with weather and edit functionality
    if st.session_state.get('selected_event'):
        event = st.session_state.selected_event
        
        st.divider()
        st.subheader("📝 Event Details")
        
        # Edit mode toggle
        if 'edit_mode' not in st.session_state:
            st.session_state.edit_mode = False
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"### {event['extendedProps']['heading']}")
        
        with col2:
            if not st.session_state.edit_mode:
                if st.button("✏️ Edit", use_container_width=True, type="primary"):
                    st.session_state.edit_mode = True
                    st.rerun()
        
        with col3:
            if st.button("🗑️ Delete", use_container_width=True, type="secondary"):
                delete_event(event['id'])
                st.session_state.selected_event = None
                st.success("✅ Event deleted!")
                st.rerun()
        
        st.divider()
        
        if st.session_state.edit_mode:
            # Edit mode
            col1, col2 = st.columns(2)
            
            with col1:
                event_date_str = event['start'].split('T')[0]
                event_date = datetime.strptime(event_date_str, '%Y-%m-%d').date()
                new_date = st.date_input("📅 Event Date", value=event_date, key="edit_date")
            
            with col2:
                event_time = event['extendedProps'].get('time', '09:00')
                time_obj = datetime.strptime(event_time, '%H:%M').time()
                new_time = st.time_input("🕐 Event Time", value=time_obj, key="edit_time")
            
            new_title = st.text_input("Title", value=event['extendedProps']['heading'], key="edit_title")
            new_description = st.text_area("Description", value=event['extendedProps'].get('description', ''), key="edit_desc", height=100)
            
            # Show current weather alert
            current_weather_alert = event['extendedProps'].get('weather_alert', '')
            if current_weather_alert:
                st.info(f"🌦️ Weather Alert: {current_weather_alert}")
            
            # Option to refresh weather
            if st.button("🔄 Refresh Weather Forecast", use_container_width=True):
                new_weather_data = get_weather_for_event(farmer_profile, new_date.strftime('%Y-%m-%d'))
                new_weather_alert = create_weather_alert(new_weather_data)
                st.session_state.temp_weather_alert = new_weather_alert
                st.rerun()
            
            weather_alert_to_save = st.session_state.get('temp_weather_alert', current_weather_alert)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Save Changes", use_container_width=True, type="primary"):
                    update_event(
                        event['id'],
                        new_date.strftime('%Y-%m-%d'),
                        new_time.strftime('%H:%M'),
                        new_title,
                        new_description,
                        weather_alert_to_save
                    )
                    st.session_state.edit_mode = False
                    st.session_state.selected_event = None
                    if 'temp_weather_alert' in st.session_state:
                        del st.session_state.temp_weather_alert
                    st.success("✅ Event updated!")
                    st.rerun()
            
            with col2:
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.edit_mode = False
                    if 'temp_weather_alert' in st.session_state:
                        del st.session_state.temp_weather_alert
                    st.rerun()
        else:
            # View mode
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(event['extendedProps'].get('description', 'No description'))
                
                if event['extendedProps'].get('weather_alert'):
                    st.info(f"🌦️ {event['extendedProps']['weather_alert']}")
            
            with col2:
                event_date = event['start'].split('T')[0]
                event_time = event['extendedProps'].get('time', '09:00')
                st.metric("📅 Date", event_date)
                st.metric("🕐 Time", event_time)


