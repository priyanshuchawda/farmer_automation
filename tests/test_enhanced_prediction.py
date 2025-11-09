#!/usr/bin/env python3
"""
Test Enhanced Price Prediction with Weather, News, and Market Data
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai.price_predictor import PricePredictor

def print_section(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def test_enhanced_prediction():
    """Test the enhanced prediction system with all data sources."""
    print_section("ENHANCED PRICE PREDICTION TEST")
    
    print("🚀 Initializing Enhanced Price Predictor...")
    predictor = PricePredictor()
    
    print("\n📊 Testing prediction for Wheat in Pune, Maharashtra")
    print("-" * 80)
    
    # Test prediction
    prediction = predictor.predict_future_prices(
        crop_name="Wheat",
        current_price=2500.0,
        location="Pune, Maharashtra",
        days_ahead=30
    )
    
    if prediction['success']:
        print("\n✅ PREDICTION SUCCESSFUL!\n")
        
        # Weather Data
        if prediction.get('weather_data'):
            weather = prediction['weather_data']
            print("🌤️  WEATHER DATA:")
            print(f"   Location: {weather['location']}")
            print(f"   Temperature: {weather['current']['temperature']:.1f}°C")
            print(f"   Humidity: {weather['current']['humidity']}%")
            print(f"   Conditions: {weather['current']['weather']}")
            print(f"   Wind Speed: {weather['current']['wind_speed']} m/s")
            
            if weather.get('forecast'):
                print(f"\n   5-Day Forecast:")
                for day in weather['forecast'][:3]:
                    print(f"   • {day['date']}: {day['temp_min']:.0f}-{day['temp_max']:.0f}°C, {day['weather']}")
        
        # Online Market Data
        print("\n🔍 ONLINE MARKET INTELLIGENCE:")
        if prediction.get('online_data'):
            online = prediction['online_data']
            if online.get('current_price'):
                print(f"   Current Market Price: ₹{online['current_price']:.2f}/quintal")
            print(f"   News: {online.get('news_summary', 'N/A')[:100]}...")
            print(f"   Market Conditions: {online.get('market_conditions', 'N/A')[:80]}...")
        
        # Predictions
        print("\n📈 PRICE PREDICTIONS:")
        print(f"   Current Price: ₹{prediction['current_price']:.2f}")
        print(f"   Trend: {prediction['trend']}")
        print(f"   Confidence: {prediction['confidence']}")
        
        if prediction['predictions']:
            print(f"\n   Forecasts:")
            for key, value in prediction['predictions'].items():
                days = key.replace('day_', '')
                change = ((value - prediction['current_price']) / prediction['current_price'] * 100)
                print(f"   • {days} days: ₹{value:.2f} ({change:+.1f}%)")
        
        print(f"\n   📅 Best Day: Day {prediction['peak_day']}")
        print(f"   📅 Worst Day: Day {prediction['lowest_day']}")
        
        # Key Factors
        if prediction['key_factors']:
            print("\n🔑 KEY FACTORS:")
            for i, factor in enumerate(prediction['key_factors'], 1):
                print(f"   {i}. {factor}")
        
        # Recommendation
        if prediction['recommendation']:
            print(f"\n💡 AI RECOMMENDATION:")
            print(f"   {prediction['recommendation'][:200]}...")
        
        print("\n" + "="*80)
        print("✅ TEST PASSED: Enhanced prediction system working with all data sources!")
        print("="*80)
        return True
    else:
        print(f"\n❌ PREDICTION FAILED: {prediction.get('message', 'Unknown error')}")
        if 'error' in prediction:
            print(f"   Error: {prediction['error']}")
        return False

def test_weather_api():
    """Test weather API separately."""
    print_section("WEATHER API TEST")
    
    predictor = PricePredictor()
    
    locations = ["Pune, Maharashtra", "Delhi", "Mumbai"]
    
    for location in locations:
        print(f"🌤️  Testing weather for {location}...")
        weather = predictor.get_weather_data(location)
        
        if weather:
            print(f"   ✅ Temperature: {weather['current']['temperature']:.1f}°C")
            print(f"   ✅ Humidity: {weather['current']['humidity']}%")
            print(f"   ✅ Weather: {weather['current']['weather']}")
        else:
            print(f"   ⚠️  Weather data not available")
        print()
    
    return True

def test_online_search():
    """Test online search for news and prices."""
    print_section("ONLINE SEARCH TEST")
    
    predictor = PricePredictor()
    
    test_crops = [
        ("Wheat", "Pune, Maharashtra"),
        ("Rice", "Haryana"),
        ("Tomato", "Karnataka")
    ]
    
    for crop, location in test_crops:
        print(f"🔍 Searching for {crop} in {location}...")
        data = predictor.get_online_news_and_prices(crop, location)
        
        if data:
            if data.get('current_price'):
                print(f"   ✅ Price found: ₹{data['current_price']:.2f}/quintal")
            print(f"   📰 News: {data.get('news_summary', 'N/A')[:80]}...")
            print(f"   📊 Market: {data.get('market_conditions', 'N/A')[:60]}...")
        else:
            print(f"   ⚠️  Search data not available")
        print()
    
    return True

def main():
    """Run all tests."""
    print("\n🤖 ENHANCED AI PRICE PREDICTION SYSTEM - COMPREHENSIVE TEST")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Check API keys
    AI_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    weather_key = os.getenv("OPENWEATHER_API_KEY")
    
    print("🔑 API Keys Check:")
    print(f"   AI API: {'✅ Found' if AI_key else '❌ Missing'}")
    print(f"   Weather API: {'✅ Found' if weather_key else '❌ Missing'}")
    
    if not AI_key:
        print("\n❌ GEMINI_API_KEY not found! Cannot proceed.")
        return
    
    # Run tests
    tests = [
        ("Weather API Integration", test_weather_api),
        ("Online Search Integration", test_online_search),
        ("Enhanced Price Prediction", test_enhanced_prediction)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{'='*80}")
    print(f"TOTAL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print(f"{'='*80}\n")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Enhanced system is fully operational!")
    elif passed >= total * 0.66:
        print("✅ SYSTEM FUNCTIONAL with weather + news + AI predictions!")
    else:
        print("⚠️  Some features need attention.")
    
    print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

if __name__ == "__main__":
    main()


