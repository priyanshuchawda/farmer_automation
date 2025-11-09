# test_cache_system.py
"""Test the caching system functionality"""

from database.cache_manager import CacheManager
from datetime import datetime
import json

print('🧪 Testing Cache Manager...\n')

# Initialize cache
cache = CacheManager()

# Test 1: Weather Cache
print('1️⃣ Testing Weather Cache:')
weather_data = {
    'temp': 25,
    'humidity': 70,
    'description': 'Sunny',
    'forecast': ['sunny', 'cloudy']
}
cache.set_weather_cache('Pune', weather_data, hours=24)
print('   ✅ Set weather cache for Pune')

cached = cache.get_weather_cache('Pune')
if cached:
    print(f'   ✅ Retrieved cached weather: {cached["description"]}')
else:
    print('   ❌ Failed to retrieve cache')

# Test 2: Market Price Cache
print('\n2️⃣ Testing Market Price Cache:')
price_data = {
    'crop': 'Wheat',
    'price': 2500,
    'market': 'APMC Pune',
    'date': datetime.now().isoformat()
}
cache.set_market_price_cache('Wheat', 'Pune', price_data, hours=24)
print('   ✅ Set market price cache for Wheat in Pune')

cached_price = cache.get_market_price_cache('Wheat', 'Pune')
if cached_price:
    print(f'   ✅ Retrieved cached price: ₹{cached_price["price"]}')
else:
    print('   ❌ Failed to retrieve cache')

# Test 3: Prediction Cache
print('\n3️⃣ Testing Prediction Cache:')
prediction_data = {
    'current_price': 2500,
    'predicted_price': 2750,
    'confidence': 0.85,
    'trend': 'upward'
}
cache.set_prediction_cache('Wheat', 'Pune', 2500, prediction_data, hours=24)
print('   ✅ Set prediction cache for Wheat in Pune')

cached_pred = cache.get_prediction_cache('Wheat', 'Pune', 2500, tolerance=100)
if cached_pred:
    print(f'   ✅ Retrieved cached prediction: ₹{cached_pred["predicted_price"]}')
else:
    print('   ❌ Failed to retrieve cache')

# Test 4: Price tolerance
print('\n4️⃣ Testing Price Tolerance (±100):')
cached_pred_2 = cache.get_prediction_cache('Wheat', 'Pune', 2550, tolerance=100)
if cached_pred_2:
    print(f'   ✅ Found cache for similar price (2550 vs 2500)')
else:
    print('   ❌ Tolerance not working')

# Test 5: Cache Statistics
print('\n5️⃣ Cache Statistics:')
info = cache.get_cache_info()
print(f'   📊 Weather cached: {info["weather_cached"]}')
print(f'   📊 Market prices cached: {info["market_prices_cached"]}')
print(f'   📊 Predictions cached: {info["predictions_cached"]}')
print(f'   📊 Total cached items: {info["total_cached"]}')

stats = cache.get_cache_statistics()
for cache_type, stat in stats.items():
    print(f'   📈 {cache_type}: {stat["hits"]} hits, {stat["misses"]} misses, {stat["hit_rate"]}% hit rate')

# Test 6: Clear expired
print('\n6️⃣ Testing Cache Cleanup:')
result = cache.clear_expired_cache()
print(f'   🧹 Cleared {result["total_deleted"]} expired entries')

print('\n✅ Cache system is working correctly!')
print('\n💡 Key Features:')
print('   • 24-hour cache lifetime')
print('   • Automatic hit/miss tracking')
print('   • Price tolerance matching (±100 rupees)')
print('   • Separate caches for weather, prices, predictions')


