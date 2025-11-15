"""
Water & Carbon Footprint Tracker
Helps farmers track sustainability metrics
"""

import streamlit as st
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
import os
from database.db_functions import get_farmer_profile, add_data
from components.translation_utils import t

class SustainabilityAnalysis(BaseModel):
    """Sustainability analysis with recommendations"""
    water_efficiency_score: int = Field(description="Water efficiency score 0-100", ge=0, le=100)
    carbon_efficiency_score: int = Field(description="Carbon efficiency score 0-100", ge=0, le=100)
    water_savings_potential: int = Field(description="Water savings in liters if optimized")
    carbon_reduction_potential: float = Field(description="Carbon reduction in tons CO2/year")
    cost_savings_potential: int = Field(description="Money savings in rupees per year")
    recommendations: List[str] = Field(description="3-5 specific actionable recommendations")

def render_sustainability_tracker():
    """Render water and carbon tracker page"""
    
    st.markdown("""
    <style>
    .sustainability-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        margin: 15px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .good-score {
        color: #4CAF50;
        font-weight: bold;
    }
    .poor-score {
        color: #F57C00;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.header("💧 Water & Carbon Footprint Tracker")
    st.caption("Track your farm's sustainability and get improvement recommendations")
    
    farmer_name = st.session_state.get("farmer_name", "Farmer")
    farmer_profile = st.session_state.get("farmer_profile", {})
    
    # Input form
    st.subheader("📝 Enter Your Farm Details")
    
    with st.form("sustainability_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🌾 Crop Information")
            crop_type = st.selectbox(
                "What crop did you grow?",
                ["Paddy/Rice", "Wheat", "Cotton", "Sugarcane", "Tomato", "Onion", 
                 "Bajra/Pearl Millet", "Jowar/Sorghum", "Chickpea/Chana", "Other"]
            )
            
            farm_area = st.number_input(
                "Farm area (acres)",
                min_value=0.1,
                value=2.0,
                step=0.5
            )
            
            season = st.selectbox(
                "Season",
                ["Kharif (Monsoon)", "Rabi (Winter)", "Zaid (Summer)"]
            )
        
        with col2:
            st.markdown("#### 💧 Water Usage")
            irrigation_method = st.selectbox(
                "Irrigation method",
                ["Flood/Traditional", "Drip Irrigation", "Sprinkler", "Rainfed"]
            )
            
            water_source = st.selectbox(
                "Water source",
                ["Borewell/Tubewell", "Canal", "River", "Rainwater", "Mixed"]
            )
            
            irrigation_hours = st.number_input(
                "Irrigation hours per week",
                min_value=0,
                value=20,
                step=5
            )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🌱 Farming Practices")
            fertilizer_type = st.selectbox(
                "Fertilizer type",
                ["Chemical/Synthetic", "Organic", "Mixed", "None"]
            )
            
            energy_source = st.selectbox(
                "Pump energy source",
                ["Diesel", "Electric", "Solar", "No pump"]
            )
        
        with col2:
            st.markdown("#### 📊 Additional Info")
            diesel_liters = 0
            if energy_source == "Diesel":
                diesel_liters = st.number_input(
                    "Diesel used (liters/month)",
                    min_value=0,
                    value=50
                )
            
            electricity_units = 0
            if energy_source == "Electric":
                electricity_units = st.number_input(
                    "Electricity (units/month)",
                    min_value=0,
                    value=500
                )
        
        submitted = st.form_submit_button("🔍 Analyze Sustainability", type="primary", width="stretch")
        
        if submitted:
            with st.spinner("🤖 AI is analyzing your sustainability metrics..."):
                analysis = analyze_sustainability(
                    crop_type, farm_area, season, irrigation_method,
                    water_source, irrigation_hours, fertilizer_type,
                    energy_source, diesel_liters, electricity_units
                )
                
                if analysis:
                    st.session_state.sustainability_analysis = analysis
                    st.session_state.sustainability_inputs = {
                        'crop_type': crop_type,
                        'farm_area': farm_area,
                        'season': season,
                        'irrigation_method': irrigation_method,
                        'fertilizer_type': fertilizer_type,
                        'energy_source': energy_source
                    }
                    
                    # Save to database
                    try:
                        year = datetime.now().year
                        season_key = season.split(" ")[0]
                        
                        sustainability_data = (
                            farmer_name,
                            season_key,
                            year,
                            None,  # water_usage (calculated)
                            None,  # water_optimal (calculated)
                            None,  # carbon_emissions (calculated)
                            irrigation_method,
                            fertilizer_type,
                            energy_source,
                            crop_type,
                        )
                        add_data("sustainability_metrics", sustainability_data)
                    except Exception as e:
                        print(f"Error saving sustainability data: {e}")
                    
                    st.rerun()
    
    # Display analysis
    if 'sustainability_analysis' in st.session_state:
        display_analysis(st.session_state.sustainability_analysis, st.session_state.sustainability_inputs)

def analyze_sustainability(crop_type, farm_area, season, irrigation_method, 
                          water_source, irrigation_hours, fertilizer_type,
                          energy_source, diesel_liters, electricity_units):
    """Analyze sustainability using AI"""
    
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("⚠️ AI API key not configured")
        return None
    
    try:
        client = genai.Client(api_key=api_key)
        
        prompt = f"""You are a sustainability expert analyzing farm practices.

FARM DETAILS:
- Crop: {crop_type}
- Area: {farm_area} acres
- Season: {season}
- Irrigation: {irrigation_method}
- Water Source: {water_source}
- Irrigation Hours/Week: {irrigation_hours}
- Fertilizer: {fertilizer_type}
- Energy: {energy_source}
- Diesel Usage: {diesel_liters} liters/month
- Electricity: {electricity_units} units/month

TASK: Analyze water and carbon efficiency

WATER EFFICIENCY SCORING:
- Drip irrigation: 85-95 score (40% less water than flood)
- Sprinkler: 70-80 score (25% less water)
- Flood/Traditional: 30-50 score (baseline)
- Rainfed: 95-100 score (no irrigation water)

CARBON EFFICIENCY SCORING:
- Solar: 95-100 score (zero emissions)
- Electric: 60-75 score (coal power emissions)
- Diesel: 20-40 score (high emissions, 2.7kg CO2/liter)
- Organic fertilizer: +10 bonus points
- Chemical fertilizer: -5 penalty points

WATER CALCULATION (Average per acre per season):
- Paddy/Rice: 1200mm (very high)
- Sugarcane: 1800mm (extremely high)
- Cotton: 700mm (high)
- Wheat: 450mm (medium)
- Vegetables (Tomato/Onion): 500mm (medium)
- Bajra/Jowar: 350mm (low)
- Chickpea: 300mm (low)

CARBON EMISSIONS:
- Diesel pump: 2.7kg CO2 per liter
- Electric pump: 0.8kg CO2 per unit (coal power)
- Chemical fertilizer: ~50kg CO2 per acre
- Tractor operations: ~30kg CO2 per acre

Calculate realistic savings and provide specific, actionable recommendations."""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_json_schema=SustainabilityAnalysis.model_json_schema(),
                temperature=0.2
            )
        )
        
        return SustainabilityAnalysis.model_validate_json(response.text)
        
    except Exception as e:
        st.error(f"Error analyzing sustainability: {str(e)}")
        return None

def display_analysis(analysis, inputs):
    """Display sustainability analysis"""
    
    st.success("✅ Sustainability Analysis Complete!")
    st.divider()
    
    # Efficiency scores
    st.subheader("📊 Your Sustainability Scores")
    
    col1, col2 = st.columns(2)
    
    with col1:
        water_score = analysis.water_efficiency_score
        water_class = "good-score" if water_score >= 70 else "poor-score"
        
        st.markdown(f"""
        <div class='sustainability-card'>
            <h3>💧 Water Efficiency</h3>
            <h1 class='{water_class}'>{water_score}/100</h1>
            <p>{"Excellent water management!" if water_score >= 70 else "Room for improvement in water usage"}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        carbon_score = analysis.carbon_efficiency_score
        carbon_class = "good-score" if carbon_score >= 70 else "poor-score"
        
        st.markdown(f"""
        <div class='sustainability-card'>
            <h3>🌱 Carbon Efficiency</h3>
            <h1 class='{carbon_class}'>{carbon_score}/100</h1>
            <p>{"Great low-carbon farming!" if carbon_score >= 70 else "Opportunities to reduce carbon footprint"}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Savings potential
    st.divider()
    st.subheader("💰 Optimization Potential")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Water Savings",
            f"{analysis.water_savings_potential:,} liters/year",
            help="Potential water savings with optimized irrigation"
        )
    
    with col2:
        st.metric(
            "Carbon Reduction",
            f"{analysis.carbon_reduction_potential:.1f} tons CO2/year",
            help="Potential carbon emissions reduction"
        )
    
    with col3:
        st.metric(
            "Cost Savings",
            f"₹{analysis.cost_savings_potential:,}/year",
            help="Estimated money savings from optimization"
        )
    
    # Recommendations
    st.divider()
    st.subheader("✅ AI Recommendations")
    
    for i, recommendation in enumerate(analysis.recommendations, 1):
        st.markdown(f"""
        <div class='sustainability-card'>
            <strong>{i}.</strong> {recommendation}
        </div>
        """, unsafe_allow_html=True)
    
    # Current practices summary
    st.divider()
    st.subheader("📋 Your Current Practices")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Crop:** {inputs['crop_type']}")
        st.write(f"**Farm Size:** {inputs['farm_area']} acres")
        st.write(f"**Season:** {inputs['season']}")
    
    with col2:
        st.write(f"**Irrigation:** {inputs['irrigation_method']}")
        st.write(f"**Fertilizer:** {inputs['fertilizer_type']}")
        st.write(f"**Energy:** {inputs['energy_source']}")
    
    # Action buttons
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Analyze Different Season", width="stretch"):
            del st.session_state.sustainability_analysis
            del st.session_state.sustainability_inputs
            st.rerun()
    
    with col2:
        if st.button("🌾 Get Climate-Smart Crops", width="stretch"):
            st.session_state.selected_menu = "🌾 Climate-Smart Crops"
            st.rerun()
