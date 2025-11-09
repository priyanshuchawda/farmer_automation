import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from google import genai
import pandas as pd

# Initialize AI AI
try:
    ai_client = genai.Client()
except Exception as e:
    ai_client = None

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_agmarknet_prices(state="Maharashtra", commodity="Tomato"):
    """Fetch live prices from Agmarknet website"""
    try:
        base_url = "https://agmarknet.gov.in/PriceAndArrivals/CommodityDailyStateWise.aspx"
        response = requests.get(base_url, timeout=30)
        
        if response.status_code != 200:
            return None, "Failed to connect to Agmarknet"

        soup = BeautifulSoup(response.text, "lxml")
        table = soup.find("table", {"class": "tableagmark_new"})
        
        if not table:
            return None, "Data table not found"

        rows = table.find_all("tr")[1:]  # skip header
        data = []
        
        for row in rows:
            cols = [col.text.strip() for col in row.find_all("td")]
            if len(cols) < 9:
                continue

            record = {
                "State": cols[0],
                "District": cols[1],
                "Market": cols[2],
                "Commodity": cols[3],
                "Variety": cols[4],
                "Date": cols[5],
                "Min Price": cols[6],
                "Max Price": cols[7],
                "Modal Price": cols[8],
            }
            data.append(record)

        df = pd.DataFrame(data)
        
        # Filter by state and commodity
        if not df.empty:
            df = df[
                (df["State"].str.lower().str.contains(state.lower(), na=False))
                & (df["Commodity"].str.lower().str.contains(commodity.lower(), na=False))
            ]
        
        return df, None
        
    except requests.Timeout:
        return None, "Connection timeout. Agmarknet server is slow."
    except Exception as e:
        return None, f"Error: {str(e)}"

# Fallback sample data
SAMPLE_PRICES = {
    "Maharashtra": {
        "Pune": {
            "Tomato": {"min": 15, "modal": 20, "max": 25},
            "Onion": {"min": 30, "modal": 35, "max": 40},
            "Potato": {"min": 18, "modal": 22, "max": 28},
            "Cabbage": {"min": 12, "modal": 15, "max": 18},
            "Cauliflower": {"min": 20, "modal": 25, "max": 30},
        },
        "Mumbai": {
            "Tomato": {"min": 18, "modal": 23, "max": 28},
            "Onion": {"min": 32, "modal": 38, "max": 45},
            "Potato": {"min": 20, "modal": 25, "max": 30},
        },
        "Nashik": {
            "Tomato": {"min": 14, "modal": 18, "max": 22},
            "Onion": {"min": 28, "modal": 32, "max": 38},
            "Potato": {"min": 16, "modal": 20, "max": 25},
        }
    },
    "Karnataka": {
        "Bangalore": {
            "Tomato": {"min": 16, "modal": 21, "max": 26},
            "Onion": {"min": 31, "modal": 36, "max": 42},
            "Potato": {"min": 19, "modal": 24, "max": 29},
        }
    },
    "Gujarat": {
        "Ahmedabad": {
            "Tomato": {"min": 15, "modal": 19, "max": 24},
            "Onion": {"min": 29, "modal": 34, "max": 39},
            "Potato": {"min": 17, "modal": 21, "max": 26},
        }
    }
}

def get_ai_market_insights(price_data, commodity, location):
    """Generate AI-powered market insights"""
    if not ai_client:
        return "AI insights unavailable. Please check AI API configuration."
    
    try:
        min_price = price_data.get("min", 0)
        max_price = price_data.get("max", 0)
        modal_price = price_data.get("modal", 0)
        
        prompt = f"""
As an agricultural market expert AI assistant, analyze this market data and provide actionable insights for a farmer:

**Market Data:**
- Commodity: {commodity}
- Location: {location}
- Minimum Price: ₹{min_price:.2f}/kg
- Modal Price: ₹{modal_price:.2f}/kg
- Maximum Price: ₹{max_price:.2f}/kg
- Price Range: ₹{max_price - min_price:.2f}/kg

**Your Task:**
Provide a comprehensive analysis with:

1. **Price Assessment** (2-3 sentences)
   - Is this a good price for farmers to sell?
   - Compare with typical market rates
   - Price volatility insights

2. **Selling Recommendations** (3-4 bullet points)
   - Best time to sell (immediate vs wait)
   - Expected price trends
   - Market demand indicators

3. **Strategic Advice** (3-4 bullet points)
   - Storage recommendations if applicable
   - Alternative markets to consider
   - Risk mitigation strategies

4. **Action Items** (2-3 specific steps)
   - What the farmer should do TODAY
   - Short-term planning (next 7 days)

Keep advice practical, specific to Indian agricultural markets, and focused on maximizing farmer profit.
"""
        
        response = ai_client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )
        return response.text
    
    except Exception as e:
        return f"Unable to generate AI insights: {str(e)}"

