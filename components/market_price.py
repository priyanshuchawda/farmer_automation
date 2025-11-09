import streamlit as st
import requests
import os
from datetime import datetime, timedelta
from google import genai
import pandas as pd

API_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
API_KEY = os.getenv("DATAGOVIN_API_KEY")

# Initialize AI AI
try:
    ai_client = genai.Client()
except Exception as e:
    ai_client = None
    print(f"AI AI initialization failed: {e}")

def get_all_states():
    """Fetch all unique states from the API"""
    params = {
        "api-key": API_KEY,
        "format": "json",
        "limit": 10000
    }
    response = requests.get(API_URL, params=params)
    data = response.json()
    records = data.get("records", [])
    states = sorted(set(r["state"] for r in records if r.get("state")))
    return states

def get_districts_by_state(state_name):
    """Fetch districts for a given state"""
    params = {
        "api-key": API_KEY,
        "format": "json",
        "limit": 10000,
        "filters[state]": state_name
    }
    response = requests.get(API_URL, params=params)
    data = response.json()
    records = data.get("records", [])
    districts = sorted(set(r["district"] for r in records if r.get("district")))
    return districts

def get_markets_by_district(district_name):
    """Fetch markets for a given district"""
    params = {
        "api-key": API_KEY,
        "format": "json",
        "limit": 10000,
        "filters[district]": district_name
    }
    response = requests.get(API_URL, params=params)
    data = response.json()
    records = data.get("records", [])
    markets = sorted(set(r["market"] for r in records if r.get("market")))
    return markets

def get_price_data(commodity, market, date):
    """Fetch price data for a commodity at a market on a specific date"""
    params = {
        "api-key": API_KEY,
        "format": "json",
        "limit": 10000,
        "filters[commodity]": commodity,
        "filters[market]": market,
        "filters[arrival_date]": date
    }
    response = requests.get(API_URL, params=params)
    data = response.json()
    records = data.get("records", [])
    return records

def get_historical_price_data(commodity, market, days=7):
    """Fetch historical price data for trend analysis"""
    all_records = []
    for i in range(days):
        date = (datetime.now() - timedelta(days=i+1)).strftime("%Y-%m-%d")
        records = get_price_data(commodity, market, date)
        all_records.extend(records)
    return all_records

def get_ai_market_insights(price_data, commodity, location, farmer_crops=None):
    """Generate AI-powered market insights and recommendations"""
    if not ai_client:
        return "AI insights unavailable. Please check AI API configuration."
    
    # Prepare price summary
    if not price_data:
        return "No price data available for analysis."
    
    try:
        min_price = float(price_data.get("min_price", 0)) / 100
        max_price = float(price_data.get("max_price", 0)) / 100
        modal_price = float(price_data.get("modal_price", 0)) / 100
        
        prompt = f"""
As an agricultural market expert AI assistant, analyze this market data and provide actionable insights for a farmer:

**Market Data:**
- Commodity: {commodity}
- Location: {location}
- Date: {price_data.get('arrival_date')}
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
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text
    
    except Exception as e:
        return f"Unable to generate AI insights: {str(e)}"

def ask_ai_assistant(user_query, context_data=None):
    """AI assistant for answering market price related questions"""
    if not ai_client:
        return "❌ AI assistant unavailable. Please configure GEMINI_API_KEY in .env file."
    
    try:
        context = ""
        if context_data:
            context = f"\n**Available Market Context:**\n{context_data}\n"
        
        prompt = f"""
You are an expert agricultural market advisor for Indian farmers. Answer the farmer's question with:
- Accurate, practical advice
- Indian market context
- Specific actionable recommendations
- Simple language (avoid technical jargon)

{context}

**Farmer's Question:** {user_query}

