"""
Test script for strict coordinate format with AI
"""
from weather.ai_client import AIClient
import os
from dotenv import load_dotenv

load_dotenv()

def test_coordinate_extraction():
    """Test coordinate extraction with the new strict format"""
    
    # Check if API key exists
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env file")
        return
    
    print("🚀 Testing Strict Coordinate Format\n")
    print("=" * 60)
    
    # Test locations
    test_locations = [
        "Wadgaonsheri pune",
        "Mumbai, Maharashtra",
        "Delhi",
        "Bangalore"
    ]
    
    try:
        client = AIClient()
        
        for location in test_locations:
            print(f"\n📍 Testing location: {location}")
            print("-" * 60)
            
            coords = client.get_coordinates_from_google_search(location)
            
            if coords:
                print(f"✅ SUCCESS!")
                print(f"   Latitude:  {coords['lat']}")
                print(f"   Longitude: {coords['lon']}")
            else:
                print(f"❌ FAILED to extract coordinates")
            
            print("-" * 60)
    
    except Exception as e:
        print(f"❌ Error: {e}")

def test_reverse_geocoding():
    """Test reverse geocoding with strict format"""
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env file")
        return
    
    print("\n🌍 Testing Reverse Geocoding\n")
    print("=" * 60)
    
    # Test coordinates (Wadgaonsheri, Pune)
    test_coords = [
        (18.553516, 73.930104),  # Wadgaonsheri
        (19.0760, 72.8777),      # Mumbai
    ]
    
    try:
        client = AIClient()
        
        for lat, lon in test_coords:
            print(f"\n🗺️  Testing coordinates: ({lat}, {lon})")
            print("-" * 60)
            
            location_info = client.get_location_from_coordinates(lat, lon)
            
            if location_info:
                print(f"✅ SUCCESS!")
                for key, value in location_info.items():
                    print(f"   {key}: {value}")
            else:
                print(f"❌ FAILED to get location info")
            
            print("-" * 60)
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  🧪 STRICT COORDINATE FORMAT TEST")
    print("=" * 60)
    
    # Test coordinate extraction
    test_coordinate_extraction()
    
    # Test reverse geocoding
    test_reverse_geocoding()
    
    print("\n" + "=" * 60)
    print("  ✅ TEST COMPLETE")
    print("=" * 60 + "\n")