def ask_ai_assistant(user_query, context_data=None):
    """AI assistant for market questions with Google Search"""
    if not ai_client:
        return "❌ AI assistant unavailable. Please configure GEMINI_API_KEY in .env file."
    
    try:
        context = ""
        if context_data:
            context = f"\n**Farmer's Context:**\n{context_data}\n"
        
        prompt = f"""
You are an expert agricultural market advisor for Indian farmers.

{context}

**Farmer's Question:** {user_query}

**Instructions:**
1. Search Google for current market prices if the question is about prices
2. Provide accurate, real-time information
3. Give practical, actionable advice
4. Use simple language
5. Include specific numbers and locations when available

**Your Response:**
"""
        
        # Enable Google Search for real-time price data
        response = ai_client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config={
                'tools': [{'google_search': {}}],  # Enable Google Search
            }
        )
        return response.text
    
    except Exception as e:
        return f"❌ Error: {str(e)}"

def get_live_price_with_search(commodity, location):
    """Get live market prices for commodities"""
    if not ai_client:
        return None
    
    try:
        query = f"""
Find the current mandi/wholesale market price of {commodity} in {location}, India.
Provide:
1. Current price in ₹/kg
2. Price range (min to max)
3. Market name
4. Recent price trends if available

Keep response concise and factual.
"""
        
        response = ai_client.models.generate_content(
            model='gemini-2.0-flash',
            contents=query,
            config={
                'tools': [{'google_search': {}}],
            }
        )
        
        return response.text
    
    except Exception as e:
        return f"Error fetching prices: {str(e)}"

