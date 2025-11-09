# components/location_manager.py
"""
Location Management System with Google Maps Grounding
Handles GPS coordinates, location storage, and Google Maps integration
"""

import streamlit as st
from google import genai
from google.genai import types
from database.db_functions import update_farmer_location
from weather.config import get_gemini_api_key
import re
from typing import Optional, Dict, Tuple

class LocationManager:
    def __init__(self):
        self.api_key = get_gemini_api_key()
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set in the .env file.")
        
        try:
            self.client = genai.Client(api_key=self.api_key)
        except Exception as e:
            raise Exception(f"Failed to initialize AI client. Error: {e}")
    
    def get_coordinates_from_location(self, location: str) -> Optional[Dict[str, float]]:
        """
        Get GPS coordinates from location name using Gemini with Google Search
        """
        prompt = f"""Find the GPS coordinates for: {location}

IMPORTANT: You MUST respond in EXACTLY this format, nothing else:
LAT: [latitude]
LON: [longitude]

Example response format:
LAT: 18.553516
LON: 73.930104

Do not add any explanations, notes, or additional text. Just the two lines above."""
        
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
                
                text = response.text.strip()
                print(f"Gemini response for '{location}': {text}")
                
                lat_match = re.search(r"LAT:\s*(-?\d+\.?\d+)", text, re.IGNORECASE)
                lon_match = re.search(r"LON:\s*(-?\d+\.?\d+)", text, re.IGNORECASE)
                
                if lat_match and lon_match:
                    lat = float(lat_match.group(1))
                    lon = float(lon_match.group(1))
                    return {"lat": lat, "lon": lon}
                
                # Fallback patterns
                lat_match = re.search(r"(?:latitude|lat)[\s:]+(-?\d+\.?\d+)", text, re.IGNORECASE)
                lon_match = re.search(r"(?:longitude|lon|long)[\s:]+(-?\d+\.?\d+)", text, re.IGNORECASE)
                
                if lat_match and lon_match:
                    lat = float(lat_match.group(1))
                    lon = float(lon_match.group(1))
                    return {"lat": lat, "lon": lon}
                    
            except Exception as e:
                print(f"Error getting coordinates with {model}: {e}")
                continue
        
        return None
    
    def get_address_from_coordinates(self, latitude: float, longitude: float) -> Optional[Dict[str, str]]:
        """
        Get full address from GPS coordinates using Gemini with Google Maps Grounding
        """
        prompt = f"""What is the complete address and location details for these GPS coordinates?
Latitude: {latitude}
Longitude: {longitude}

Please provide:
- Full address
- City
- State/Province
- Country
- Postal code (if available)
- Nearby landmarks"""
        
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_maps=types.GoogleMaps())],
                    tool_config=types.ToolConfig(
                        retrieval_config=types.RetrievalConfig(
                            lat_lng=types.LatLng(latitude=latitude, longitude=longitude)
                        )
                    ),
                ),
            )
            
            address_info = {
                'full_address': response.text.strip(),
                'latitude': latitude,
                'longitude': longitude
            }
            
            # Check for grounding metadata
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'grounding_metadata'):
                    grounding = candidate.grounding_metadata
                    if hasattr(grounding, 'grounding_chunks') and grounding.grounding_chunks:
                        address_info['sources'] = []
                        for chunk in grounding.grounding_chunks:
                            if hasattr(chunk, 'maps'):
                                address_info['sources'].append({
                                    'title': chunk.maps.title,
                                    'uri': chunk.maps.uri,
                                    'place_id': chunk.maps.place_id if hasattr(chunk.maps, 'place_id') else None
                                })
            
            return address_info
            
        except Exception as e:
            print(f"Error getting address from coordinates: {e}")
            return None
    
    def find_nearby_places(self, latitude: float, longitude: float, query: str) -> Optional[str]:
        """
        Find nearby places using Google Maps Grounding
        Example queries: "restaurants near here", "hospitals nearby", "markets within 2km"
        """
        prompt = f"""{query}

Current location coordinates: {latitude}, {longitude}

Please provide:
1. List of relevant places
2. Distance from current location
3. Ratings and reviews
4. Opening hours if available
5. Contact information"""
        
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_maps=types.GoogleMaps(enable_widget=True))],
                    tool_config=types.ToolConfig(
                        retrieval_config=types.RetrievalConfig(
                            lat_lng=types.LatLng(latitude=latitude, longitude=longitude)
                        )
                    ),
                ),
            )
            
            result = {
                'text': response.text,
                'sources': [],
                'widget_token': None
            }
            
            # Extract grounding metadata
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'grounding_metadata'):
                    grounding = candidate.grounding_metadata
                    
                    if hasattr(grounding, 'grounding_chunks') and grounding.grounding_chunks:
                        for chunk in grounding.grounding_chunks:
                            if hasattr(chunk, 'maps'):
                                result['sources'].append({
                                    'title': chunk.maps.title,
                                    'uri': chunk.maps.uri,
                                    'place_id': chunk.maps.place_id if hasattr(chunk.maps, 'place_id') else None
                                })
                    
                    if hasattr(grounding, 'google_maps_widget_context_token'):
                        result['widget_token'] = grounding.google_maps_widget_context_token
            
            return result
            
        except Exception as e:
            print(f"Error finding nearby places: {e}")
            return None
    
    def get_location_aware_recommendations(self, latitude: float, longitude: float, 
                                          user_preferences: str) -> Optional[str]:
        """
        Get personalized recommendations based on user location and preferences
        using Google Maps Grounding
        """
        prompt = f"""{user_preferences}

Based on my location at coordinates: {latitude}, {longitude}

Please provide personalized recommendations considering:
1. Proximity to my location
2. Quality ratings and reviews
3. Current availability
4. Practical information (hours, contact, etc.)"""
        
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_maps=types.GoogleMaps())],
                    tool_config=types.ToolConfig(
                        retrieval_config=types.RetrievalConfig(
                            lat_lng=types.LatLng(latitude=latitude, longitude=longitude)
                        )
                    ),
                ),
            )
            
            return response.text
            
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return None


