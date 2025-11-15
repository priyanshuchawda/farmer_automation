from weather.climate_analyzer import ClimateAnalyzer

# Test with Pune coordinates
analyzer = ClimateAnalyzer('Pune', 18.5204, 73.8567)
print('🔍 Testing Climate Analyzer...\n')

# Test drought risk
print('📊 DROUGHT RISK:')
drought = analyzer.get_drought_risk()
print(f'Score: {drought["score"]}/100')
print(f'Level: {drought["level"]}')
print(f'Days without rain: {drought["days_without_rain"]}')
print(f'Actions: {len(drought["actions"])} recommendations')
for i, action in enumerate(drought["actions"], 1):
    print(f'  {i}. {action}')

print('\n🌊 FLOOD RISK:')
flood = analyzer.get_flood_risk()
print(f'Score: {flood["score"]}/100')
print(f'Level: {flood["level"]}')

print('\n🔥 HEAT STRESS:')
heat = analyzer.get_heat_stress()
print(f'Score: {heat["score"]}/100')
print(f'Level: {heat["level"]}')

print('\n✅ All climate analyzers working!')
