# components/simple_price_advisor.py
"""
SIMPLE PRICE ADVISOR - Should I sell today or wait?
Uses Gemini 2.5 Flash for smart recommendations
"""

import streamlit as st
from google import genai
from google.genai import types
import os
from datetime import datetime, timedelta, date
from components.translation_utils import t
from dotenv import load_dotenv
import requests
import json

load_dotenv()

class SimplePriceAdvisor:
    """AI-powered simple price advisor using Gemini 2.5 Flash."""
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            self.client = None
            return
        
        try:
            self.client = genai.Client(api_key=api_key)
            # Use Gemini 2.5 Flash for fast, smart recommendations
            self.model = 'gemini-2.5-flash'
            print("✅ Using Gemini 2.5 Flash for Price Advisor")
        except Exception as e:
            print(f"⚠️ AI initialization failed: {e}")
            self.client = None
    
    def get_simple_advice(self, crop, current_price, location, market_days):
        """Get simple YES/NO advice: sell now or wait?"""
        
        if not self.client:
            return self._fallback_advice(crop, current_price, market_days)
        
        today = date.today()
        
        # System instruction - role and behavior
        system_instruction = """You are a market timing expert for Indian farmers.
Your goal: Give clear YES/NO advice on selling timing.
Use simple language - assume farmer has 5-8th grade education.
Base advice on practical factors: seasonality, storage, weather, and profit."""
        
        # Format market days for better readability
        market_schedule = '\n'.join([f"  - {d['day']} ({d['date'].strftime('%d %b')})" for d in market_days])
        
        # Task prompt - optimized with clearer structure and examples
        task_prompt = f"""A farmer needs simple advice: SELL NOW or WAIT?

SITUATION:
Crop: {crop}
Current Mandi Price: ₹{current_price} per kg
Location: {location}, India
Today: {today.strftime('%A, %d %B %Y')}

Upcoming Market Days:
{market_schedule}

YOUR TASK:
Analyze 5 key factors and recommend SELL NOW or WAIT:

1. SEASONAL SUPPLY
   - Is this harvest season for {crop} in {location}? (harvest = high supply = falling prices)
   - Is supply increasing or decreasing in {today.strftime('%B')}?

2. PRICE TREND PATTERN
   - Historical pattern: Do {crop} prices typically rise or fall in {today.strftime('%B')}?
   - Recent trend: Are prices moving up or down?

3. STORAGE CAPABILITY
   - {crop} perishability: Can it be stored 3-7 days without major loss?
   - Storage available to farmer? (assume basic storage, not cold storage)

4. PROFIT OPPORTUNITY
   - Expected price change in next 3-7 days: +₹X or -₹X per kg?
   - For 100kg harvest: Will waiting gain more than ₹100-200 profit?

5. RISK FACTORS
   - Weather risk: Monsoon/rain expected soon?
   - Quality risk: Will crop quality degrade fast?
   - Market risk: Are many farmers about to harvest (supply flood)?

OUTPUT (use exact format):

RECOMMENDATION: [SELL NOW or WAIT]

NEXT BEST DAY: [specific day], [date in DD Mon format]
EXPECTED PRICE: ₹[number]/kg
PRICE CHANGE: [↑ UP by ₹X / ↓ DOWN by ₹X / → SAME]

REASON: [ONE simple sentence explaining the recommendation - use farmer language]

PROFIT IMPACT: For 100kg harvest, waiting will [GAIN/LOSE/BREAK_EVEN] approximately ₹[specific amount]

RISK: [LOW/MEDIUM/HIGH] - [ONE sentence about biggest risk]

FEW-SHOT EXAMPLES:

Example 1: Tomato, ₹20/kg, November (Harvest Season)
RECOMMENDATION: SELL NOW

NEXT BEST DAY: Monday, 14 Nov
EXPECTED PRICE: ₹17/kg
PRICE CHANGE: ↓ DOWN by ₹3

REASON: All farmers harvesting now - tomato supply very high this month, prices dropping every day

PROFIT IMPACT: For 100kg harvest, waiting will LOSE approximately ₹300

RISK: HIGH - Tomatoes will spoil in 3-4 days without cold storage, quality drops fast


Example 2: Wheat, ₹29/kg, January (Off-Season)
RECOMMENDATION: WAIT

NEXT BEST DAY: Saturday, 15 Jan
EXPECTED PRICE: ₹32/kg
PRICE CHANGE: ↑ UP by ₹3

REASON: Harvest finished 2 months ago - wheat supply low, demand high, government buying at MSP

PROFIT IMPACT: For 100kg harvest, waiting will GAIN approximately ₹300

RISK: LOW - Wheat can be stored 6+ months easily, no rain expected, quality stays good


Now provide advice for this farmer's {crop}:"""
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=task_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.2,  # Low for consistent advice
                    max_output_tokens=400
                )
            )
            
            return response.text
        
        except Exception as e:
            print(f"AI error: {e}")
            return self._fallback_advice(crop, current_price, market_days)
    
    def _fallback_advice(self, crop, current_price, market_days):
        """Simple rule-based advice if AI fails."""
        today = date.today()
        next_market = market_days[0] if market_days else None
        
        if not next_market:
            return "Unable to provide advice without market day information."
        
        # Simple rules
        month = today.month
        
        # Peak harvest months (prices usually drop)
        harvest_months = {
            'Tomatoes': [11, 12, 1, 2],  # Nov-Feb
            'Onions': [1, 2, 3, 4],      # Jan-Apr
            'Wheat': [3, 4],              # Mar-Apr
            'Rice': [10, 11],             # Oct-Nov
        }
        
        is_harvest_season = month in harvest_months.get(crop, [])
        
        if is_harvest_season:
            advice = "SELL NOW"
            reason = "Harvest season - many farmers selling, prices may drop"
            price_trend = "↓ DOWN"
        else:
            advice = "WAIT"
            reason = "Off-season - demand is high, prices may increase"
            price_trend = "↑ UP"
        
        return f"""
RECOMMENDATION: {advice}

NEXT BEST DAY: {next_market['day']}, {next_market['date'].strftime('%d %B')}
EXPECTED PRICE: ₹{current_price}/kg
PRICE CHANGE: {price_trend} by ₹2-5

REASON: {reason}

PROFIT IMPACT: Hard to predict exactly, but check weather forecast!

RISK: MEDIUM - Always check weather before deciding!
"""


