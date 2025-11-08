"""Quick verification script for all integrations"""

import sys

print("="*70)
print("🔍 VERIFYING ALL INTEGRATIONS")
print("="*70)

tests_passed = 0
tests_failed = 0

# Test 1: Database Functions
print("\n1️⃣ Testing Database Layer...")
try:
    from database.db_functions import init_db, get_data, get_farmer_profile, get_farmer_events
    init_db()
    print("   ✅ Database functions imported and initialized")
    tests_passed += 1
except Exception as e:
    print(f"   ❌ Failed: {e}")
    tests_failed += 1

# Test 2: Weather Integration
print("\n2️⃣ Testing Weather Integration...")
try:
    from weather.weather_assistant import get_weather_forecast_for_query
    from weather.combined_forecast import get_weather_forecast
    from weather.gemini_client import GeminiClient
    print("   ✅ Weather modules imported successfully")
    tests_passed += 1
except Exception as e:
    print(f"   ❌ Failed: {e}")
    tests_failed += 1

# Test 3: Calendar Integration
print("\n3️⃣ Testing Calendar Integration...")
try:
    from calender.ai_service import AIService
    from calender.calendar_component import render_calendar
    from components.calendar_integration import render_integrated_calendar, get_weather_for_event, create_weather_alert
    print("   ✅ Calendar modules imported successfully")
    tests_passed += 1
except Exception as e:
    print(f"   ❌ Failed: {e}")
    tests_failed += 1

# Test 4: Profile Integration
print("\n4️⃣ Testing Profile Integration...")
try:
    from components.profiles_page import render_profiles_page
    print("   ✅ Profile module imported successfully")
    tests_passed += 1
except Exception as e:
    print(f"   ❌ Failed: {e}")
    tests_failed += 1

# Test 5: Marketplace Components
print("\n5️⃣ Testing Marketplace Components...")
try:
    from components.tool_listings import render_tool_listing, render_tool_management
    from components.crop_listings import render_crop_listing, render_crop_management
    print("   ✅ Marketplace modules imported successfully")
    tests_passed += 1
except Exception as e:
    print(f"   ❌ Failed: {e}")
    tests_failed += 1

# Test 6: Environment Variables
print("\n6️⃣ Testing Environment Variables...")
try:
    from weather.config import get_api_key, get_gemini_api_key
    api_key = get_api_key()
    gemini_key = get_gemini_api_key()
    
    if api_key and gemini_key:
        print(f"   ✅ OpenWeather API Key: {api_key[:10]}...")
        print(f"   ✅ Gemini API Key: {gemini_key[:10]}...")
        tests_passed += 1
    else:
        print("   ⚠️ API keys not found in .env")
        tests_failed += 1
except Exception as e:
    print(f"   ❌ Failed: {e}")
    tests_failed += 1

# Test 7: Database Tables
print("\n7️⃣ Testing Database Tables...")
try:
    import sqlite3
    conn = sqlite3.connect('farmermarket.db')
    c = conn.cursor()
    
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in c.fetchall()]
    
    required_tables = ['farmers', 'tools', 'crops', 'calendar_events']
    missing = [t for t in required_tables if t not in tables]
    
    if not missing:
        print(f"   ✅ All required tables exist: {', '.join(required_tables)}")
        
        # Check farmers table structure
        c.execute("PRAGMA table_info(farmers)")
        columns = [col[1] for col in c.fetchall()]
        
        required_columns = ['name', 'location', 'weather_location', 'latitude', 'longitude']
        missing_cols = [c for c in required_columns if c not in columns]
        
        if not missing_cols:
            print(f"   ✅ Farmers table has all required columns")
            tests_passed += 1
        else:
            print(f"   ⚠️ Missing columns in farmers table: {missing_cols}")
            tests_failed += 1
    else:
        print(f"   ❌ Missing tables: {missing}")
        tests_failed += 1
    
    conn.close()
except Exception as e:
    print(f"   ❌ Failed: {e}")
    tests_failed += 1

# Test 8: Main App
print("\n8️⃣ Testing Main App Import...")
try:
    # Just check if app.py can be parsed without errors
    with open('app.py', 'r', encoding='utf-8') as f:
        code = f.read()
        compile(code, 'app.py', 'exec')
    print("   ✅ app.py is valid Python code")
    tests_passed += 1
except Exception as e:
    print(f"   ❌ Failed: {e}")
    tests_failed += 1

# Summary
print("\n" + "="*70)
print("📊 VERIFICATION SUMMARY")
print("="*70)
print(f"Tests Passed: {tests_passed}/{tests_passed + tests_failed}")
print(f"Tests Failed: {tests_failed}/{tests_passed + tests_failed}")

if tests_failed == 0:
    print("\n✅ ALL INTEGRATIONS VERIFIED SUCCESSFULLY!")
    print("\n🚀 You can now run: streamlit run app.py")
else:
    print(f"\n⚠️ {tests_failed} test(s) failed. Please check the errors above.")
    sys.exit(1)

print("="*70)
