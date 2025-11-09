from weather.combined_forecast import get_weather_forecast
from datetime import datetime

print('Current system date:', datetime.now())
print('\n--- Testing weather forecast ---')

# Test with coordinates (chandiya gujarat)
forecast = get_weather_forecast('chandiya gujarat', lat=23.088338, lon=69.846525)

if forecast:
    print(f'\nGot {len(forecast)} days of forecast:')
    for day in forecast:
        print(f"Date: {day['date']}, Temp: {day['temperature']}°C, Rain: {day['rainfall']}mm, Wind: {day['wind_speed']} km/h")
else:
    print('No forecast data received!')


