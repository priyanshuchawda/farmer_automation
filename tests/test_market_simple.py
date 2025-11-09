import os
from dotenv import load_dotenv
import requests

load_dotenv()
API_KEY = os.getenv("DATAGOVIN_API_KEY")

print(f"API Key: {'Found' if API_KEY else 'Missing'}")

if not API_KEY:
    print("❌ Add DATAGOVIN_API_KEY to .env file")
    exit(1)

url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
params = {
    "api-key": API_KEY,
    "format": "json",
    "limit": 2,
    "filters[state]": "Maharashtra"
}

print(f"\n🔍 Testing with Maharashtra state filter...")
print(f"URL: {url}")

try:
    response = requests.get(url, params=params, timeout=60)
    print(f"\n✅ Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Records: {len(data.get('records', []))}")
        
        if data.get('records'):
            rec = data['records'][0]
            print(f"\n📊 Sample:")
            print(f"  {rec.get('commodity')} - {rec.get('market')}")
            print(f"  Price: ₹{float(rec.get('modal_price',0))/100}/kg")
            print("\n✅ API WORKING!")
        else:
            print("⚠️ No records returned")
    else:
        print(f"❌ Error: {response.text[:100]}")
        
except requests.Timeout:
    print("❌ API Timeout - Server is slow or unresponsive")
except Exception as e:
    print(f"❌ Error: {e}")


