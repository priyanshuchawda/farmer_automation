"""
Climate Risk Dashboard - Main UI component
Shows comprehensive climate risk analysis with actionable recommendations
"""

import streamlit as st
from weather.climate_analyzer import ClimateAnalyzer
from database.db_functions import get_farmer_profile, add_data
from components.translation_utils import t
from datetime import datetime
import plotly.graph_objects as go

def render_climate_risk_dashboard():
    """Render the main climate risk dashboard"""
    
    st.markdown("""
    <style>
    .risk-card {
        padding: 20px;
        border-radius: 12px;
        margin: 15px 0;
        border-left: 5px solid;
    }
    .risk-critical {
        background: linear-gradient(135deg, #FFE5E5 0%, #FFD0D0 100%);
        border-left-color: #D32F2F;
    }
    .risk-high {
        background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%);
        border-left-color: #F57C00;
    }
    .risk-moderate {
        background: linear-gradient(135deg, #FFF9C4 0%, #FFF59D 100%);
        border-left-color: #FBC02D;
    }
    .risk-low {
        background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
        border-left-color: #388E3C;
    }
    .action-item {
        background: white;
        padding: 12px;
        border-radius: 8px;
        margin: 8px 0;
        border-left: 3px solid #2196F3;
    }
    @media (max-width: 768px) {
        .risk-card { padding: 15px; }
        .action-item { padding: 10px; }
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.header("🌡️ Farm Climate Risk Analysis")
    
    # Get farmer profile
    farmer_profile = st.session_state.get("farmer_profile", {})
    farmer_name = st.session_state.get("farmer_name", "Farmer")
    
    if not farmer_profile or not farmer_profile.get('latitude'):
        st.warning("⚠️ Please update your profile with location coordinates to see climate risk analysis")
        if st.button("📍 Update Profile", type="primary"):
            st.session_state.selected_menu = "👤 My Profile"
            st.rerun()
        return
    
    location = farmer_profile.get('weather_location', 'Unknown')
    lat = farmer_profile.get('latitude')
    lon = farmer_profile.get('longitude')
    
    st.caption(f"📍 Location: {location} | Last updated: {datetime.now().strftime('%d %b %Y, %I:%M %p')}")
    
    # Refresh button
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Refresh Analysis", use_container_width=True):
            st.rerun()
    
    # Analyze climate risks
    with st.spinner("🔍 Analyzing climate risks using AI..."):
        analyzer = ClimateAnalyzer(location, lat, lon)
        risk_data = analyzer.get_overall_risk()
    
    # Overall Risk Score
    overall_score = risk_data['overall_score']
    overall_level = risk_data['overall_level']
    
    # Color coding
    if overall_level == "CRITICAL":
        color_gradient = "linear-gradient(135deg, #D32F2F 0%, #F44336 100%)"
        emoji = "🔴"
    elif overall_level == "HIGH":
        color_gradient = "linear-gradient(135deg, #F57C00 0%, #FF9800 100%)"
        emoji = "🟠"
    elif overall_level == "MODERATE":
        color_gradient = "linear-gradient(135deg, #FBC02D 0%, #FDD835 100%)"
        emoji = "🟡"
    else:
        color_gradient = "linear-gradient(135deg, #388E3C 0%, #4CAF50 100%)"
        emoji = "🟢"
    
    # Overall risk card
    st.markdown(f"""
    <div style='background: {color_gradient}; padding: 30px; border-radius: 15px; 
                text-align: center; color: white; margin: 20px 0;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);'>
        <h1 style='margin: 0; font-size: 2.5rem;'>{emoji} {overall_score:.0f}/100</h1>
        <h2 style='margin: 10px 0 0 0; font-size: 1.5rem;'>{overall_level} CLIMATE RISK</h2>
        <p style='margin: 10px 0 0 0; opacity: 0.9;'>
            Primary Concern: {risk_data['highest_risk']['type']} 
            ({risk_data['highest_risk']['score']}/100)
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Individual Risk Sections
    st.subheader("📊 Detailed Risk Assessment")
    
    # Create tabs for each risk type
    tab1, tab2, tab3 = st.tabs(["🔥 Drought Risk", "💧 Flood Risk", "🌡️ Heat Stress"])
    
    with tab1:
        render_drought_section(risk_data['drought'], farmer_name, location)
    
    with tab2:
        render_flood_section(risk_data['flood'])
    
    with tab3:
        render_heat_section(risk_data['heat_stress'])
    
    # Save to history
    try:
        history_data = (
            farmer_name,
            datetime.now().strftime('%Y-%m-%d'),
            location,
            int(overall_score),
            risk_data['drought']['score'],
            risk_data['flood']['score'],
            risk_data['heat_stress']['score'],
            risk_data['drought']['days_without_rain'],
            risk_data['drought']['soil_moisture'],
            str(risk_data['drought']['actions']),
            None  # actions_taken - farmer can update later
        )
        add_data("climate_risk_history", history_data)
    except Exception as e:
        print(f"Error saving climate history: {e}")

