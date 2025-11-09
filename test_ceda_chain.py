import requests
import pandas as pd
from datetime import datetime, timedelta

API_KEY = "0690a8ea7cd6986959695fa658783ca8244ff1999766b34dcb3d0d6c84d1e31b"
BASE = "https://api.ceda.ashoka.edu.in/v1"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

print("=" * 70)
print("🧪 Testing CEDA API - Complete Chain")
print("=" * 70)

def get_json(url, **kw):
    """Helper to make API calls"""
    r = requests.request(**kw, url=f"{BASE}{url}", headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.json()

try:
    # 1️⃣ Get Commodity
    print("\n1️⃣ Fetching commodities...")
    result = get_json("/agmarknet/commodities", method="get")
    commodities = result["output"]["data"]
    print(f"✅ Found {len(commodities)} commodities")
    
    if not commodities:
        print("❌ No commodities returned. API key may need activation.")
        exit(1)
    
    # Find Onion
    commodity = next((c for c in commodities if "onion" in c["commodity_name"].lower()), None)
    if not commodity:
        commodity = commodities[0]  # Fallback to first
    
    print(f"✅ Selected: {commodity['commodity_name']} (ID: {commodity['commodity_id']})")
    
    # 2️⃣ Get State + District
    print("\n2️⃣ Fetching geographies...")
    result = get_json("/agmarknet/geographies", method="get")
    geos = result["output"]["data"]
    print(f"✅ Found {len(geos)} states")
    
    if not geos:
        print("❌ No geographies returned.")
        exit(1)
    
    # Find Maharashtra entry
    maha_entry = next((g for g in geos if "Maharashtra" in g["census_state_name"]), None)
    if not maha_entry:
        maha_entry = geos[0]  # Fallback to first
    
    state_id = maha_entry["census_state_id"]
    state_name = maha_entry["census_state_name"]
    district_id = maha_entry["census_district_id"]
    district_name = maha_entry["census_district_name"]
    
    print(f"✅ State: {state_name} (ID: {state_id})")
    print(f"✅ District: {district_name} (ID: {district_id})")
    
    # 3️⃣ Get Markets
    print("\n3️⃣ Fetching markets...")
    payload = {
        "commodity_id": commodity["commodity_id"],
        "state_id": state_id,
        "district_id": district_id,
        "indicator": "price"
    }
    print(f"   Payload: {payload}")
    
    result = get_json("/agmarknet/markets", method="post", json=payload)
    markets = result["output"]["data"]
    print(f"✅ Found {len(markets)} markets with price data")
    
    if not markets:
        print("❌ No markets returned for this combination.")
        exit(1)
    
    market = markets[0]
    print(f"✅ Market: {market['market_name']} (ID: {market['market_id']})")
    
    # 4️⃣ Get Prices
    print("\n4️⃣ Fetching price data...")
    to_date = datetime.now().strftime("%Y-%m-%d")
    from_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    
    payload = {
        "commodity_id": commodity["commodity_id"],
        "state_id": state_id,
        "district_id": [district_id],
        "market_id": [market["market_id"]],
        "from_date": from_date,
        "to_date": to_date
    }
    print(f"   Date range: {from_date} to {to_date}")
    
    result = get_json("/agmarknet/prices", method="post", json=payload)
    prices = result["output"]["data"]
    print(f"✅ Found {len(prices)} price records!")
    
    if prices:
        df = pd.DataFrame(prices)
        print(f"\n📊 DataFrame: {len(df)} rows x {len(df.columns)} columns")
        print(f"Columns: {df.columns.tolist()}")
        
        print("\n📋 Sample Records:")
        print(df.head(10).to_string())
        
        # Statistics
        print("\n💰 Price Statistics (last 90 days):")
        print(f"   Average Modal Price: ₹{df['modal_price'].mean():.2f}/qtl")
        print(f"   Minimum Price: ₹{df['min_price'].min():.2f}/qtl")
        print(f"   Maximum Price: ₹{df['max_price'].max():.2f}/qtl")
        
        # Convert to per kg
        print(f"\n💡 Per Kg Prices (÷100):")
        print(f"   Average: ₹{df['modal_price'].mean()/100:.2f}/kg")
        print(f"   Min: ₹{df['min_price'].min()/100:.2f}/kg")
        print(f"   Max: ₹{df['max_price'].max()/100:.2f}/kg")
        
        print("\n" + "=" * 70)
        print("🎉 CEDA API IS FULLY WORKING!")
        print("=" * 70)
        print("✅ Commodities endpoint working")
        print("✅ Geographies endpoint working")
        print("✅ Markets endpoint working")
        print("✅ Prices endpoint working")
        print("✅ Real data successfully retrieved!")
        print("\n🚀 Ready to integrate into Streamlit app!")
        print("=" * 70)
    else:
        print("⚠️ No price data available for this date range")
        print("💡 Try increasing the date range (e.g., 180 days)")
        
except requests.exceptions.HTTPError as e:
    print(f"\n❌ HTTP Error: {e}")
    print(f"Response: {e.response.text if hasattr(e, 'response') else 'N/A'}")
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("✅ TEST COMPLETE")
print("=" * 70)


