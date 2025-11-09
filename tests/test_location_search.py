"""
Test location search with fuzzy/misspelled names
"""
from weather.ai_client import AIClient

def test_location_search():
    """Test location search with various inputs"""
    print("🧪 Testing Location Search with Google Maps Grounding\n")
    
    # Test locations including misspelled ones
    test_locations = [
        "sainah nagar wadgaonsheri",  # User's input (misspelled)
        "Sainath Nagar Wadgaon Sheri",  # Correct spelling
        "wadgaon sheri pune",
        "Kothrud Pune",
        "Deccan Gymkhana Pune"
    ]
    
    ai_client = AIClient()
    
    for location in test_locations:
        print(f"\n{'='*60}")
        print(f"Searching for: {location}")
        print(f"{'='*60}")
        
        try:
            result = ai_client.get_coordinates_from_google_search(location)
            
            if result:
                print(f"✅ Found coordinates!")
                print(f"   📍 Latitude: {result['lat']}")
                print(f"   📍 Longitude: {result['lon']}")
            else:
                print(f"❌ Could not find location")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print(f"\n{'='*60}")
    print("✅ Test completed!")

if __name__ == "__main__":
    test_location_search()
