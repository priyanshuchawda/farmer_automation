from datetime import datetime, timedelta
from weather.combined_forecast import get_weather_forecast
from weather.gemini_client import GeminiClient, WeatherQuery

def format_weather_response(weather_data, query_info: WeatherQuery, gemini_client):
    """Format weather data into a natural language response with farmer advice"""
    date_str = weather_data['date'].strftime('%Y-%m-%d')
    temp = weather_data['temperature']
    rain = weather_data['rainfall']
    wind = weather_data['wind_speed']
    
    # Create basic weather summary
    weather_summary = (
        f"📍 Location: {query_info.city}\n"
        f"📅 Date: {date_str}\n\n"
        f"Weather Conditions:\n"
        f"🌡️ Temperature: {temp}°C\n"
        f"🌧️ Rainfall: {rain}mm\n"
        f"💨 Wind Speed: {wind} km/h\n"
    )
    
    # Get farmer-specific advice from Gemini
    try:
        farming_advice = gemini_client.get_farmer_advice(
            weather_data=f"Temperature: {temp}°C, Rainfall: {rain}mm, Wind Speed: {wind} km/h on {date_str}",
            location=query_info.city
        )
        response = f"{weather_summary}\n{'='*50}\n🌾 Farming Advice:\n{'='*50}\n{farming_advice}"
    except Exception as e:
        print(f"Error getting farming advice: {e}")
        # Fallback to basic response
        response = f"{weather_summary}\n{'='*50}\n"
        if query_info.info_type == 'temperature':
            response += f"{'🌞 Pleasant day!' if 20 <= temp <= 28 else '🔥 Quite warm!' if temp > 28 else '❄️ Bit cool!'}"
        elif query_info.info_type == 'rain':
            response += f"{'☔ Carry an umbrella!' if rain > 2 else '🌂 Light rain possible.' if rain > 0 else '☀️ No rain expected.'}"
        else:
            response += f"Summary: {'🌞' if temp > 25 else '⛅'} {'☔' if rain > 2 else '🌂' if rain > 0 else '☀️'} {'🌪️' if wind > 20 else '🍃'}"
    
    return response

def get_weather_forecast_for_query(query):
    """Main function to handle weather queries"""
    # Parse the query using Gemini
    gemini_client = GeminiClient()
    query_info = gemini_client.parse_weather_query(query)

    if not query_info:
        return "Sorry, I couldn't understand your query. Please try again."

    # Get current date and check if we need to update our model
    current_date = datetime.now()
    try:
        import os
        weather_dir = os.path.dirname(os.path.abspath(__file__))
        last_update_path = os.path.join(weather_dir, 'last_update.txt')
        with open(last_update_path, 'r') as f:
            last_update = datetime.strptime(f.read().strip(), '%Y-%m-%d')
        days_since_update = (current_date.date() - last_update.date()).days
    except:
        days_since_update = float('inf')
    
    # If data is more than 7 days old, notify user
    if days_since_update > 7:
        print("\nNote: Weather data needs updating. Predictions may be less accurate.")
    
    # Get combined forecast
    coordinates = None
    if query_info.city.lower() != "pune":
        print(f"Searching for coordinates for {query_info.city} using Google Search...")
        coordinates = gemini_client.get_coordinates_from_google_search(query_info.city)
        if not coordinates:
            return f"Sorry, I couldn't find coordinates for {query_info.city}."
        
    combined_forecast = get_weather_forecast(query_info.city, lat=coordinates['lat'] if coordinates else None, lon=coordinates['lon'] if coordinates else None)
    
    if not combined_forecast:
        return "Sorry, I couldn't get the weather forecast for that location."

    # Get forecast for requested date
    if query_info.date:
        if query_info.date.lower() == 'today':
            target_date = datetime.now().date()
        elif query_info.date.lower() == 'tomorrow':
            target_date = datetime.now().date() + timedelta(days=1)
        else:
            try:
                target_date = datetime.strptime(query_info.date, '%Y-%m-%d').date()
            except ValueError:
                return "Sorry, I couldn't understand the date in your query."
    else:
        target_date = datetime.now().date()

    forecast = None
    for day in combined_forecast:
        if isinstance(day['date'], str):
            day['date'] = datetime.strptime(day['date'], '%Y-%m-%d').date()

        if isinstance(day['date'], datetime):
            compare_date = day['date'].date()
        else:
            compare_date = day['date']
            
        if compare_date == target_date:
            forecast = day
            break
    
    if not forecast:
        return "मैं केवल अगले 5-7 दिनों का मौसम बता सकता हूं। (I can only provide forecasts for the next 5-7 days.)"
    
    # Format response with farmer advice
    response = format_weather_response(forecast, query_info, gemini_client)
    return response

def main():
    print("पुणे का मौसम जानने के लिए स्वागत है! (Welcome to Pune Weather Assistant!)")
    print("आप किसी भी भाषा में पूछ सकते हैं। (You can ask in any language.)")
    print("Testing with the following queries:\n")
    
    # Test cases - add or modify queries here
    test_queries = [
        "what is the weather in Mumbai tomorrow"
    ]

    query = test_queries[0]
    print(f"\n--- Testing query: '{query}' ---")
    try:
        response = get_weather_forecast_for_query(query)
        print("\n" + response + "\n")
        print("-" * 50)
    except Exception as e:
        print(f"\nSorry, there was an error: {str(e)}")
        print("Please try again with a different question.\n")

if __name__ == "__main__":
    main()