def render_market_price():
    """Main component to display market prices"""
    # Mobile responsive CSS for market price component
    st.markdown("""
    <style>
    @media (max-width: 768px) {
        /* Stack input columns */
        [data-testid="column"] {
            width: 100% !important;
            margin-bottom: 10px;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            font-size: 0.9rem !important;
            padding: 8px !important;
        }
        
        /* Text input sizing */
        .stTextInput input {
            font-size: 14px !important;
        }
    }
    
    @media (max-width: 480px) {
        /* Smaller expander headers */
        .streamlit-expanderHeader {
            font-size: 0.85rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.header("💰 Market Price Checker")
    st.caption("Live vegetable and commodity prices from government sources")
    
    # Get farmer's location from profile
    farmer_name = st.session_state.get("farmer_name")
    farmer_location = None
    
    if farmer_name:
        from database.db_functions import get_farmer_profile
        farmer_profile = get_farmer_profile(farmer_name)
        if farmer_profile:
            farmer_location = farmer_profile.get('location', '')
            # Extract city from full address (if it contains commas, take relevant part)
            if farmer_location:
                # Try to extract city name from address
                location_parts = [part.strip() for part in farmer_location.split(',')]
                # Look for city names in common positions
                for part in location_parts:
                    if any(keyword in part.lower() for keyword in ['pune', 'mumbai', 'nashik', 'bangalore', 'delhi', 'ahmedabad']):
                        farmer_location = part
                        break
                else:
                    # If no major city found, use the first meaningful part
                    farmer_location = location_parts[-3] if len(location_parts) >= 3 else location_parts[0]
    
    # Default prices for farmer's location
    if farmer_location:
        st.success(f"📍 Showing prices for your location: **{farmer_location}**")
        
        # Auto-fetch common crop prices for farmer's location
        st.subheader("🌾 Current Prices in Your Area")
        
        common_crops = ["Tomato", "Onion", "Potato", "Wheat", "Rice"]
        
        with st.spinner(f"🔍 AI is searching for current prices in {farmer_location}... Please wait..."):
            if ai_client:
                for crop in common_crops:
                    with st.expander(f"**{crop}** - Click to view details", expanded=False):
                        live_result = get_live_price_with_search(crop, farmer_location)
                        if live_result:
                            st.info(live_result)
                        else:
                            st.warning("Price data not available")
            else:
                st.warning("⚠️ AI service unavailable. Please check other locations manually below.")
        
        st.markdown("---")
    
    # Data source toggle
    col_mode, col_refresh = st.columns([4, 1])
    with col_mode:
        use_live_data = st.toggle("🌐 Fetch Live Market Data", value=True)
    with col_refresh:
        if st.button("🔄", help="Clear cache and refresh"):
            st.cache_data.clear()
            st.rerun()
    
    # Search for other locations
    st.subheader("🔍 Check Prices in Other Locations")
    st.caption("Search for prices in different cities or villages")
    
    col1, col2 = st.columns(2)
    
    with col1:
        live_commodity = st.text_input(
            "Commodity",
            placeholder="e.g., Tomato, Onion, Potato",
            key="live_commodity"
        )
    with col2:
        live_location = st.text_input(
            "Location (City/Village)",
            placeholder="e.g., Pune, Mumbai, Nashik",
            key="live_location"
        )
    
    if st.button("🔍 Search Prices", use_container_width=True, type="primary"):
        if live_commodity and live_location:
            with st.spinner(f"🔍 AI is searching for {live_commodity} prices in {live_location}... Please wait..."):
                if ai_client:
                    live_result = get_live_price_with_search(live_commodity, live_location)
                    if live_result:
                        st.success(f"✅ Price information for {live_commodity} in {live_location}")
                        st.info(live_result)
                        
                        # AI Insights
                        with st.expander("🤖 Market Insights & Recommendations", expanded=True):
                            with st.spinner("🤖 AI is analyzing market conditions... Please wait..."):
                                insight_query = f"Based on current {live_commodity} prices in {live_location}, provide selling recommendations for farmers"
                                insights = ask_ai_assistant(insight_query, f"Commodity: {live_commodity}\nLocation: {live_location}")
                                st.markdown(insights)
                else:
                    st.error("Service temporarily unavailable")
        else:
            st.warning("⚠️ Please enter both commodity and location")
    
    # AI Assistant Chatbot
    st.divider()
    st.markdown("### 🤖 AI Market Assistant")
    st.caption("Ask anything about market prices, selling strategies, or crop planning!")
    
    if 'market_chat_history' not in st.session_state:
        st.session_state.market_chat_history = []
    
    user_question = st.text_input(
        "Ask your question:",
        placeholder="e.g., 'What is current tomato price in Pune?', 'Should I sell my onions now?'",
        key="market_ai_query"
    )
    
    col_ask, col_clear = st.columns([4, 1])
    with col_ask:
        ask_button = st.button("💬 Ask AI", use_container_width=True, type="secondary")
    with col_clear:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.market_chat_history = []
            st.rerun()
    
    if ask_button and user_question:
        with st.spinner("🤖 AI is searching and analyzing your question... Please wait..."):
            context = ""
            if 'live_commodity' in locals() and live_commodity:
                context += f"Commodity: {live_commodity}\n"
            if 'live_location' in locals() and live_location:
                context += f"Location: {live_location}\n"
            
            ai_response = ask_ai_assistant(user_question, context)
            
            st.session_state.market_chat_history.append({
                "question": user_question,
                "answer": ai_response,
                "timestamp": datetime.now().strftime("%H:%M")
            })
    
    # Display chat history
    if st.session_state.market_chat_history:
        st.markdown("#### 💭 Conversation History")
        for chat in reversed(st.session_state.market_chat_history[-5:]):
            with st.container():
                st.markdown(f"**👤 You ({chat['timestamp']}):** {chat['question']}")
                st.markdown(f"**🤖 AI Assistant:**")
                st.info(chat['answer'])
                st.divider()


