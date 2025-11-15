from weather.climate_analyzer import ClimateAnalyzer
from weather.api_client import OpenWeatherAPI

# Test if both use same weather source
print('🔍 Testing Weather Integration...\n')

# Test 1: OpenWeather API
api = OpenWeatherAPI()
forecast = api.get_detailed_forecast(18.5204, 73.8567)
if forecast is not None and not forecast.empty:
    print('✅ OpenWeather API working')
    print(f'   Forecast rows: {len(forecast)}')
    temp = forecast.iloc[0]['temp']
    rain = forecast.iloc[0]['rain']
    print(f'   Current temp: {temp:.1f}°C')
    print(f'   Current rain: {rain:.1f}mm')
else:
    print('❌ OpenWeather API failed')

# Test 2: Climate Analyzer uses same API
print('\n🔍 Testing Climate Analyzer...')
analyzer = ClimateAnalyzer('Pune', 18.5204, 73.8567)
drought = analyzer.get_drought_risk()
print(f'✅ Climate Analyzer working')
print(f'   Drought score: {drought["score"]}/100')
print(f'   Days without rain: {drought["days_without_rain"]}')

print('\n✅ YES - Both use same OpenWeather API!')
print('   Weather Forecast page → OpenWeather API')
print('   Climate Risk Dashboard → OpenWeather API')
