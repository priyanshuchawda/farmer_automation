import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

API_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
API_KEY = os.getenv("DATAGOVIN_API_KEY")

print("=" * 60)
print("🧪 Testing Market Price API")
print("=" * 60)

# Check API Key
if API_KEY:
    print(f"✅ API Key loaded: {API_KEY[:10]}...")
else:
    print("❌ API Key NOT found in .env file")
    print("📝 Please add DATAGOVIN_API_KEY to your .env file")
    exit(1)

# Test API connection
print("\n🔍 Testing API connection...")
params = {
    "api-key": API_KEY,
    "format": "json",
    "limit": 5
}

try:
    response = requests.get(API_URL, params=params, timeout=30)
    print(f"📡 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        records = data.get("records", [])
        
        print(f"✅ API Working! Found {len(records)} records")
        
        if records:
            print("\n📊 Sample Record:")
            sample = records[0]
            print(f"   State: {sample.get('state')}")
            print(f"   District: {sample.get('district')}")
            print(f"   Market: {sample.get('market')}")
            print(f"   Commodity: {sample.get('commodity')}")
            print(f"   Date: {sample.get('arrival_date')}")
            print(f"   Min Price: ₹{float(sample.get('min_price', 0))/100:.2f}/kg")
            print(f"   Modal Price: ₹{float(sample.get('modal_price', 0))/100:.2f}/kg")
            print(f"   Max Price: ₹{float(sample.get('max_price', 0))/100:.2f}/kg")
        
        print("\n✅ Market Price API is working correctly!")
    else:
        print(f"❌ API Error: Status {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")

print("=" * 60)


