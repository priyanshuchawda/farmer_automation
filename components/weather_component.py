import streamlit as st
from weather.weather_assistant import get_weather_forecast_for_query
from weather.combined_forecast import get_weather_forecast
from database.db_functions import get_farmer_profile
from datetime import datetime

def render_weather_component():
    st.header("🌤️ Weather Forecast & Farming Advice")
    
    # Check if farmer is logged in and has profile
    farmer_name = st.session_state.get("farmer_name")
    if farmer_name:
        farmer_profile = get_farmer_profile(farmer_name)
        
        if farmer_profile and farmer_profile.get('weather_location'):
            # Show farmer's location weather automatically
            st.subheader(f"📍 Your Location: {farmer_profile['weather_location']}")
            
            with st.spinner("Loading weather for your location..."):
                try:
                    forecast = get_weather_forecast(
                        farmer_profile['weather_location'],
                        lat=farmer_profile.get('latitude'),
                        lon=farmer_profile.get('longitude')
                    )
                    
                    if forecast:
                        st.success("✅ 7-Day Weather Forecast")
                        
                        # Display forecast cards
                        cols = st.columns(min(7, len(forecast)))
                        for idx, day in enumerate(forecast[:7]):
                            with cols[idx]:
                                date_obj = day['date'] if isinstance(day['date'], str) else day['date'].strftime('%Y-%m-%d')
                                
                                # Determine if it's today or future
                                is_today = datetime.now().date() == (datetime.strptime(date_obj, '%Y-%m-%d').date() if isinstance(date_obj, str) else date_obj)
                                day_label = "Today" if is_today else date_obj[-5:]
                                
                                st.metric(
                                    day_label,
                                    f"{day['temperature']}°C",
                                    help=f"Rain: {day['rainfall']}mm | Wind: {day['wind_speed']} km/h"
                                )
                                
                                # Weather emoji
                                if day['rainfall'] > 5:
                                    st.write("🌧️")
                                elif day['rainfall'] > 0:
                                    st.write("🌦️")
                                elif day['temperature'] > 30:
                                    st.write("☀️")
                                else:
                                    st.write("⛅")
                        
                        st.divider()
                        
                        # Detailed view for today
                        if forecast:
                            today_weather = forecast[0]
                            st.subheader("📊 Today's Detailed Forecast")
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("🌡️ Temperature", f"{today_weather['temperature']}°C")
                            with col2:
                                st.metric("🌧️ Rainfall", f"{today_weather['rainfall']} mm")
                            with col3:
                                st.metric("💨 Wind Speed", f"{today_weather['wind_speed']} km/h")
                            
                            # Farming advice based on today's weather
                            temp = today_weather['temperature']
                            rain = today_weather['rainfall']
                            
                            st.info("🌾 **Farming Recommendations:**")
                            
                            if rain > 10:
                                st.warning("⚠️ Heavy rain expected today. Postpone outdoor activities and ensure proper drainage.")
                            elif rain > 2:
                                st.info("🌧️ Light rain expected. Good for transplanting, but avoid harvesting.")
                            elif rain == 0 and temp > 30:
                                st.warning("🔥 Hot and dry day. Ensure adequate irrigation, especially for young plants.")
                            elif rain == 0 and temp >= 20 and temp <= 30:
                                st.success("✅ Perfect weather for most farming activities! Good day for planting, harvesting, or field work.")
                            elif temp < 15:
                                st.warning("❄️ Cold weather. Protect sensitive crops and consider mulching.")
                
                except Exception as e:
                    st.error(f"Unable to load weather: {str(e)}")
            
            st.divider()
    
    # AI-powered weather chatbot
    st.subheader("🤖 Ask About Any Location's Weather")
    st.write("Get weather forecasts with personalized farming advice for any location!")

    query = st.text_input(
        "Enter your weather query:",
        placeholder="e.g., 'weather in Mumbai tomorrow', 'temperature in Nashik today'",
        key="weather_query_input"
    )

    if st.button("🔍 Get Forecast", use_container_width=True, type="primary"):
        if query:
            with st.spinner("🌤️ Fetching weather forecast and farming advice..."):
                response = get_weather_forecast_for_query(query)
                
                st.divider()
                st.markdown("### 📋 Weather Report")
                st.write(response)
        else:
            st.warning("⚠️ Please enter a query.")