**Your Response:**
"""
        
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text
    
    except Exception as e:
        return f"❌ Error: {str(e)}"

def render_market_price():
    """Main component to display market prices"""
    st.header("💰 Market Price Checker")
    st.caption("Check live vegetable and commodity prices from government mandis across India")
    
    if not API_KEY:
        st.error("⚠️ DATAGOVIN_API_KEY not found in .env file. Please add your API key from data.gov.in")
        st.info("📝 Get your API key from: https://data.gov.in/")
        return
    
    try:
        # State Selection
        st.subheader("📍 Select Location")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            with st.spinner("Loading states..."):
                states = get_all_states()
            selected_state = st.selectbox("Select State", states, key="state_select")
        
        with col2:
            if selected_state:
                with st.spinner("Loading districts..."):
                    districts = get_districts_by_state(selected_state)
                selected_district = st.selectbox("Select District", districts, key="district_select")
            else:
                selected_district = None
        
        with col3:
            if selected_district:
                with st.spinner("Loading markets..."):
                    markets = get_markets_by_district(selected_district)
                selected_market = st.selectbox("Select Market", markets, key="market_select")
            else:
                selected_market = None
        
        # Commodity and Date Selection
        st.divider()
        st.subheader("🥬 Price Search")
        col4, col5 = st.columns(2)
        
        with col4:
            commodity = st.text_input(
                "Commodity Name", 
                placeholder="e.g., Tomato, Onion, Potato",
                help="Enter the exact name of the commodity"
            )
        
        with col5:
            # Default to yesterday's date (market data is usually a day behind)
            default_date = datetime.now().date() - timedelta(days=1)
            selected_date = st.date_input("Select Date", value=default_date)
        
        # Search Button
        if st.button("🔍 Get Price", use_container_width=True, type="primary"):
            if not selected_market:
                st.warning("⚠️ Please select a market")
            elif not commodity:
                st.warning("⚠️ Please enter a commodity name")
            else:
                with st.spinner("Fetching price data..."):
                    date_str = selected_date.strftime("%Y-%m-%d")
                    records = get_price_data(commodity, selected_market, date_str)
                    
                    if not records:
                        st.error(f"❌ No price data found for {commodity} in {selected_market} on {date_str}")
                        st.info("💡 Try:\n- Different commodity name\n- Different date\n- Check spelling")
                    else:
                        st.success(f"✅ Found {len(records)} price record(s)")
                        
                        for idx, record in enumerate(records):
                            min_price = float(record.get("min_price", 0)) / 100
                            max_price = float(record.get("max_price", 0)) / 100
                            modal_price = float(record.get("modal_price", 0)) / 100
                            
                            st.markdown(f"""
                            <div class='card'>
                                <h4>📊 {record.get('commodity')}</h4>
                                <p><strong>🏬 Market:</strong> {record.get('market')}</p>
                                <p><strong>📍 Location:</strong> {record.get('district')}, {record.get('state')}</p>
                                <p><strong>📅 Date:</strong> {record.get('arrival_date')}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            col_a, col_b, col_c = st.columns(3)
                            with col_a:
                                st.metric("Minimum Price", f"₹{min_price:.2f}/kg")
                            with col_b:
                                st.metric("Modal Price", f"₹{modal_price:.2f}/kg", 
                                         delta=f"±₹{(max_price-min_price)/2:.2f}")
                            with col_c:
                                st.metric("Maximum Price", f"₹{max_price:.2f}/kg")
                            
                            # AI Insights
                            if ai_client:
                                with st.expander("🤖 AI Market Insights & Recommendations", expanded=True):
                                    with st.spinner("Analyzing market data with AI..."):
                                        location_str = f"{record.get('market')}, {record.get('district')}, {record.get('state')}"
                                        insights = get_ai_market_insights(record, commodity, location_str)
                                        st.markdown(insights)
                            
                            # Price Trend Analysis
                            with st.expander("📈 7-Day Price Trend"):
                                with st.spinner("Fetching historical data..."):
                                    historical = get_historical_price_data(commodity, selected_market, days=7)
                                    if historical:
                                        df_hist = pd.DataFrame([{
                                            'Date': h.get('arrival_date'),
                                            'Min Price (₹/kg)': float(h.get('min_price', 0)) / 100,
                                            'Modal Price (₹/kg)': float(h.get('modal_price', 0)) / 100,
                                            'Max Price (₹/kg)': float(h.get('max_price', 0)) / 100
                                        } for h in historical])
                                        
                                        if not df_hist.empty:
                                            st.line_chart(df_hist.set_index('Date'))
                                            st.dataframe(df_hist, use_container_width=True)
                                        else:
                                            st.info("No historical data available")
                                    else:
                                        st.info("No historical data available for trend analysis")
                            
                            st.divider()
    
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.info("Please check your API key and internet connection")
    
    # AI Assistant Chatbot Section
    st.divider()
    st.markdown("### 🤖 AI Market Assistant")
    st.caption("Ask anything about market prices, selling strategies, or crop planning!")
    
    # Chat interface
    if 'market_chat_history' not in st.session_state:
        st.session_state.market_chat_history = []
    
    user_question = st.text_input(
        "Ask your question:",
        placeholder="e.g., 'When is the best time to sell tomatoes?', 'Should I store onions or sell now?'",
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
        with st.spinner("🤔 AI is thinking..."):
            # Prepare context
            context = ""
            if 'selected_state' in locals():
                context += f"State: {selected_state}\n"
            if 'selected_district' in locals() and selected_district:
                context += f"District: {selected_district}\n"
            if 'commodity' in locals() and commodity:
                context += f"Commodity of Interest: {commodity}\n"
            
            ai_response = ask_ai_assistant(user_question, context)
            
            st.session_state.market_chat_history.append({
                "question": user_question,
                "answer": ai_response,
                "timestamp": datetime.now().strftime("%H:%M")
            })
    
    # Display chat history
    if st.session_state.market_chat_history:
        st.markdown("#### 💭 Conversation History")
        for chat in reversed(st.session_state.market_chat_history[-5:]):  # Show last 5
            with st.container():
                st.markdown(f"**👤 You ({chat['timestamp']}):** {chat['question']}")
                st.markdown(f"**🤖 AI Assistant:**")
                st.info(chat['answer'])
                st.divider()


