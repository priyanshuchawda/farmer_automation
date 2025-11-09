"""
Test Script for Google Maps Grounding with Gemini 2.5 Flash
Demonstrates location-aware features powered by Google Maps
"""

from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()

def test_google_maps_grounding():
    """Test Google Maps grounding functionality"""
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env file")
        return
    
    client = genai.Client(api_key=api_key)
    
    # Test location (Pune, Maharashtra, India)
    test_latitude = 18.5204
    test_longitude = 73.8567
    
    print("\n" + "="*80)
    print("🗺️ TESTING GOOGLE MAPS GROUNDING WITH GEMINI 2.5 FLASH")
    print("="*80)
    print(f"\n📍 Test Location: Pune, Maharashtra, India")
    print(f"🌐 Coordinates: {test_latitude}, {test_longitude}")
    print("\n" + "="*80)
    
    # Test 1: Get address from coordinates
    print("\n📋 TEST 1: Get Address from Coordinates")
    print("-" * 80)
    
    prompt = f"""What is the complete address and location details for these GPS coordinates?
Latitude: {test_latitude}
Longitude: {test_longitude}

Please provide the full address with city, state, country, and nearby landmarks."""
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_maps=types.GoogleMaps())],
                tool_config=types.ToolConfig(
                    retrieval_config=types.RetrievalConfig(
                        lat_lng=types.LatLng(latitude=test_latitude, longitude=test_longitude)
                    )
                ),
            ),
        )
        
        print("\n✅ Response:")
        print(response.text)
        
        # Check for grounding metadata
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'grounding_metadata'):
                grounding = candidate.grounding_metadata
                if hasattr(grounding, 'grounding_chunks') and grounding.grounding_chunks:
                    print("\n🗺️ Google Maps Sources:")
                    for idx, chunk in enumerate(grounding.grounding_chunks, 1):
                        if hasattr(chunk, 'maps'):
                            print(f"  {idx}. {chunk.maps.title}")
                            print(f"     🔗 {chunk.maps.uri}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Find nearby agricultural services
    print("\n\n📋 TEST 2: Find Nearby Agricultural Services")
    print("-" * 80)
    
    prompt = "Find agricultural equipment dealers and seed stores near me with ratings and reviews"
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_maps=types.GoogleMaps(enable_widget=True))],
                tool_config=types.ToolConfig(
                    retrieval_config=types.RetrievalConfig(
                        lat_lng=types.LatLng(latitude=test_latitude, longitude=test_longitude)
                    )
                ),
            ),
        )
        
        print("\n✅ Response:")
        print(response.text)
        
        # Check for grounding metadata and sources
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'grounding_metadata'):
                grounding = candidate.grounding_metadata
                
                if hasattr(grounding, 'grounding_chunks') and grounding.grounding_chunks:
                    print("\n🗺️ Places Found (from Google Maps):")
                    for idx, chunk in enumerate(grounding.grounding_chunks, 1):
                        if hasattr(chunk, 'maps'):
                            print(f"\n  {idx}. {chunk.maps.title}")
                            print(f"     🔗 {chunk.maps.uri}")
                            if hasattr(chunk.maps, 'place_id'):
                                print(f"     🆔 Place ID: {chunk.maps.place_id}")
                
                if hasattr(grounding, 'google_maps_widget_context_token'):
                    print(f"\n🗺️ Widget Token Available: Yes")
                    print(f"   Token (first 50 chars): {grounding.google_maps_widget_context_token[:50]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Find specific places (restaurants)
    print("\n\n📋 TEST 3: Find Restaurants Near Location")
    print("-" * 80)
    
    prompt = "What are the best restaurants within walking distance from here? Include ratings, cuisine types, and opening hours."
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_maps=types.GoogleMaps())],
                tool_config=types.ToolConfig(
                    retrieval_config=types.RetrievalConfig(
                        lat_lng=types.LatLng(latitude=test_latitude, longitude=test_longitude)
                    )
                ),
            ),
        )
        
        print("\n✅ Response:")
        print(response.text)
        
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'grounding_metadata'):
                grounding = candidate.grounding_metadata
                if hasattr(grounding, 'grounding_chunks') and grounding.grounding_chunks:
                    print(f"\n🗺️ Total Places Found: {len(grounding.grounding_chunks)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Personalized recommendations
    print("\n\n📋 TEST 4: Get Personalized Farming Recommendations")
    print("-" * 80)
    
    prompt = """I am a farmer looking for:
1. Veterinary services for dairy cattle
2. Organic fertilizer suppliers
3. Cold storage facilities

Please recommend places near my location with good reviews and provide contact details."""
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_maps=types.GoogleMaps())],
                tool_config=types.ToolConfig(
                    retrieval_config=types.RetrievalConfig(
                        lat_lng=types.LatLng(latitude=test_latitude, longitude=test_longitude)
                    )
                ),
            ),
        )
        
        print("\n✅ Response:")
        print(response.text)
        
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'grounding_metadata'):
                grounding = candidate.grounding_metadata
                if hasattr(grounding, 'grounding_chunks') and grounding.grounding_chunks:
                    print("\n🗺️ Recommended Places:")
                    for idx, chunk in enumerate(grounding.grounding_chunks, 1):
                        if hasattr(chunk, 'maps'):
                            print(f"  {idx}. {chunk.maps.title}")
                            print(f"     🔗 {chunk.maps.uri}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n\n" + "="*80)
    print("✅ TESTING COMPLETE!")
    print("="*80)
    print("\n💡 Key Features Demonstrated:")
    print("  1. ✅ Address lookup from GPS coordinates")
    print("  2. ✅ Nearby places search with location context")
    print("  3. ✅ Restaurant recommendations with ratings")
    print("  4. ✅ Personalized farming service recommendations")
    print("  5. ✅ Google Maps grounding with sources and links")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    test_google_maps_grounding()