def render_location_setup(farmer_name: str, current_location: Optional[str] = None, 
                         current_lat: Optional[float] = None, 
                         current_lon: Optional[float] = None):
    """
    Render location setup UI for user profile
    """
    st.subheader("📍 Location Settings")
    
    st.markdown("""
    <div style='background-color:#FFF3CD;padding:15px;border-radius:10px;margin-bottom:20px;border-left:4px solid #FFC107;'>
        <strong>🗺️ Location Information</strong><br>
        <small>💡 Set your location once and use it for weather, market prices, and personalized recommendations.</small>
    </div>
    """, unsafe_allow_html=True)
    
    if current_lat and current_lon:
        st.success(f"✅ Current Location: {current_location or 'Set'}")
        st.info(f"📍 Coordinates: {current_lat:.6f}, {current_lon:.6f}")
        
        if st.button("🔄 Update Location", width="stretch"):
            st.session_state['update_location'] = True
    
    if not current_lat or not current_lon or st.session_state.get('update_location', False):
        st.markdown("---")
        
        location_method = st.radio(
            "Choose how to set your location:",
            ["📝 Enter Location Name", "🌐 Use GPS Coordinates", "🧭 Use Browser GPS (Coming Soon)"],
            horizontal=True
        )
        
        if location_method == "📝 Enter Location Name":
            location_input = st.text_input(
                "Enter your location",
                placeholder="e.g., Wadgaon Sheri, Pune, Maharashtra",
                help="Enter your village, city, or detailed address"
            )
            
            if st.button("🔍 Find Coordinates", width="stretch"):
                if location_input:
                    with st.spinner("🔍 Finding coordinates..."):
                        location_manager = LocationManager()
                        coords = location_manager.get_coordinates_from_location(location_input)
                        
                        if coords:
                            st.success(f"✅ Found coordinates: {coords['lat']:.6f}, {coords['lon']:.6f}")
                            
                            # Get full address using Google Maps Grounding
                            with st.spinner("📍 Getting detailed address..."):
                                address_info = location_manager.get_address_from_coordinates(
                                    coords['lat'], coords['lon']
                                )
                                
                                if address_info:
                                    st.info(f"📍 **Address:** {address_info['full_address']}")
                                    
                                    if 'sources' in address_info and address_info['sources']:
                                        st.markdown("**🗺️ Google Maps Sources:**")
                                        for source in address_info['sources']:
                                            st.markdown(f"- [{source['title']}]({source['uri']})")
                            
                            if st.button("💾 Save This Location", width="stretch"):
                                update_farmer_location(
                                    farmer_name, 
                                    location_input, 
                                    coords['lat'], 
                                    coords['lon']
                                )
                                st.success("✅ Location saved successfully!")
                                st.session_state['update_location'] = False
                                st.rerun()
                        else:
                            st.error("❌ Could not find coordinates. Please check the location name.")
                else:
                    st.warning("⚠️ Please enter a location.")
        
        elif location_method == "🌐 Use GPS Coordinates":
            col1, col2 = st.columns(2)
            with col1:
                lat_input = st.number_input("Latitude", format="%.6f", step=0.000001)
            with col2:
                lon_input = st.number_input("Longitude", format="%.6f", step=0.000001)
            
            if st.button("📍 Verify & Get Address", width="stretch"):
                if lat_input and lon_input:
                    with st.spinner("📍 Getting address information..."):
                        location_manager = LocationManager()
                        address_info = location_manager.get_address_from_coordinates(lat_input, lon_input)
                        
                        if address_info:
                            st.info(f"📍 **Address:** {address_info['full_address']}")
                            
                            if 'sources' in address_info and address_info['sources']:
                                st.markdown("**🗺️ Google Maps Sources:**")
                                for source in address_info['sources']:
                                    st.markdown(f"- [{source['title']}]({source['uri']})")
                            
                            location_name = st.text_input(
                                "Enter a name for this location",
                                placeholder="e.g., My Farm, Home"
                            )
                            
                            if st.button("💾 Save Location", width="stretch"):
                                if location_name:
                                    update_farmer_location(
                                        farmer_name,
                                        location_name,
                                        lat_input,
                                        lon_input
                                    )
                                    st.success("✅ Location saved successfully!")
                                    st.session_state['update_location'] = False
                                    st.rerun()
                                else:
                                    st.warning("⚠️ Please enter a name for the location.")
                        else:
                            st.error("❌ Could not verify coordinates.")
                else:
                    st.warning("⚠️ Please enter both latitude and longitude.")
    



def get_farmer_location_context(farmer_name: str) -> Optional[Tuple[float, float, str]]:
    """
    Get farmer's stored location coordinates and location name
    Returns: (latitude, longitude, location_name) or None
    """
    from database.db_functions import get_farmer_profile
    
    profile = get_farmer_profile(farmer_name)
    if profile and profile.get('latitude') and profile.get('longitude'):
        return (
            profile['latitude'],
            profile['longitude'],
            profile.get('location', 'Unknown')
        )
    return None
