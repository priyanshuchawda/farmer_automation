"""
Climate-Smart Crop Selector
AI recommends crops based on current climate conditions
Uses Gemini 2.5 Flash with structured output
"""

import streamlit as st
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import os
from weather.climate_analyzer import ClimateAnalyzer
from database.db_functions import get_farmer_profile, add_data
from components.translation_utils import t

# Pydantic models for structured output
class CropRecommendation(BaseModel):
    """Single crop recommendation with details"""
    crop_name: str = Field(description="Name of the crop (English)")
    local_name: str = Field(description="Local name in Hindi/Marathi")
    drought_tolerance: int = Field(description="Drought tolerance score 0-10", ge=0, le=10)
    heat_tolerance: int = Field(description="Heat tolerance score 0-10", ge=0, le=10)
    water_requirement: str = Field(description="Water requirement: LOW, MEDIUM, or HIGH")
    expected_profit_per_acre: int = Field(description="Expected profit in rupees per acre")
    climate_risk_score: int = Field(description="Climate risk for this crop 0-100", ge=0, le=100)
    growing_season: str = Field(description="Suitable season: Kharif, Rabi, or Zaid")
    reasons: List[str] = Field(description="3-5 reasons why this crop is recommended")

class CropRecommendations(BaseModel):
    """Complete crop recommendations"""
    season: str = Field(description="Current/upcoming season")
    climate_summary: str = Field(description="Brief climate situation summary")
    recommended_crops: List[CropRecommendation] = Field(description="Top 3-5 recommended crops")
    avoid_crops: List[str] = Field(description="2-3 crops to avoid with reasons")

