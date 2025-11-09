import requests

API_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
API_KEY = "YOUR_PERSONAL_API_KEY_HERE"  # replace with your key


# ----------------------------------------------------------------
# Get all unique states
# ----------------------------------------------------------------
def get_all_states():
    params = {
        "api-key": API_KEY,
        "format": "json",
        "limit": 10000
    }
    response = requests.get(API_URL, params=params)
    data = response.json()
    records = data.get("records", [])
    states = sorted(set(r["state"] for r in records if r.get("state")))
    return states


# ----------------------------------------------------------------
# Get districts by state
# ----------------------------------------------------------------
def get_districts_by_state(state_name):
    params = {
        "api-key": API_KEY,
        "format": "json",
        "limit": 10000,
        "filters[state]": state_name
    }
    response = requests.get(API_URL, params=params)
    data = response.json()
    records = data.get("records", [])
    districts = sorted(set(r["district"] for r in records if r.get("district")))
    return districts


# ----------------------------------------------------------------
# Get markets (mandis) by district
# ----------------------------------------------------------------
def get_markets_by_district(district_name):
    params = {
        "api-key": API_KEY,
        "format": "json",
        "limit": 10000,
        "filters[district]": district_name
    }
    response = requests.get(API_URL, params=params)
    data = response.json()
    records = data.get("records", [])
    markets = sorted(set(r["market"] for r in records if r.get("market")))
    return markets


# ----------------------------------------------------------------
# Get price by market and date (₹/kg)
# ----------------------------------------------------------------
def get_price(commodity, market, date):
    params = {
        "api-key": API_KEY,
        "format": "json",
        "limit": 10000,
        "filters[commodity]": commodity,
        "filters[market]": market,
        "filters[arrival_date]": date
    }
    response = requests.get(API_URL, params=params)
    data = response.json()
    records = data.get("records", [])

    if not records:
        print(f"\n❌ No price data found for {commodity} in {market} on {date}.")
        return

    for record in records:
        min_price = float(record.get("min_price", 0)) / 100
        max_price = float(record.get("max_price", 0)) / 100
        modal_price = float(record.get("modal_price", 0)) / 100
        print(f"\n📅 Date: {record.get('arrival_date')}")
        print(f"🥬 Commodity: {record.get('commodity')}")
        print(f"🏬 Market: {record.get('market')} ({record.get('district')}, {record.get('state')})")
        print(f"💰 Prices (₹/kg): Min = {min_price:.2f}, Max = {max_price:.2f}, Modal = {modal_price:.2f}")
        print("—" * 60)


# ----------------------------------------------------------------
# MAIN FLOW
# ----------------------------------------------------------------
if __name__ == "__main__":
    print("\n🌾 Government Vegetable Price Finder")
    print("===================================")

    # 1️⃣ Select State
    states = get_all_states()
    print("\n📍 Available States:")
    print("—" * 60)
    for i, state in enumerate(states, start=1):
        print(f"{i}. {state}")

    try:
        s_choice = int(input("\nSelect State Number: ").strip())
        if 1 <= s_choice <= len(states):
            selected_state = states[s_choice - 1]
        else:
            print("❌ Invalid state number.")
            exit()
    except ValueError:
        print("❌ Please enter a valid number.")
        exit()

    # 2️⃣ Select District
    districts = get_districts_by_state(selected_state)
    if not districts:
        print(f"No districts found for {selected_state}.")
        exit()

    print(f"\n🏙️ Districts in {selected_state}:")
    print("—" * 60)
    for i, d in enumerate(districts, start=1):
        print(f"{i}. {d}")

    try:
        d_choice = int(input("\nSelect District Number: ").strip())
        if 1 <= d_choice <= len(districts):
            selected_district = districts[d_choice - 1]
        else:
            print("❌ Invalid district number.")
            exit()
    except ValueError:
        print("❌ Please enter a valid number.")
        exit()

    # 3️⃣ Select Market
    markets = get_markets_by_district(selected_district)
    if not markets:
        print(f"No markets found for district {selected_district}.")
        exit()

    print(f"\n🏬 Markets in {selected_district}:")
    print("—" * 60)
    for i, m in enumerate(markets, start=1):
        print(f"{i}. {m}")

    try:
        m_choice = int(input("\nSelect Market Number: ").strip())
        if 1 <= m_choice <= len(markets):
            selected_market = markets[m_choice - 1]
        else:
            print("❌ Invalid market number.")
            exit()
    except ValueError:
        print("❌ Please enter a valid number.")
        exit()

    # 4️⃣ Enter Commodity and Date
    commodity = input("\nEnter Vegetable/Commodity Name (e.g., Tomato): ").strip()
    date = input("Enter Date (YYYY-MM-DD): ").strip()

    print("\n🔍 Fetching Data... Please wait...\n")
    get_price(commodity, selected_market, date)