def render_simple_price_advisor():
    """Render the simple price advisor page."""
    
    # CSS for clean, simple look
    st.markdown("""
    <style>
    .sell-now-card {
        background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        border: 4px solid #2E7D32;
        box-shadow: 0 6px 16px rgba(0,0,0,0.2);
        margin: 20px 0;
        color: white;
    }
    
    .wait-card {
        background: linear-gradient(135deg, #FF9800 0%, #FFA726 100%);
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        border: 4px solid #F57C00;
        box-shadow: 0 6px 16px rgba(0,0,0,0.2);
        margin: 20px 0;
        color: white;
    }
    
    .price-box {
        background: white;
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #2196F3;
        margin: 15px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .advice-box {
        background: #FFF9C4;
        padding: 25px;
        border-radius: 12px;
        border: 3px solid #FBC02D;
        margin: 20px 0;
    }
    
    .big-price {
        font-size: 42px;
        font-weight: bold;
        margin: 10px 0;
    }
    
    @media (max-width: 768px) {
        .big-price { font-size: 32px; }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
                padding: 25px; border-radius: 15px; text-align: center; 
                margin-bottom: 30px; box-shadow: 0 4px 12px rgba(0,0,0,0.2);'>
        <h1 style='color: white; margin: 0; font-size: 32px;'>🤔 {t("Should I Sell Today?")}</h1>
        <p style='color: white; margin: 10px 0 0 0; font-size: 18px; opacity: 0.95;'>
            {t("Get AI-powered advice in 1 minute")}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Input form - SIMPLE
    st.markdown(f"### 📝 {t('Tell me about your situation')}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        crop = st.selectbox(
            f"🌾 {t('What crop did you harvest?')}",
            [
                "Tomatoes", "Onions", "Potatoes", "Wheat", "Rice",
                "Cotton", "Sugarcane", "Grapes", "Banana", "Chilli",
                "Turmeric", "Soybeans", "Groundnut", "Bajra", "Jowar"
            ]
        )
        
        current_price = st.number_input(
            f"💰 {t('Today market price')} (₹/kg)",
            min_value=1,
            value=25,
            step=1
        )
    
    with col2:
        profile = st.session_state.get("farmer_profile", {})
        location = profile.get("location", "Pune") if profile else "Pune"
        
        st.text_input(f"📍 {t('Your Location')}", value=location, disabled=True)
        
        quantity = st.number_input(
            f"📦 {t('How much do you have?')} (kg)",
            min_value=1,
            value=100,
            step=10
        )
    
    # Market days selection
    st.markdown(f"### 📅 {t('When are the market days?')}")
    
    today = date.today()
    
    # Common market day patterns in India
    st.info(f"ℹ️ {t('Select the days when mandi happens in your area')}")
    
    col1, col2, col3 = st.columns(3)
    
    market_days = []
    
    with col1:
        if st.checkbox(f"📅 {t('Tomorrow')} ({(today + timedelta(days=1)).strftime('%A')})", value=True):
            market_days.append({
                'day': (today + timedelta(days=1)).strftime('%A'),
                'date': today + timedelta(days=1),
                'days_from_now': 1
            })
    
    with col2:
        day3 = today + timedelta(days=3)
        if st.checkbox(f"📅 {day3.strftime('%A')} ({t('3 days later')})", value=True):
            market_days.append({
                'day': day3.strftime('%A'),
                'date': day3,
                'days_from_now': 3
            })
    
    with col3:
        day7 = today + timedelta(days=7)
        if st.checkbox(f"📅 {day7.strftime('%A')} ({t('Next week')})", value=False):
            market_days.append({
                'day': day7.strftime('%A'),
                'date': day7,
                'days_from_now': 7
            })
    
    st.markdown("---")
    
    # Get advice button
    if st.button(f"🤖 {t('GET AI ADVICE NOW')}", type="primary", use_container_width=True):
        if not market_days:
            st.error(f"⚠️ {t('Please select at least one market day!')}")
            return
        
        with st.spinner(f"🤔 {t('AI is analyzing prices, weather, and market trends...')}"):
            advisor = SimplePriceAdvisor()
            advice = advisor.get_simple_advice(crop, current_price, location, market_days)
            
            # Store in session state
            st.session_state.price_advice = advice
            st.session_state.crop_for_advice = crop
            st.session_state.current_price_shown = current_price
            st.session_state.quantity_shown = quantity
    
    # Display advice if available
    if 'price_advice' in st.session_state:
        advice = st.session_state.price_advice
        crop = st.session_state.crop_for_advice
        shown_price = st.session_state.current_price_shown
        shown_qty = st.session_state.quantity_shown
        
        st.markdown("---")
        st.markdown(f"## 🎯 {t('AI RECOMMENDATION')}")
        
        # Parse recommendation
        lines = advice.split('\n')
        recommendation = ""
        
        for line in lines:
            if line.startswith("RECOMMENDATION:"):
                recommendation = line.split(":", 1)[1].strip()
                break
        
        # Show big card with recommendation
        if "SELL NOW" in recommendation or "SELL" in recommendation.upper():
            st.markdown(f"""
            <div class='sell-now-card'>
                <h1 style='margin: 0; font-size: 48px;'>✅ SELL NOW!</h1>
                <p style='margin: 15px 0 0 0; font-size: 20px; opacity: 0.95;'>
                    {t("Don't wait - sell at the next market!")}
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='wait-card'>
                <h1 style='margin: 0; font-size: 48px;'>⏳ WAIT!</h1>
                <p style='margin: 15px 0 0 0; font-size: 20px; opacity: 0.95;'>
                    {t("Better price expected later!")}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Display full advice in clean format
        st.markdown(f"""
        <div class='advice-box'>
            <h3 style='color: #F57F00; margin: 0 0 15px 0;'>💡 {t("Detailed Analysis")}</h3>
            <div style='white-space: pre-wrap; font-size: 16px; line-height: 1.8;'>
{advice}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Today's price display
        st.markdown(f"""
        <div class='price-box'>
            <h3 style='color: #1976D2; margin: 0 0 10px 0;'>📅 {t("TODAY")}</h3>
            <p style='margin: 5px 0;'><strong>🌾 {t("Crop")}:</strong> {crop}</p>
            <p style='margin: 5px 0;'><strong>💰 {t("Current Price")}:</strong> ₹{shown_price}/kg</p>
            <p style='margin: 5px 0;'><strong>📦 {t("Quantity")}:</strong> {shown_qty} kg</p>
            <p style='margin: 5px 0;'><strong>💵 {t("Total Value")}:</strong> ₹{shown_price * shown_qty:,.0f}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Action buttons
        st.markdown("")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(f"🔄 {t('Check Another Crop')}", use_container_width=True):
                del st.session_state.price_advice
                st.rerun()
        
        with col2:
            if st.button(f"🌤️ {t('Check Weather')}", use_container_width=True):
                st.session_state.nav_history.append(st.session_state.selected_menu)
                st.session_state.nav_forward = []
                st.session_state.selected_menu = "🌤️ Weather Forecast"
                st.rerun()
    
    # Help section
    st.markdown("---")
    with st.expander(f"❓ {t('How does this work?')}"):
        st.markdown(f"""
        ### 🎯 {t("Super Simple Price Advisor")}
        
        **{t("What it does:")}**
        - {t("Analyzes current market trends")}
        - {t("Checks seasonal patterns")}
        - {t("Considers weather forecasts")}
        - {t("Calculates profit/loss for waiting")}
        - {t("Gives you ONE clear answer: SELL NOW or WAIT")}
        
        **{t("How to use:")}**
        1. {t("Select your crop")}
        2. {t("Enter today's price")}
        3. {t("Select market days")}
        4. {t("Click 'GET AI ADVICE'")}
        5. {t("Get instant recommendation!")}
        
        **⏱️ {t("Takes only 1 minute!")}**
        
        **🤖 {t("Powered by Google Gemini 2.5 Flash AI")}**
        """)
