import requests
import pandas as pd
from datetime import datetime, timedelta

API_KEY = "0690a8ea7cd6986959695fa658783ca8244ff1999766b34dcb3d0d6c84d1e31b"
BASE_URL = "https://api.ceda.ashoka.edu.in/v1"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

print("=" * 70)
print("🧪 Testing CEDA API (Correct Implementation)")
print("=" * 70)

# Test 1: Get all commodities
print("\n1️⃣ Getting all commodities...")
try:
    response = requests.get(f"{BASE_URL}/agmarknet/commodities", headers=headers, timeout=15)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        commodities = data.get("commodities", [])
        print(f"✅ Found {len(commodities)} commodities")
        print("\n📋 Sample commodities:")
        for comm in commodities[:10]:
            print(f"   ID: {comm['id']}, Name: {comm['name']}")
        
        # Save for later use
        commodity_map = {c['name']: c['id'] for c in commodities}
    else:
        print(f"❌ Error: {response.text}")
        commodity_map = {}
except Exception as e:
    print(f"❌ Error: {str(e)}")
    commodity_map = {}

# Test 2: Get geographies
print("\n2️⃣ Getting geographies (states and districts)...")
try:
    response = requests.get(f"{BASE_URL}/agmarknet/geographies", headers=headers, timeout=15)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        geographies = data.get("geographies", [])
        print(f"✅ Found {len(geographies)} states")
        
        print("\n📍 Sample states:")
        for state in geographies[:5]:
            print(f"   State: {state['state_name']} (ID: {state['state_id']})")
            if state['districts']:
                print(f"      Districts: {len(state['districts'])}")
        
        # Find Maharashtra
        maharashtra = next((s for s in geographies if 'Maharashtra' in s['state_name']), None)
        if maharashtra:
            print(f"\n✅ Maharashtra found! State ID: {maharashtra['state_id']}")
            print(f"   Districts: {len(maharashtra['districts'])}")
    else:
        print(f"❌ Error: {response.text}")
except Exception as e:
    print(f"❌ Error: {str(e)}")

# Test 3: Get prices (using POST)
print("\n3️⃣ Getting actual price data...")
try:
    # Get tomato ID
    tomato_id = commodity_map.get("Tomato", 1)
    
    # Date range
    to_date = datetime.now().strftime("%Y-%m-%d")
    from_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    payload = {
        "commodity_id": tomato_id,
        "state_id": 8,  # Maharashtra
        "from_date": from_date,
        "to_date": to_date
    }
    
    print(f"Payload: {payload}")
    
    response = requests.post(
        f"{BASE_URL}/agmarknet/prices",
        headers=headers,
        json=payload,
        timeout=20
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        records = data.get("data", [])
        print(f"✅ Found {len(records)} price records!")
        
        if records:
            df = pd.DataFrame(records)
            print(f"\n✅ DataFrame: {len(df)} rows x {len(df.columns)} columns")
            print(f"Columns: {df.columns.tolist()}")
            
            print("\n📊 Sample Records:")
            print(df.head(5).to_string())
            
            # Calculate statistics
            print("\n💰 Price Statistics (last 30 days):")
            print(f"   Average Modal Price: ₹{df['modal_price'].mean():.2f}/qtl")
            print(f"   Min Price: ₹{df['min_price'].min():.2f}/qtl")
            print(f"   Max Price: ₹{df['max_price'].max():.2f}/qtl")
            
            print("\n" + "=" * 70)
            print("🎉 CEDA API IS WORKING PERFECTLY!")
            print("=" * 70)
            print("✅ Can fetch commodities")
            print("✅ Can fetch geographies")
            print("✅ Can fetch price data")
            print("✅ Ready to integrate into main app!")
            print("=" * 70)
    else:
        print(f"❌ Error: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")

print("\n" + "=" * 70)
print("✅ TEST COMPLETE")
print("=" * 70)


