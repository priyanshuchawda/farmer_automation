# check_cache_tables.py
import sqlite3
from datetime import datetime

print('📊 CACHE STORAGE IN SQL DATABASE\n')
print('=' * 70)

conn = sqlite3.connect('farmermarket.db')
c = conn.cursor()

# List all cache tables
print('\n✅ CACHE TABLES IN DATABASE:')
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%cache%'")
tables = c.fetchall()
for table in tables:
    print(f'   • {table[0]}')

# Count entries
print('\n📦 CACHED ENTRIES:')
c.execute('SELECT COUNT(*) FROM weather_cache')
weather_count = c.fetchone()[0]
print(f'   • Weather: {weather_count} entries')

c.execute('SELECT COUNT(*) FROM market_price_cache')
market_count = c.fetchone()[0]
print(f'   • Market Prices: {market_count} entries')

c.execute('SELECT COUNT(*) FROM prediction_cache')
pred_count = c.fetchone()[0]
print(f'   • Predictions: {pred_count} entries')

print(f'\n   📊 TOTAL: {weather_count + market_count + pred_count} cached items')

# Show sample data
if weather_count > 0:
    print('\n🌤️ WEATHER CACHE SAMPLE:')
    c.execute('SELECT location, cached_at, expires_at FROM weather_cache LIMIT 3')
    for row in c.fetchall():
        print(f'   Location: {row[0]}')
        print(f'   Cached: {row[1][:19]}')
        print(f'   Expires: {row[2][:19]}')
        print()

if market_count > 0:
    print('💰 MARKET PRICE CACHE SAMPLE:')
    c.execute('SELECT crop_name, location, cached_at, expires_at FROM market_price_cache LIMIT 3')
    for row in c.fetchall():
        print(f'   Crop: {row[0]} in {row[1]}')
        print(f'   Cached: {row[2][:19]}')
        print(f'   Expires: {row[3][:19]}')
        print()

if pred_count > 0:
    print('🤖 PREDICTION CACHE SAMPLE:')
    c.execute('SELECT crop_name, location, reference_price, cached_at, expires_at FROM prediction_cache LIMIT 3')
    for row in c.fetchall():
        print(f'   Crop: {row[0]} in {row[1]} (₹{row[2]})')
        print(f'   Cached: {row[3][:19]}')
        print(f'   Expires: {row[4][:19]}')
        print()

print('=' * 70)
print('\n⏰ CACHE EXPIRY TIMES:')
print('   • Weather: 6 hours')
print('   • Market Prices: 24 hours')
print('   • Predictions: 24 hours')
print('\n💡 Cache is automatically refreshed when expired!')

conn.close()