def render_climate_smart_crops():
    """Render climate-smart crop selector page"""
    
    st.markdown("""
    <style>
    .crop-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        margin: 15px 0;
        border-left: 5px solid #4CAF50;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .crop-card-avoid {
        border-left-color: #D32F2F;
        background: #FFEBEE;
    }
    .metric-badge {
        display: inline-block;
        background: #E8F5E9;
        padding: 5px 12px;
        border-radius: 20px;
        margin: 5px;
        font-size: 14px;
        color: #2E7D32;
    }
    .reason-item {
        padding: 8px;
        margin: 5px 0;
        background: #F5F5F5;
        border-radius: 6px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.header("🌾 Climate-Smart Crop Selector")
    st.caption("AI-powered crop recommendations based on real-time climate analysis")
    
    # Get farmer profile
    farmer_profile = st.session_state.get("farmer_profile", {})
    farmer_name = st.session_state.get("farmer_name", "Farmer")
    
    if not farmer_profile or not farmer_profile.get('latitude'):
        st.warning("⚠️ Please update your profile with location to get crop recommendations")
        if st.button("📍 Update Profile", type="primary"):
            st.session_state.selected_menu = "👤 My Profile"
            st.rerun()
        return
    
    location = farmer_profile.get('weather_location', 'Unknown')
    lat = farmer_profile.get('latitude')
    lon = farmer_profile.get('longitude')
    
    # Season selection
    st.subheader("📅 Select Season")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        season = st.selectbox(
            "Which season are you planning for?",
            ["Kharif (Monsoon: June-Oct)", "Rabi (Winter: Nov-Mar)", "Zaid (Summer: Mar-Jun)"],
            help="Select the season you want to plant crops for"
        )
        
        season_key = season.split(" ")[0]  # Extract Kharif/Rabi/Zaid
    
    with col2:
        st.metric("Your Location", location)
    
    # Analyze button
    if st.button("🤖 Get AI Crop Recommendations", type="primary", width="stretch"):
        with st.spinner("🔍 Analyzing climate conditions and recommending crops..."):
            
            # Get climate analysis
            analyzer = ClimateAnalyzer(location, lat, lon)
            risk_data = analyzer.get_overall_risk()
            
            # Get AI recommendations
            recommendations = get_crop_recommendations(
                location, 
                season_key, 
                risk_data,
                lat,
                lon
            )
            
            if recommendations:
                st.session_state.crop_recommendations = recommendations
                st.session_state.crop_season = season_key
                st.rerun()
    
    # Display recommendations if available
    if 'crop_recommendations' in st.session_state:
        display_recommendations(
            st.session_state.crop_recommendations,
            st.session_state.crop_season,
            farmer_name,
            location
        )

def get_crop_recommendations(location, season, risk_data, lat, lon):
    """Get AI-powered crop recommendations"""
    
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("⚠️ AI API key not configured")
        return None
    
    try:
        client = genai.Client(api_key=api_key)
        
        # Build comprehensive prompt
        drought_score = risk_data['drought']['score']
        flood_score = risk_data['flood']['score']
        heat_score = risk_data['heat_stress']['score']
        days_without_rain = risk_data['drought']['days_without_rain']
        
        prompt = f"""You are an expert agricultural advisor specializing in climate-smart crop selection for Indian farmers.

LOCATION: {location}, India
SEASON: {season}
TODAY: {datetime.now().strftime('%Y-%m-%d')}

CURRENT CLIMATE CONDITIONS:
- Drought Risk: {drought_score}/100 ({risk_data['drought']['level']})
- Flood Risk: {flood_score}/100 ({risk_data['flood']['level']})
- Heat Stress: {heat_score}/100 ({risk_data['heat_stress']['level']})
- Days Without Rain: {days_without_rain}

TASK: Recommend top 3-5 crops optimized for these climate conditions.

CROP SELECTION CRITERIA:
1. Climate Resilience - Choose crops that can handle current risks
2. Water Efficiency - Prefer low-water crops if drought risk is high
3. Profitability - Consider market prices and expected yields
4. Season Suitability - Match with {season} season requirements
5. Local Adaptability - Crops commonly grown in {location} region

SCORING GUIDELINES:
- Drought Tolerance: 10 = Survives 60+ days without rain, 5 = Needs regular water, 1 = Very sensitive
- Heat Tolerance: 10 = Thrives >38°C, 5 = Optimal 25-30°C, 1 = Sensitive to heat
- Water Requirement: LOW (<400mm), MEDIUM (400-700mm), HIGH (>700mm)
- Climate Risk Score: 0-30 = LOW risk, 31-60 = MODERATE, 61+ = HIGH risk for this crop

PROFITABILITY (2024-25 Season):
- Bajra/Pearl Millet: ₹35,000-45,000/acre
- Jowar/Sorghum: ₹30,000-40,000/acre  
- Chickpea/Chana: ₹28,000-35,000/acre
- Cotton: ₹40,000-60,000/acre
- Wheat: ₹35,000-45,000/acre
- Paddy/Rice: ₹30,000-40,000/acre (but high water needs)
- Tomato: ₹50,000-80,000/acre (but climate sensitive)
- Onion: ₹40,000-60,000/acre

CROPS TO AVOID if conditions are unfavorable:
- Paddy/Rice: If drought risk >60 (needs 1200mm water)
- Sugarcane: If drought risk >50 (very high water needs)
- Tomato: If heat stress >60 (sensitive to >35°C)

Provide specific, actionable recommendations with clear reasoning."""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_json_schema=CropRecommendations.model_json_schema(),
                temperature=0.2
            )
        )
        
        return CropRecommendations.model_validate_json(response.text)
        
    except Exception as e:
        st.error(f"Error getting recommendations: {str(e)}")
        return None

def display_recommendations(recommendations, season, farmer_name, location):
    """Display crop recommendations beautifully"""
    
    st.success("✅ AI Analysis Complete!")
    
    # Climate summary
    st.info(f"📊 **Climate Summary:** {recommendations.climate_summary}")
    
    st.divider()
    
    # Recommended crops
    st.subheader(f"🌾 Recommended Crops for {season} Season")
    
    for i, crop in enumerate(recommendations.recommended_crops, 1):
        # Determine border color based on risk
        if crop.climate_risk_score < 30:
            border_color = "#4CAF50"
            risk_emoji = "🟢"
        elif crop.climate_risk_score < 60:
            border_color = "#FBC02D"
            risk_emoji = "🟡"
        else:
            border_color = "#FF9800"
            risk_emoji = "🟠"
        
        st.markdown(f"""
        <div style='background: white; padding: 20px; border-radius: 12px; margin: 15px 0;
                    border-left: 5px solid {border_color}; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
            <h3 style='margin: 0 0 10px 0; color: #2E7D32;'>
                {i}. {crop.crop_name} ({crop.local_name})
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Drought Tolerance", f"{crop.drought_tolerance}/10")
        with col2:
            st.metric("Heat Tolerance", f"{crop.heat_tolerance}/10")
        with col3:
            st.metric("Water Need", crop.water_requirement)
        with col4:
            st.metric("Climate Risk", f"{risk_emoji} {crop.climate_risk_score}/100")
        
        # Expected profit
        st.markdown(f"**💰 Expected Profit:** ₹{crop.expected_profit_per_acre:,}/acre")
        st.caption(f"**Season:** {crop.growing_season}")
        
        # Reasons
        st.markdown("**✅ Why This Crop:**")
        for reason in crop.reasons:
            st.markdown(f"""
            <div class='reason-item'>
                • {reason}
            </div>
            """, unsafe_allow_html=True)
        
        # Adopt button
        if st.button(f"📌 Adopt {crop.crop_name}", key=f"adopt_{i}", width="stretch"):
            try:
                adoption_data = (
                    farmer_name,
                    crop.crop_name,
                    season,
                    datetime.now().year,
                    crop.climate_risk_score,
                    crop.drought_tolerance,
                    crop.water_requirement,
                    f"AI recommended based on climate analysis",
                    None,  # expected_yield
                    None,  # actual_yield
                    crop.expected_profit_per_acre,
                    None,  # profit_actual
                )
                add_data("crop_adoptions", adoption_data)
                st.success(f"✅ {crop.crop_name} adopted! Recorded in your profile.")
            except Exception as e:
                st.error(f"Error saving: {e}")
        
        st.markdown("---")
    
    # Crops to avoid
    st.subheader("❌ Crops to Avoid This Season")
    
    for crop_info in recommendations.avoid_crops:
        st.markdown(f"""
        <div class='crop-card crop-card-avoid'>
            <strong>⚠️</strong> {crop_info}
        </div>
        """, unsafe_allow_html=True)
    
    # Action buttons
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Try Different Season", width="stretch"):
            del st.session_state.crop_recommendations
            del st.session_state.crop_season
            st.rerun()
    
    with col2:
        if st.button("📊 View Climate Risk Details", width="stretch"):
            st.session_state.selected_menu = "🌡️ Climate Risk Dashboard"
            st.rerun()
