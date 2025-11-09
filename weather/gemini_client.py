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


class GeminiClient:
    def __init__(self):
        self.api_key = get_gemini_api_key()
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set in the .env file.")
        
        try:
            self.client = genai.Client(api_key=self.api_key)
        except Exception as e:
            raise Exception(f"Failed to initialize Gemini client. Error: {e}")

    def get_farmer_advice(self, weather_data: str, location: str) -> str:
        """
        Get farmer-specific advice based on weather data using Gemini AI.
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
        
        models_to_try = ["gemini-2.0-flash-exp", "gemini-2.5-flash", "gemini-2.0-flash"]
        
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
        Uses Gemini with Google Search to find the latitude and longitude of a given location.
        """
        prompt = f"What are the latitude and longitude of {location}? Provide only the numerical coordinates in decimal format (e.g., 19.0760, 72.8777)."
        
        models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash"]
        
        for model in models_to_try:
            try:
                response = self.client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        tools=[types.Tool(google_search=types.GoogleSearch())]
                    ),
                )
                
                text = response.text
                print(f"Gemini response for '{location}': {text}")
                
                # Try to find two comma-separated floats (e.g., "19.0760, 72.8777")
                coords_match = re.search(r"(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)", text)
                if coords_match:
                    lat = float(coords_match.group(1))
                    lon = float(coords_match.group(2))
                    return {"lat": lat, "lon": lon}
                
                # Try to find latitude and longitude with labels (e.g., "latitude: 19.0760, longitude: 72.8777")
                lat_match = re.search(r"(?:latitude|lat)[\s:]+(-?\d+\.?\d*)", text, re.IGNORECASE)
                lon_match = re.search(r"(?:longitude|lon|long)[\s:]+(-?\d+\.?\d*)", text, re.IGNORECASE)
                
                if lat_match and lon_match:
                    return {"lat": float(lat_match.group(1)), "lon": float(lon_match.group(1))}
                
                # Try to find coordinates in parentheses (e.g., "(19.0760, 72.8777)")
                coords_paren = re.search(r"\((-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\)", text)
                if coords_paren:
                    lat = float(coords_paren.group(1))
                    lon = float(coords_paren.group(2))
                    return {"lat": lat, "lon": lon}
                
                # Handle degrees with decimals and directions (e.g., "19.0760° N, 72.8777° E")
                dms_lat_match = re.search(r"(-?\d+\.?\d*)°?\s*([NS])", text, re.IGNORECASE)
                dms_lon_match = re.search(r"(-?\d+\.?\d*)°?\s*([EW])", text, re.IGNORECASE)

                if dms_lat_match and dms_lon_match:
                    lat_val = float(dms_lat_match.group(1))
                    lat_dir = dms_lat_match.group(2).upper()
                    lon_val = float(dms_lon_match.group(1))
                    lon_dir = dms_lon_match.group(2).upper()

                    lat = lat_val if lat_dir == 'N' else -lat_val
                    lon = lon_val if lon_dir == 'E' else -lon_val
                    return {"lat": lat, "lon": lon}

                print(f"Could not extract coordinates from Gemini response for {location}: {text}")
                return None
            except Exception as e:
                print(f"Error getting coordinates with {model} and Google Search for {location}: {e}")
                continue
        return None

    def parse_weather_query(self, query: str) -> Optional[WeatherQuery]:
        """
        Uses the Gemini API to parse a weather query and extract structured information.
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
        
        models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash"]
        
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
