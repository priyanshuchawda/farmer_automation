"""
Test script to verify reverse geocoding functionality
"""
from weather.ai_client import AIClient

def test_reverse_geocoding():
    """Test reverse geocoding with sample coordinates"""
    print("🧪 Testing Reverse Geocoding with Gemini AI\n")
    
    # Sample coordinates (Pune area)
    test_coordinates = [
        {"lat": 18.5204, "lon": 73.8567, "name": "Pune, Maharashtra"},
        {"lat": 18.5793, "lon": 73.8143, "name": "Wadgaon Sheri, Pune"},
    ]
    
    ai_client = AIClient()
    
    for coords in test_coordinates:
        print(f"\n{'='*60}")
        print(f"Testing: {coords['name']}")
        print(f"Coordinates: {coords['lat']}, {coords['lon']}")
        print(f"{'='*60}")
        
        try:
            location_info = ai_client.get_location_from_coordinates(
                coords['lat'], 
                coords['lon']
            )
            
            if location_info:
                print("\n✅ Successfully retrieved location information:")
                print(f"   📍 Address: {location_info.get('address', 'N/A')}")
                print(f"   🏘️  City: {location_info.get('city', 'N/A')}")
                print(f"   🗺️  State: {location_info.get('state', 'N/A')}")
                print(f"   🌏 Country: {location_info.get('country', 'N/A')}")
            else:
                print("\n❌ Failed to retrieve location information")
                
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
    
    print(f"\n{'='*60}")
    print("✅ Test completed!")

if __name__ == "__main__":
    test_reverse_geocoding()
