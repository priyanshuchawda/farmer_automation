import streamlit as st
from weather.weather_assistant import get_weather_forecast_for_query
from weather.combined_forecast import get_weather_forecast
from weather.api_client import OpenWeatherAPI
from database.db_functions import get_farmer_profile
from datetime import datetime
import pandas as pd

def get_farming_advice(temp, rain, humidity, wind_speed):
    """Generate detailed farming advice based on weather parameters"""
    advice = []
    
    # Temperature based advice
    if temp > 35:
        advice.append("🔥 **Extreme Heat Alert**: Avoid working during peak afternoon hours (12 PM - 4 PM). Ensure irrigation in early morning or evening.")
    elif temp > 30:
        advice.append("☀️ **Hot Weather**: Increase irrigation frequency. Protect young plants with shade nets if available.")
    elif temp < 10:
        advice.append("❄️ **Cold Alert**: Protect sensitive crops with mulching. Delay planting of warm-season crops.")
    elif temp < 15:
        advice.append("🌡️ **Cool Weather**: Good for cool-season crops like wheat, peas, and leafy greens.")
    
    # Rain based advice
    if rain > 20:
        advice.append("⛈️ **Heavy Rain Warning**: Ensure proper drainage. Postpone spraying operations. Protect harvested produce.")
    elif rain > 5:
        advice.append("🌧️ **Moderate Rain Expected**: Good for soil moisture. Avoid harvesting. Delay fertilizer application.")
    elif rain > 0:
        advice.append("🌦️ **Light Rain**: Ideal for transplanting seedlings. Natural irrigation for crops.")
    elif rain == 0 and humidity < 40:
        advice.append("💧 **Dry Conditions**: Monitor soil moisture closely. Increase irrigation for vegetable crops.")
    
    # Humidity based advice
    if humidity > 80 and temp > 25:
        advice.append("🦠 **Disease Risk**: High humidity + warm temperature increases fungal disease risk. Monitor crops closely.")
    elif humidity < 30:
        advice.append("💨 **Low Humidity**: Plants may lose moisture quickly. Check irrigation needs.")
    
    # Wind based advice
    if wind_speed > 40:
        advice.append("💨 **Strong Wind Alert**: Secure structures and shade nets. Delay spraying operations.")
    elif wind_speed > 20:
        advice.append("🌬️ **Moderate Wind**: Not ideal for spraying pesticides/fertilizers.")
    
    return advice if advice else ["✅ **Good Conditions**: Favorable weather for general farming activities."]

