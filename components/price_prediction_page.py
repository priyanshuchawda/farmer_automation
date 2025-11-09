# components/price_prediction_page.py
"""
AI-Powered Price Prediction Interface
Provides farmers with price predictions, selling advice, and profit calculations
"""

import streamlit as st
from datetime import datetime, timedelta
try:
    from ai.price_predictor import PricePredictor
except ImportError:
    # Fallback if module not found
    PricePredictor = None

def render_price_prediction_page():
    """Render the comprehensive price prediction and analysis page."""
    
    st.header("🤖 AI-Powered Price Intelligence")
    
    # Check if PricePredictor is available
    if PricePredictor is None:
        st.error("⚠️ AI Price Prediction module is not available. Please contact administrator.")
        st.info("💡 The prediction feature requires additional AI components to be installed.")
        return
    
    st.markdown("""
    <div style='background: linear-gradient(135deg, #E8F5E9 0%, #F1F8E9 100%); 
                padding: 20px; border-radius: 12px; margin-bottom: 20px; 
                border-left: 5px solid #4CAF50;'>
        <h4 style='color: #2E8B57; margin: 0;'>🎯 Make Smarter Selling Decisions</h4>
        <p style='margin: 8px 0 0 0; color: #666;'>
            Use AI-powered predictions to maximize your profits. Get insights on when to sell, 
            expected price trends, and profit calculations.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Custom CSS
    st.markdown("""
    <style>
    .prediction-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin: 15px 0;
        border-left: 5px solid #2E8B57;
    }
    .metric-box {
        background: linear-gradient(135deg, #E8F5E9 0%, #F1F8E9 100%);
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
    }
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #2E8B57;
    }
    .metric-label {
        font-size: 14px;
        color: #666;
        margin-top: 5px;
    }
    .trend-up {
        color: #4CAF50;
        font-weight: bold;
    }
    .trend-down {
        color: #F44336;
        font-weight: bold;
    }
    .trend-stable {
        color: #FF9800;
        font-weight: bold;
    }
    .action-sell {
        background: #4CAF50;
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
    .action-wait {
        background: #FF9800;
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
    .action-partial {
        background: #2196F3;
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create tabs for different features
    tab1, tab2, tab3 = st.tabs([
        "📈 Price Prediction",
        "⏰ Best Time to Sell",
        "💰 Profit Calculator"
    ])
    
    # ============================================
    # TAB 1: PRICE PREDICTION
    # ============================================
    with tab1:
        st.subheader("📈 Future Price Prediction")
        st.markdown("Get AI-powered predictions for crop prices over the next 30 days")
        
        col1, col2 = st.columns(2)
        
        with col1:
            crop_name = st.selectbox(
                "Select Crop",
                ["Wheat", "Rice", "Tomato", "Onion", "Potato", "Cotton", "Sugarcane", 
                 "Maize", "Soybean", "Chickpea", "Chili", "Turmeric"],
                key="pred_crop"
            )
        
        with col2:
            current_price = st.number_input(
                "Current Market Price (₹/quintal)",
                min_value=0.0,
                value=2000.0,
                step=100.0,
                key="pred_price"
            )
        
        location = st.text_input(
            "Location (City/District)",
            value="Pune, Maharashtra",
            key="pred_location"
        )
        
        predict_button = st.button("🔮 Predict Future Prices", width="stretch", type="primary")
        
        if predict_button:
            if current_price <= 0:
                st.error("❌ Please enter a valid current price")
            else:
                with st.spinner("🤖 AI is analyzing market trends and generating predictions..."):
                    try:
                        predictor = PricePredictor()
                        prediction = predictor.predict_future_prices(
                            crop_name, current_price, location
                        )
                        
                        if prediction['success']:
                            st.success("✅ Price prediction generated successfully!")
                            
                            # Display Weather Information
                            if prediction.get('weather_data'):
                                weather = prediction['weather_data']
                                st.markdown("### 🌤️ Current Weather Conditions")
                                
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("Temperature", f"{weather['current']['temperature']:.1f}°C")
                                with col2:
                                    st.metric("Humidity", f"{weather['current']['humidity']}%")
                                with col3:
                                    st.metric("Weather", weather['current']['weather'].title())
                                with col4:
                                    st.metric("Wind", f"{weather['current']['wind_speed']} m/s")
                                
                                # Show forecast
                                if weather.get('forecast'):
                                    with st.expander("📅 5-Day Weather Forecast"):
                                        for day in weather['forecast']:
                                            st.markdown(f"**{day['date']}:** {day['temp_min']:.0f}-{day['temp_max']:.0f}°C, {day['weather']}, Rain probability: {day['rain_probability']:.0f}%")
                            
                            # Display Online Market Intelligence
                            if prediction.get('online_data'):
                                online = prediction['online_data']
                                st.markdown("### 🔍 Market Intelligence (Google Search)")
                                
                                if online.get('current_price'):
                                    price_diff = online['current_price'] - current_price
                                    price_diff_pct = (price_diff / current_price * 100) if current_price > 0 else 0
                                    
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.metric("Your Reference Price", f"₹{current_price:.2f}")
                                    with col2:
                                        st.metric("Current Market Price (Online)", f"₹{online['current_price']:.2f}",
                                                delta=f"{price_diff:+.2f} ({price_diff_pct:+.1f}%)")
                                
                                if online.get('full_response'):
                                    with st.expander("📰 View Full Market Report", expanded=True):
                                        st.markdown(online['full_response'])
                                
                                # Show sources with citations
                                if online.get('sources'):
                                    st.markdown("**📚 Information Sources:**")
                                    for i, source in enumerate(online['sources'], 1):
                                        st.markdown(f"{i}. [{source.get('title', 'Source')}]({source.get('url', '#')})")
                                
                                if online.get('search_queries'):
                                    with st.expander("🔍 Search Queries Used"):
                                        for query in online['search_queries']:
                                            st.code(query)
                            
                            st.markdown("---")
                            
                            # Display trend
                            trend = prediction['trend']
                            trend_icon = "📈" if trend == "UPWARD" else "📉" if trend == "DOWNWARD" else "➡️"
                            trend_class = "trend-up" if trend == "UPWARD" else "trend-down" if trend == "DOWNWARD" else "trend-stable"
                            
                            st.markdown(f"""
                            <div class='prediction-card'>
                                <h3>{trend_icon} Overall Trend: <span class='{trend_class}'>{trend}</span></h3>
                                <p><strong>Confidence Level:</strong> {prediction['confidence']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Display predictions
                            st.markdown("### 📊 Price Predictions")
                            col1, col2, col3 = st.columns(3)
                            
                            predictions = prediction['predictions']
                            
                            with col1:
                                day7_price = predictions.get('day_7', current_price)
                                day7_change = ((day7_price - current_price) / current_price * 100) if current_price > 0 else 0
                                change_icon = "↗️" if day7_change > 0 else "↘️" if day7_change < 0 else "→"
                                st.markdown(f"""
                                <div class='metric-box'>
                                    <div class='metric-label'>7 Days Ahead</div>
                                    <div class='metric-value'>₹{day7_price:.2f}</div>
                                    <div style='color: {"green" if day7_change > 0 else "red" if day7_change < 0 else "gray"};'>
                                        {change_icon} {abs(day7_change):.1f}%
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col2:
                                day15_price = predictions.get('day_15', current_price)
                                day15_change = ((day15_price - current_price) / current_price * 100) if current_price > 0 else 0
                                change_icon = "↗️" if day15_change > 0 else "↘️" if day15_change < 0 else "→"
                                st.markdown(f"""
                                <div class='metric-box'>
                                    <div class='metric-label'>15 Days Ahead</div>
                                    <div class='metric-value'>₹{day15_price:.2f}</div>
                                    <div style='color: {"green" if day15_change > 0 else "red" if day15_change < 0 else "gray"};'>
                                        {change_icon} {abs(day15_change):.1f}%
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col3:
                                day30_price = predictions.get('day_30', current_price)
                                day30_change = ((day30_price - current_price) / current_price * 100) if current_price > 0 else 0
                                change_icon = "↗️" if day30_change > 0 else "↘️" if day30_change < 0 else "→"
                                st.markdown(f"""
                                <div class='metric-box'>
                                    <div class='metric-label'>30 Days Ahead</div>
                                    <div class='metric-value'>₹{day30_price:.2f}</div>
                                    <div style='color: {"green" if day30_change > 0 else "red" if day30_change < 0 else "gray"};'>
                                        {change_icon} {abs(day30_change):.1f}%
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            # Peak and Lowest days
                            st.markdown("### 📅 Best and Worst Days")
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                peak_date = (datetime.now() + timedelta(days=prediction['peak_day'])).strftime('%B %d, %Y')
                                st.success(f"🎯 **Best Day to Sell:** Day {prediction['peak_day']} ({peak_date})")
                            
                            with col2:
                                lowest_date = (datetime.now() + timedelta(days=prediction['lowest_day'])).strftime('%B %d, %Y')
                                st.error(f"⚠️ **Lowest Price Expected:** Day {prediction['lowest_day']} ({lowest_date})")
                            
                            # Key factors
                            if prediction['key_factors']:
                                st.markdown("### 🔑 Key Factors Affecting Price")
                                for factor in prediction['key_factors']:
                                    st.markdown(f"- {factor}")
                            
                            # Recommendation
                            if prediction['recommendation']:
                                st.markdown("### 💡 AI Recommendation")
                                st.info(prediction['recommendation'])
                            
                        else:
                            st.error(f"❌ {prediction.get('message', 'Failed to generate prediction')}")
                            if 'error' in prediction:
                                st.error(f"Error details: {prediction['error']}")
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        st.info("💡 Make sure your GOOGLE_API_KEY is set in the .env file")
    
    # ============================================
    # TAB 2: BEST TIME TO SELL
    # ============================================
    with tab2:
        st.subheader("⏰ Best Time to Sell Analysis")
        st.markdown("Find out the optimal time to sell your crop for maximum profit")
        
        col1, col2 = st.columns(2)
        
        with col1:
            crop_name_sell = st.selectbox(
                "Select Crop",
                ["Wheat", "Rice", "Tomato", "Onion", "Potato", "Cotton", "Sugarcane", 
                 "Maize", "Soybean", "Chickpea", "Chili", "Turmeric"],
                key="sell_crop"
            )
        
        with col2:
            current_price_sell = st.number_input(
                "Current Market Price (₹/quintal)",
                min_value=0.0,
                value=2000.0,
                step=100.0,
                key="sell_price"
            )
        
        harvest_date = st.date_input(
            "Expected Harvest Date (Optional)",
            value=None,
            key="harvest_date"
        )
        
        analyze_button = st.button("📊 Analyze Best Selling Time", width="stretch", type="primary")
        
        if analyze_button:
            if current_price_sell <= 0:
                st.error("❌ Please enter a valid current price")
            else:
                with st.spinner("🤖 AI is analyzing market patterns and seasonal trends..."):
                    try:
                        predictor = PricePredictor()
                        advice = predictor.get_best_selling_time(
                            crop_name_sell, 
                            current_price_sell,
                            harvest_date.strftime('%Y-%m-%d') if harvest_date else None
                        )
                        
                        if advice['success']:
                            st.success("✅ Selling time analysis completed!")
                            
                            # Action recommendation
                            action = advice['action']
                            if action == 'SELL_NOW':
                                action_class = 'action-sell'
                                action_text = "🟢 RECOMMENDED: SELL NOW"
                            elif action == 'WAIT_FOR_BETTER_PRICE':
                                action_class = 'action-wait'
                                action_text = "🟡 RECOMMENDED: WAIT FOR BETTER PRICE"
                            else:
                                action_class = 'action-partial'
                                action_text = "🔵 RECOMMENDED: SELL PARTIALLY"
                            
                            st.markdown(f"""
                            <div class='{action_class}'>
                                <h3 style='margin: 0;'>{action_text}</h3>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.markdown("<br>", unsafe_allow_html=True)
                            
                            # Scores
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                sell_now_score = advice['sell_now_score']
                                st.markdown(f"""
                                <div class='metric-box'>
                                    <div class='metric-label'>Sell Now Score</div>
                                    <div class='metric-value'>{sell_now_score}/10</div>
                                    <div style='color: {"green" if sell_now_score >= 7 else "orange" if sell_now_score >= 4 else "red"};'>
                                        {"Strong" if sell_now_score >= 7 else "Moderate" if sell_now_score >= 4 else "Weak"}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col2:
                                wait_score = advice['wait_score']
                                st.markdown(f"""
                                <div class='metric-box'>
                                    <div class='metric-label'>Wait Score</div>
                                    <div class='metric-value'>{wait_score}/10</div>
                                    <div style='color: {"green" if wait_score >= 7 else "orange" if wait_score >= 4 else "red"};'>
                                        {"Strong" if wait_score >= 7 else "Moderate" if wait_score >= 4 else "Weak"}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            # Best month and reason
                            if advice['best_month']:
                                st.markdown("### 📅 Optimal Selling Period")
                                st.success(f"**Best Month:** {advice['best_month']}")
                                if advice['reason']:
                                    st.info(f"**Why:** {advice['reason']}")
                            
                            # Timeline
                            if advice['timeline']:
                                st.markdown("### ⏱️ Recommended Timeline")
                                st.warning(advice['timeline'])
                            
                            # Expected peak price
                            if advice['expected_peak_price'] > 0:
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.metric(
                                        "Current Price",
                                        f"₹{current_price_sell:.2f}",
                                        delta=None
                                    )
                                with col2:
                                    price_increase = advice['expected_peak_price'] - current_price_sell
                                    price_increase_pct = (price_increase / current_price_sell * 100) if current_price_sell > 0 else 0
                                    st.metric(
                                        "Expected Peak Price",
                                        f"₹{advice['expected_peak_price']:.2f}",
                                        delta=f"+₹{price_increase:.2f} (+{price_increase_pct:.1f}%)"
                                    )
                            
                            # Storage advice
                            if advice['storage_advice']:
                                st.markdown("### 📦 Storage Advice")
                                st.info(advice['storage_advice'])
                            
                            # Risk factors
                            if advice['risk_factors']:
                                st.markdown("### ⚠️ Risk Factors to Consider")
                                for risk in advice['risk_factors']:
                                    st.markdown(f"- {risk}")
                        
                        else:
                            st.error(f"❌ {advice.get('message', 'Failed to generate advice')}")
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        st.info("💡 Make sure your GOOGLE_API_KEY is set in the .env file")
    
    # ============================================
    # TAB 3: PROFIT CALCULATOR
    # ============================================
    with tab3:
        st.subheader("💰 Profit/Loss Calculator")
        st.markdown("Compare your expected vs actual selling prices and analyze the outcome")
        
        col1, col2 = st.columns(2)
        
        with col1:
            crop_name_calc = st.selectbox(
                "Select Crop",
                ["Wheat", "Rice", "Tomato", "Onion", "Potato", "Cotton", "Sugarcane", 
                 "Maize", "Soybean", "Chickpea", "Chili", "Turmeric"],
                key="calc_crop"
            )
            
            expected_price = st.number_input(
                "Expected Price (₹/quintal)",
                min_value=0.0,
                value=2000.0,
                step=100.0,
                key="expected_price"
            )
            
            quantity = st.number_input(
                "Quantity Sold",
                min_value=0.0,
                value=10.0,
                step=1.0,
                key="quantity"
            )
        
        with col2:
            unit = st.selectbox(
                "Unit",
                ["quintal", "kg", "ton"],
                key="unit"
            )
            
            actual_price = st.number_input(
                "Actual Selling Price (₹/unit)",
                min_value=0.0,
                value=2200.0,
                step=100.0,
                key="actual_price"
            )
        
        calculate_button = st.button("🧮 Calculate Profit/Loss", width="stretch", type="primary")
        
        if calculate_button:
            if expected_price <= 0 or actual_price <= 0 or quantity <= 0:
                st.error("❌ Please enter valid values for all fields")
            else:
                with st.spinner("🤖 AI is analyzing your transaction..."):
                    try:
                        predictor = PricePredictor()
                        result = predictor.calculate_profit(
                            crop_name_calc,
                            expected_price,
                            actual_price,
                            quantity,
                            unit
                        )
                        
                        if result['success']:
                            # Verdict display
                            verdict = result['verdict']
                            if 'GOOD' in verdict:
                                verdict_color = '#4CAF50'
                                verdict_icon = '✅'
                            elif 'FAIR' in verdict:
                                verdict_color = '#FF9800'
                                verdict_icon = '👍'
                            elif 'POOR' in verdict:
                                verdict_color = '#FF5722'
                                verdict_icon = '⚠️'
                            else:
                                verdict_color = '#F44336'
                                verdict_icon = '❌'
                            
                            st.markdown(f"""
                            <div style='background: {verdict_color}; color: white; padding: 20px; 
                                        border-radius: 12px; text-align: center; margin: 20px 0;'>
                                <h2 style='margin: 0; color: white;'>{verdict_icon} {verdict.replace('_', ' ')}</h2>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Financial summary
                            st.markdown("### 💵 Financial Summary")
                            
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.markdown(f"""
                                <div class='metric-box'>
                                    <div class='metric-label'>Expected Revenue</div>
                                    <div class='metric-value'>₹{result['expected_revenue']:,.2f}</div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col2:
                                st.markdown(f"""
                                <div class='metric-box'>
                                    <div class='metric-label'>Actual Revenue</div>
                                    <div class='metric-value'>₹{result['actual_revenue']:,.2f}</div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col3:
                                profit_color = "green" if result['profit_loss'] >= 0 else "red"
                                profit_icon = "↗️" if result['profit_loss'] >= 0 else "↘️"
                                st.markdown(f"""
                                <div class='metric-box'>
                                    <div class='metric-label'>Profit/Loss</div>
                                    <div class='metric-value' style='color: {profit_color};'>
                                        {profit_icon} ₹{abs(result['profit_loss']):,.2f}
                                    </div>
                                    <div style='color: {profit_color};'>
                                        {result['profit_percentage']:+.2f}%
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            # AI Analysis
                            if result['analysis']:
                                st.markdown("### 🤖 AI Analysis")
                                st.info(result['analysis'])
                            
                            # Market context
                            if result['market_context']:
                                st.markdown("### 📊 Market Context")
                                st.warning(result['market_context'])
                            
                            # Learning point
                            if result['learning']:
                                st.markdown("### 💡 Key Takeaway")
                                st.success(result['learning'])
                        
                        else:
                            st.error("❌ Failed to calculate profit")
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        st.info("💡 Make sure your GOOGLE_API_KEY is set in the .env file")


