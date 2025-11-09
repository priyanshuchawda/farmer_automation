import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List, Optional
from weather.config import get_gemini_api_key
import re

load_dotenv()

class WeatherQuery(BaseModel):
    city: str = Field(description="The city for which the weather is being requested.")
    date: Optional[str] = Field(description="The date for which the weather is being requested. It can be 'today', 'tomorrow', or a specific date.")
    info_type: str = Field(description="The type of weather information requested, e.g., 'temperature', 'rain', 'wind', or 'all'.")


class AIClient:
    def __init__(self):
        self.api_key = get_gemini_api_key()
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set in the .env file.")
        
        try:
            self.client = genai.Client(api_key=self.api_key)
        except Exception as e:
            raise Exception(f"Failed to initialize AI client. Error: {e}")

    def get_farmer_advice(self, weather_data: str, location: str) -> str:
        """
        Get farmer-specific advice based on weather data using AI AI.
        """
        prompt = f"""
        You are an agricultural advisor helping farmers in India. Based on the following weather forecast, 
        provide practical farming advice in a friendly, conversational tone.
        
        Location: {location}
        Weather Data: {weather_data}
        
        Please provide:
        1. A brief summary of the weather conditions
        2. Specific farming recommendations (irrigation, pest control, harvesting, planting, etc.)
        3. Any warnings or precautions farmers should take
        4. Best activities for the day based on weather
        
        Keep the response concise (4-6 sentences), practical, and farmer-friendly.
        Use simple language and include relevant emojis to make it engaging.
        Focus on actionable advice that helps farmers make decisions.
        """
        
        models_to_try = ["AI-2.0-flash-exp", "AI-2.5-flash", "AI-2.0-flash"]
        
        for model in models_to_try:
            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=prompt
                )
                return response.text
            except Exception as e:
                print(f"Error getting farmer advice with {model}: {e}")
                continue
        
        return "Unable to generate farming advice at this time."

    def get_coordinates_from_google_search(self, location: str) -> Optional[dict]:
        """
        Uses AI with Google Search to find the latitude and longitude of a given location.
        """
        prompt = f"""Find the GPS coordinates for: {location}

IMPORTANT: You MUST respond in EXACTLY this format, nothing else:
LAT: [latitude]
LON: [longitude]

Example response format:
LAT: 18.553516
LON: 73.930104

Do not add any explanations, notes, or additional text. Just the two lines above."""
        
        models_to_try = ["AI-2.5-flash", "AI-2.0-flash", "AI-1.5-flash"]
        
        for model in models_to_try:
            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        tools=[types.Tool(google_search=types.GoogleSearch())]
                    ),
                )
                
                text = response.text.strip()
                print(f"AI response for '{location}': {text}")
                
                # Primary: Try to extract from strict format LAT: X LON: Y
                lat_match = re.search(r"LAT:\s*(-?\d+\.?\d+)", text, re.IGNORECASE)
                lon_match = re.search(r"LON:\s*(-?\d+\.?\d+)", text, re.IGNORECASE)
                
                if lat_match and lon_match:
                    lat = float(lat_match.group(1))
                    lon = float(lon_match.group(1))
                    print(f"✅ Extracted coordinates: LAT={lat}, LON={lon}")
                    return {"lat": lat, "lon": lon}
                
                # Fallback: Try latitude/longitude format
                lat_match = re.search(r"(?:latitude|lat)[\s:]+(-?\d+\.?\d+)", text, re.IGNORECASE)
                lon_match = re.search(r"(?:longitude|lon|long)[\s:]+(-?\d+\.?\d+)", text, re.IGNORECASE)
                
                if lat_match and lon_match:
                    lat = float(lat_match.group(1))
                    lon = float(lon_match.group(1))
                    print(f"✅ Extracted coordinates (fallback): LAT={lat}, LON={lon}")
                    return {"lat": lat, "lon": lon}
                
                # Additional fallback: "are X and Y" format
                coords_are_match = re.search(r"are\s+(-?\d+\.?\d+)\s+and\s+(-?\d+\.?\d+)", text, re.IGNORECASE)
                if coords_are_match:
                    lat = float(coords_are_match.group(1))
                    lon = float(coords_are_match.group(2))
                    print(f"✅ Extracted coordinates (are/and): LAT={lat}, LON={lon}")
                    return {"lat": lat, "lon": lon}
                
                # Fallback: Two comma-separated floats
                coords_match = re.search(r"(-?\d+\.?\d+)\s*,\s*(-?\d+\.?\d+)", text)
                if coords_match:
                    lat = float(coords_match.group(1))
                    lon = float(coords_match.group(2))
                    print(f"✅ Extracted coordinates (comma): LAT={lat}, LON={lon}")
                    return {"lat": lat, "lon": lon}

                print(f"❌ Could not extract coordinates from AI response for {location}: {text}")
                return None
            except Exception as e:
                print(f"Error getting coordinates with {model} and Google Search for {location}: {e}")
                continue
        return None

    def get_location_from_coordinates(self, latitude: float, longitude: float) -> Optional[dict]:
        """
        Get location information (city, state, country) from GPS coordinates using AI.
        """
        prompt = f"""Find the location name for these GPS coordinates:
Latitude: {latitude}
Longitude: {longitude}

IMPORTANT: You MUST respond in EXACTLY this format, one item per line:
City: [city name]
State: [state/province name]
Country: [country name]
Address: [full address]

Example response:
City: Wadgaonsheri
State: Maharashtra
Country: India
Address: Wadgaonsheri, Pune, Maharashtra, India

Do not add any explanations or additional text."""
        
        models_to_try = ["AI-2.5-flash", "AI-2.0-flash", "AI-1.5-flash"]
        
        for model in models_to_try:
            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=prompt
                )
                
                text = response.text.strip()
                
                # Parse the response
                location_info = {}
                for line in text.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip().lower().replace(' ', '_').replace('/', '_')
                        location_info[key] = value.strip()
                
                return location_info
                
            except Exception as e:
                print(f"Error getting location from coordinates with {model}: {e}")
                continue
        
        return None

    def parse_weather_query(self, query: str) -> Optional[WeatherQuery]:
        """
        Uses the AI API to parse a weather query and extract structured information.
        """
        prompt = f"""
        Please extract the weather query from the following text.
        The user wants to know the weather.
        The query is: "{query}"
        
        For the date field:
        - Use "today" for today
        - Use "tomorrow" for tomorrow
        - For specific dates like "10th nov" or "November 10", convert to YYYY-MM-DD format (use current year if not specified, and assume November 2025 for testing purposes if year is not specified).
        - If no date is mentioned, use "today"
        
        For info_type:
        - Use "temperature" if asking about temperature/temp
        - Use "rain" if asking about rain/rainfall/precipitation
        - Use "wind" if asking about wind
        - Use "all" for general weather queries
        """
        
        models_to_try = ["AI-2.5-flash", "AI-2.0-flash"]
        
        for model in models_to_try:
            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config={
                        "response_mime_type": "application/json",
                        "response_json_schema": WeatherQuery.model_json_schema(),
                    },
                )
                recipe = WeatherQuery.model_validate_json(response.text)
                return recipe
            except Exception as e:
                print(f"Error parsing weather query with {model}: {e}")
                continue
        
        return None


