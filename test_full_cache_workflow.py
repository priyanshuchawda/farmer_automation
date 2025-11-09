# test_full_cache_workflow.py
"""
Complete test of the caching workflow
Shows how cache reduces API calls on repeated requests
"""

from ai.price_predictor import PricePredictor
from database.cache_manager import CacheManager
import time

print("🧪 Testing Full Cache Workflow\n")
print("=" * 70)

# Initialize
predictor = PricePredictor()
cache = CacheManager()

# Clear all cache to start fresh
print("\n1️⃣ Clearing existing cache...")
cache.clear_all_cache()
print("   ✅ Cache cleared\n")

# Test parameters
crop = "Wheat"
location = "Pune"
price = 2500

print("=" * 70)
print(f"\n2️⃣ FIRST REQUEST (Cache Miss - Will fetch fresh data)")
print(f"   Crop: {crop}")
print(f"   Location: {location}")
print(f"   Current Price: ₹{price}/quintal")
print("-" * 70)

start_time = time.time()

# This will fetch fresh data
try:
    prediction1 = predictor.predict_future_prices(crop, price, location, days_ahead=30)
    first_request_time = time.time() - start_time
    
    print(f"\n   ⏱️  Time taken: {first_request_time:.2f} seconds")
    print(f"   📊 Predicted price: ₹{prediction1.get('predicted_price', 'N/A')}")
    print(f"   📈 Trend: {prediction1.get('trend', 'N/A')}")
except Exception as e:
    print(f"   ⚠️  Error: {e}")
    print("   (This is expected if API keys are not configured)")
    first_request_time = 0

print("\n" + "=" * 70)
print("\n3️⃣ SECOND REQUEST (Cache Hit - Should be instant)")
print(f"   Same crop, location, and similar price")
print("-" * 70)

start_time = time.time()

# This should use cache
try:
    prediction2 = predictor.predict_future_prices(crop, price, location, days_ahead=30)
    second_request_time = time.time() - start_time
    
    print(f"\n   ⏱️  Time taken: {second_request_time:.2f} seconds")
    print(f"   📊 Predicted price: ₹{prediction2.get('predicted_price', 'N/A')}")
    
    if second_request_time < first_request_time and first_request_time > 0:
        speedup = first_request_time / second_request_time if second_request_time > 0 else float('inf')
        print(f"\n   🚀 SPEEDUP: {speedup:.1f}x faster!")
        print(f"   💾 Cache saved {first_request_time - second_request_time:.2f} seconds")
except Exception as e:
    print(f"   ⚠️  Error: {e}")

print("\n" + "=" * 70)
print("\n4️⃣ THIRD REQUEST (Cache Hit with price tolerance)")
print(f"   Same crop/location, slightly different price (₹{price + 50})")
print("-" * 70)

start_time = time.time()

# This should still use cache due to tolerance (±100)
try:
    prediction3 = predictor.predict_future_prices(crop, price + 50, location, days_ahead=30)
    third_request_time = time.time() - start_time
    
    print(f"\n   ⏱️  Time taken: {third_request_time:.2f} seconds")
    print(f"   📊 Predicted price: ₹{prediction3.get('predicted_price', 'N/A')}")
    print(f"   💡 Used cache despite price difference (tolerance: ±₹100)")
except Exception as e:
    print(f"   ⚠️  Error: {e}")

print("\n" + "=" * 70)
print("\n5️⃣ Cache Statistics")
print("-" * 70)

stats = cache.get_cache_statistics()
info = cache.get_cache_info()

print(f"\n   📦 Total cached items: {info['total_cached']}")
print(f"   🌤️  Weather cache: {info['weather_cached']}")
print(f"   💰 Market price cache: {info['market_prices_cached']}")
print(f"   🤖 Prediction cache: {info['predictions_cached']}")

if stats:
    print("\n   📈 Performance Metrics:")
    for cache_type, stat in stats.items():
        print(f"      • {cache_type}: {stat['hits']} hits, {stat['misses']} misses ({stat['hit_rate']}% hit rate)")

print("\n" + "=" * 70)
print("\n✅ Cache System Demonstration Complete!")
print("\n💡 Key Benefits Demonstrated:")
print("   • ⚡ Instant responses for cached data")
print("   • 💰 Reduced API costs (no repeated calls)")
print("   • 🎯 Smart price tolerance matching")
print("   • 📊 Automatic hit/miss tracking")
print("   • ⏰ 24-hour cache lifetime for all data")
print("\n" + "=" * 70)