def render_weather_component():
    st.header("🌤️ Weather Forecast & Farming Advice")
    
    # Check if farmer is logged in and has profile
    farmer_name = st.session_state.get("farmer_name")
    if farmer_name:
        farmer_profile = get_farmer_profile(farmer_name)
        
        if farmer_profile and farmer_profile.get('weather_location'):
            lat = farmer_profile.get('latitude')
            lon = farmer_profile.get('longitude')
            
            if not lat or not lon:
                st.warning(f"⚠️ Location coordinates not found for '{farmer_profile['weather_location']}'. Please update your profile.")
                return
            
            # Show farmer's location weather automatically
            st.subheader(f"📍 Your Location: {farmer_profile['weather_location']}")
            
            with st.spinner("Loading weather for your location..."):
                try:
                    weather_api = OpenWeatherAPI()
                    detailed_forecast = weather_api.get_detailed_forecast(lat, lon)
                    daily_forecast = get_weather_forecast(
                        farmer_profile['weather_location'],
                        lat=lat,
                        lon=lon
                    )
                    
                    if detailed_forecast is not None and not detailed_forecast.empty:
                        # Get current/today's weather
                        today_df = detailed_forecast[detailed_forecast['date'] == datetime.now().date()]
                        
                        if not today_df.empty:
                            current = today_df.iloc[0]
                            
                            # Current Weather Summary
                            st.markdown("### 🌡️ Current Weather")
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Temperature", f"{current['temp']:.1f}°C", 
                                         delta=f"Feels like {current['feels_like']:.1f}°C")
                            with col2:
                                st.metric("Humidity", f"{current['humidity']}%")
                            with col3:
                                st.metric("Wind Speed", f"{current['wind_speed']:.1f} km/h")
                            with col4:
                                st.metric("Rain Chance", f"{current['pop']:.0f}%")
                            
                            # Weather description
                            st.info(f"☁️ {current['weather_desc'].title()} | Cloud Cover: {current['clouds']}%")
                            
                            # Farming Recommendations
                            st.markdown("### 🌾 Smart Farming Recommendations")
                            advice_list = get_farming_advice(
                                current['temp'], 
                                current['rain'], 
                                current['humidity'], 
                                current['wind_speed']
                            )
                            for advice in advice_list:
                                st.markdown(f"- {advice}")
                            
                            st.divider()
                            
                            # Today's Hourly Forecast
                            st.markdown("### ⏰ Today's Hourly Forecast")
                            st.caption("Plan your farming activities based on hourly weather")
                            
                            # Show next 8 readings (24 hours)
                            hourly_display = today_df.head(8) if len(today_df) >= 8 else today_df
                            
                            cols = st.columns(min(4, len(hourly_display)))
                            for idx, (_, hour) in enumerate(hourly_display.iterrows()):
                                with cols[idx % 4]:
                                    with st.container():
                                        st.markdown(f"**{hour['time']}**")
                                        st.metric("", f"{hour['temp']:.1f}°C")
                                        
                                        # Weather icon emoji
                                        if hour['rain'] > 2:
                                            st.write("🌧️ Rain")
                                        elif hour['pop'] > 50:
                                            st.write("🌦️ Possible Rain")
                                        elif hour['clouds'] > 70:
                                            st.write("☁️ Cloudy")
                                        elif hour['temp'] > 30:
                                            st.write("☀️ Hot")
                                        else:
                                            st.write("⛅ Clear")
                                        
                                        st.caption(f"💧{hour['humidity']}% | 💨{hour['wind_speed']:.0f} km/h")
                            
                            st.divider()
                        
                        # 5-Day Weather Forecast
                        if daily_forecast:
                            st.markdown("### 📅 5-Day Weather Forecast")
                            
                            cols = st.columns(min(5, len(daily_forecast)))
                            for idx, day in enumerate(daily_forecast[:5]):
                                with cols[idx]:
                                    date_obj = day['date'] if isinstance(day['date'], str) else day['date']
                                    is_today = str(date_obj) == str(datetime.now().date())
                                    day_label = "Today" if is_today else datetime.strptime(str(date_obj), '%Y-%m-%d').strftime('%a %d')
                                    
                                    st.markdown(f"**{day_label}**")
                                    st.metric("Temp", f"{day['temperature']:.1f}°C")
                                    
                                    # Weather emoji
                                    if day['rainfall'] > 10:
                                        st.write("⛈️ Heavy Rain")
                                    elif day['rainfall'] > 2:
                                        st.write("🌧️ Rain")
                                    elif day['rainfall'] > 0:
                                        st.write("🌦️ Light Rain")
                                    elif day['temperature'] > 32:
                                        st.write("☀️ Hot")
                                    else:
                                        st.write("⛅ Clear")
                                    
                                    st.caption(f"💧 {day['rainfall']:.1f}mm\n💨 {day['wind_speed']:.1f} km/h")
                            
                            st.divider()
                            
                            # Best farming activities recommendation
                            st.markdown("### 📋 Week Planning Guide")
                            for idx, day in enumerate(daily_forecast[:5]):
                                date_obj = day['date'] if isinstance(day['date'], str) else day['date']
                                day_name = datetime.strptime(str(date_obj), '%Y-%m-%d').strftime('%A, %B %d')
                                
                                with st.expander(f"📆 {day_name}"):
                                    col1, col2 = st.columns([1, 2])
                                    with col1:
                                        st.metric("Temperature", f"{day['temperature']:.1f}°C")
                                        st.metric("Rainfall", f"{day['rainfall']:.1f} mm")
                                        st.metric("Wind", f"{day['wind_speed']:.1f} km/h")
                                    
                                    with col2:
                                        st.markdown("**Recommended Activities:**")
                                        if day['rainfall'] > 10:
                                            st.write("- ❌ Avoid field work")
                                            st.write("- ✅ Equipment maintenance")
                                            st.write("- ✅ Planning and record keeping")
                                        elif day['rainfall'] > 2:
                                            st.write("- ✅ Good day for transplanting")
                                            st.write("- ❌ Postpone harvesting")
                                            st.write("- ❌ Avoid spraying")
                                        elif day['temperature'] > 35:
                                            st.write("- ⏰ Work in early morning/evening")
                                            st.write("- ✅ Irrigation essential")
                                            st.write("- ❌ Avoid transplanting")
                                        else:
                                            st.write("- ✅ Excellent for planting")
                                            st.write("- ✅ Good for harvesting")
                                            st.write("- ✅ Spraying operations OK")
                    
                except Exception as e:
                    st.error(f"Unable to load weather: {str(e)}")
            
            st.divider()
        else:
            st.info("👤 Please update your profile with a location to see weather forecasts.")
    
    # AI-powered weather chatbot
    st.markdown("### 🤖 Ask About Any Location's Weather")
    st.caption("Get weather forecasts with personalized farming advice for any location!")

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