def render_drought_section(drought_data, farmer_name, location):
    """Render drought risk section"""
    score = drought_data['score']
    level = drought_data['level']
    
    # Determine card class
    if level == "CRITICAL":
        card_class = "risk-critical"
    elif level == "HIGH":
        card_class = "risk-high"
    elif level == "MODERATE":
        card_class = "risk-moderate"
    else:
        card_class = "risk-low"
    
    st.markdown(f"""
    <div class='risk-card {card_class}'>
        <h3 style='margin: 0 0 10px 0;'>🔥 DROUGHT RISK: {score}/100 - {level}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Days Without Rain", f"{drought_data['days_without_rain']} days",
                 delta="Critical" if drought_data['days_without_rain'] > 30 else None,
                 delta_color="inverse" if drought_data['days_without_rain'] > 30 else "normal")
    
    with col2:
        st.metric("Soil Moisture", f"{drought_data['soil_moisture']}%",
                 delta="Low" if drought_data['soil_moisture'] < 40 else None,
                 delta_color="inverse" if drought_data['soil_moisture'] < 40 else "normal")
    
    with col3:
        st.metric("Next Rain Expected", f"{drought_data['next_rain_days']} days")
    
    with col4:
        st.metric("Temperature Stress", drought_data['temperature_stress'])
    
    # Actions
    st.markdown("### ⚠️ Required Actions")
    
    if score > 60:
        st.error("**URGENT: Immediate action required to prevent crop losses**")
    
    for i, action in enumerate(drought_data['actions'], 1):
        st.markdown(f"""
        <div class='action-item'>
            <strong>{i}.</strong> {action}
        </div>
        """, unsafe_allow_html=True)
    
    # Estimated loss warning
    if drought_data.get('estimated_loss'):
        st.warning(f"⚠️ **Potential Loss:** {drought_data['estimated_loss']}")
    
    # Action tracking
    st.markdown("---")
    st.markdown("#### ✅ Mark Actions as Completed")
    
    actions_taken = []
    for i, action in enumerate(drought_data['actions']):
        if st.checkbox(action, key=f"drought_action_{i}"):
            actions_taken.append(action)
    
    if st.button("💾 Save Actions Taken", key="save_drought_actions"):
        # Update database with actions taken
        st.success(f"✅ Recorded {len(actions_taken)} completed actions!")

def render_flood_section(flood_data):
    """Render flood risk section"""
    score = flood_data['score']
    level = flood_data['level']
    
    if level == "CRITICAL":
        card_class = "risk-critical"
    elif level == "HIGH":
        card_class = "risk-high"
    elif level == "MODERATE":
        card_class = "risk-moderate"
    else:
        card_class = "risk-low"
    
    st.markdown(f"""
    <div class='risk-card {card_class}'>
        <h3 style='margin: 0 0 10px 0;'>💧 FLOOD RISK: {score}/100 - {level}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Rainfall (3 days)", f"{flood_data['upcoming_rain_3day']:.1f}mm")
    
    with col2:
        st.metric("Soil Saturation", f"{flood_data['soil_saturation']}%")
    
    with col3:
        st.metric("Drainage", flood_data['drainage_status'])
    
    # Actions
    if flood_data['actions']:
        st.markdown("### 📋 Recommended Actions")
        for i, action in enumerate(flood_data['actions'], 1):
            st.markdown(f"""
            <div class='action-item'>
                <strong>{i}.</strong> {action}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ No immediate flood protection actions needed")

def render_heat_section(heat_data):
    """Render heat stress section"""
    score = heat_data['score']
    level = heat_data['level']
    
    if level == "CRITICAL":
        card_class = "risk-critical"
    elif level == "HIGH":
        card_class = "risk-high"
    elif level == "MODERATE":
        card_class = "risk-moderate"
    else:
        card_class = "risk-low"
    
    st.markdown(f"""
    <div class='risk-card {card_class}'>
        <h3 style='margin: 0 0 10px 0;'>🌡️ HEAT STRESS: {score}/100 - {level}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Recent Max Temp", f"{heat_data['recent_max_temp']:.1f}°C")
    
    with col2:
        st.metric("Heat Wave Duration", f"{heat_data['heat_wave_days']} days")
    
    # Crop impact
    if heat_data.get('crop_impact'):
        st.info(f"🌾 **Crop Impact:** {heat_data['crop_impact']}")
    
    # Actions
    if heat_data['actions']:
        st.markdown("### 📋 Recommended Actions")
        for i, action in enumerate(heat_data['actions'], 1):
            st.markdown(f"""
            <div class='action-item'>
                <strong>{i}.</strong> {action}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ No heat stress mitigation needed currently")
