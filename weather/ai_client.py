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

class LocationInfo(BaseModel):
    """Structured location information from GPS coordinates"""
    city: str = Field(description="City, village, or town name")
    state: str = Field(description="State or province name")
    country: str = Field(description="Country name")
    full_address: str = Field(description="Complete human-readable address")


class AIClient:
    def __init__(self):
        self.api_key = get_gemini_api_key()
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set in the .env file.")
        
        try:
            self.client = genai.Client(api_key=self.api_key)
        except Exception as e:
            raise Exception(f"Failed to initialize AI client. Error: {e}")
    
    def get_language_instruction(self):
        """Get language instruction based on selected language"""
        try:
            import streamlit as st
            selected_lang = st.session_state.get('language', 'English')
            
            language_map = {
                "English": "English",
                "हिन्दी (Hindi)": "Hindi (हिन्दी)",
                "मराठी (Marathi)": "Marathi (मराठी)"
            }
            
            target_language = language_map.get(selected_lang, "English")
            
            if target_language != "English":
                return f"\n\nIMPORTANT: Reply ONLY in {target_language} language. Do not use English."
            return ""
        except:
            return ""

    def get_farmer_advice(self, weather_data: str, location: str) -> str:
        """
        Get farmer-specific advice based on weather data using AI AI.
        """
        language_instruction = self.get_language_instruction()
        
        prompt = f"""You are an expert agricultural advisor for Indian farmers. Provide weather-based farming advice following this EXACT structure:

📍 Location: {location}
{weather_data}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌾 FARMING RECOMMENDATIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Provide advice in these categories (use relevant ones based on weather):

💧 IRRIGATION:
• Specific water management advice based on rainfall and temperature

🌱 CROP MANAGEMENT:
• Suitable activities: planting, transplanting, harvesting, or field preparation
• Crop protection measures if needed

🐛 PEST & DISEASE CONTROL:
• Weather-related pest/disease risks (if any)
• Preventive or control measures

⚠️ IMPORTANT PRECAUTIONS:
• Any weather-related warnings or urgent actions needed

📋 TODAY'S PRIORITY TASKS:
• 2-3 most important activities farmers should focus on today

GUIDELINES:
- Be professional yet friendly
- Use bullet points for clarity
- Include specific, actionable steps
- Mention crop-specific advice when relevant
- Keep advice practical for small to medium farmers
- Use emojis sparingly but effectively
- Total response: 6-8 concise points{language_instruction}"""
        
        models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
        
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
        Uses Gemini with Google Maps Grounding to find GPS coordinates for any location.
        Two-step approach: 1) Find location with Google Maps, 2) Get coordinates
        """
        models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash"]
        
        for model in models_to_try:
            try:
                # Step 1: Use Google Maps to find and verify the location
                search_prompt = f"""Search for this location on Google Maps: {location}

Provide the complete address including city, state, and country."""
                
                maps_response = self.client.models.generate_content(
                    model=model,
                    contents=search_prompt,
                    config=types.GenerateContentConfig(
                        tools=[types.Tool(google_maps=types.GoogleMaps())]
                    ),
                )
                
                found_location = maps_response.text.strip()
                print(f"✅ Google Maps found: '{found_location}' for '{location}'")
                
                # Step 2: Now ask for coordinates of the verified location
                coords_prompt = f"""What are the GPS coordinates (latitude and longitude) for: {found_location}

Provide ONLY the numbers in this format:
latitude, longitude

Example: 18.553516, 73.930104"""
                
                coords_response = self.client.models.generate_content(
                    model=model,
                    contents=coords_prompt,
                )
                
                coords_text = coords_response.text.strip()
                print(f"📍 Coordinates response: {coords_text}")
                
                # Extract coordinates - look for two decimal numbers
                coords_match = re.search(r'(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)', coords_text)
                if coords_match:
                    lat = float(coords_match.group(1))
                    lon = float(coords_match.group(2))
                    
                    # Validate coordinates are reasonable (roughly India region)
                    if 6 <= lat <= 38 and 68 <= lon <= 98:
                        print(f"✅ Extracted and validated coordinates: {lat}, {lon}")
                        return {"lat": lat, "lon": lon}
                    else:
                        print(f"⚠️ Coordinates out of expected range: {lat}, {lon}")
                
                # Try alternative patterns
                numbers = re.findall(r'-?\d+\.\d+', coords_text)
                if len(numbers) >= 2:
                    lat = float(numbers[0])
                    lon = float(numbers[1])
                    if 6 <= lat <= 38 and 68 <= lon <= 98:
                        print(f"✅ Extracted coordinates from list: {lat}, {lon}")
                        return {"lat": lat, "lon": lon}
                
                print(f"⚠️ Could not extract valid coordinates from: {coords_text}")
                
            except Exception as e:
                print(f"❌ Error with {model} for '{location}': {e}")
                continue
        
        return None

    def get_location_from_coordinates(self, latitude: float, longitude: float) -> Optional[dict]:
        """
        Get location information (city, state, country) from GPS coordinates using Google Maps Grounding.
        This provides accurate, real-world address information with structured output.
        """
        # Step 1: Get address from Google Maps Grounding
        prompt = f"""Find the nearest location or address for these GPS coordinates: {latitude}, {longitude}
Provide the city, state/province, and country."""
        
        models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash"]
        
        for model in models_to_try:
            try:
                # First call: Get address with Google Maps Grounding
                maps_response = self.client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        tools=[types.Tool(google_maps=types.GoogleMaps())],
                        tool_config=types.ToolConfig(
                            retrieval_config=types.RetrievalConfig(
                                lat_lng=types.LatLng(
                                    latitude=latitude,
                                    longitude=longitude
                                )
                            )
                        ),
                    ),
                )
                
                address_text = maps_response.text.strip()
                print(f"✅ Google Maps response: {address_text}")
                
                # Step 2: Parse the address into structured format
                structure_prompt = f"""Extract location details from this address: "{address_text}"

Provide structured information."""
                
                structured_response = self.client.models.generate_content(
                    model=model,
                    contents=structure_prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_json_schema=LocationInfo.model_json_schema(),
                    ),
                )
                
                # Parse the structured JSON response
                location_data = LocationInfo.model_validate_json(structured_response.text)
                
                print(f"✅ Structured location: {location_data.city}, {location_data.state}, {location_data.country}")
                
                # Convert to dict for compatibility
                location_info = {
                    'city': location_data.city,
                    'state': location_data.state,
                    'country': location_data.country,
                    'address': location_data.full_address,
                    'latitude': latitude,
                    'longitude': longitude
                }
                
                # Check if we have grounding metadata with sources
                if hasattr(maps_response, 'candidates') and len(maps_response.candidates) > 0:
                    candidate = maps_response.candidates[0]
                    if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                        grounding = candidate.grounding_metadata
                        if hasattr(grounding, 'grounding_chunks') and grounding.grounding_chunks:
                            # Get the first place from grounding chunks
                            first_chunk = grounding.grounding_chunks[0]
                            if hasattr(first_chunk, 'maps'):
                                location_info['place_name'] = first_chunk.maps.title
                                location_info['place_id'] = first_chunk.maps.place_id
                                location_info['maps_uri'] = first_chunk.maps.uri
                
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


