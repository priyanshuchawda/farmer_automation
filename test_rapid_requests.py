# test_rapid_requests.py
from database.cache_manager import CacheManager
import time

cache = CacheManager()

# Test rapid repeated requests
print('🚀 Testing Rapid Repeated Requests\n')

# Simulate 10 requests for same data
crop = 'Tomato'
location = 'Mumbai'

# Set initial cache
cache.set_market_price_cache(crop, location, {
    'price': 3000,
    'market': 'APMC Mumbai',
    'date': '2025-01-09'
}, hours=24)

print(f'Set cache for {crop} in {location}')
print('Making 10 rapid requests...\n')

for i in range(10):
    start = time.time()
    result = cache.get_market_price_cache(crop, location)
    elapsed = time.time() - start
    if result:
        print(f'  Request {i+1}: ✅ Cache hit in {elapsed*1000:.1f}ms')
    else:
        print(f'  Request {i+1}: ❌ Cache miss')

print('\n📊 Final Statistics:')
info = cache.get_cache_info()
stats = cache.get_cache_statistics()

print(f'Total cached: {info["total_cached"]} items')
if 'market_price' in stats:
    m = stats['market_price']
    print(f'Market Price Cache: {m["hits"]} hits, {m["misses"]} misses ({m["hit_rate"]}% hit rate)')


