import requests

BASE = 'https://api.ceda.ashoka.edu.in/v1'
H = {'Authorization': 'Bearer 0690a8ea7cd6986959695fa658783ca8244ff1999766b34dcb3d0d6c84d1e31b'}

# Try state-level data (no district/market filter)
r = requests.post(BASE+'/agmarknet/prices', headers=H, json={
    'commodity_id': 23,  # Onion
    'state_id': 27,  # Maharashtra
    'from_date': '2024-06-01',
    'to_date': '2025-11-09'
})

d = r.json()['output']['data']
print(f'✅ Found {len(d)} records at state level!')

if d:
    print('\n📊 Sample records:')
    for rec in d[:10]:
        print(f"  {rec['date']}: ₹{rec['modal_price']}/qtl (₹{rec['modal_price']/100:.2f}/kg)")
    
    print(f'\n💰 Average modal price: ₹{sum(r["modal_price"] for r in d)/len(d):.2f}/qtl')
    print('🎉 CEDA API IS WORKING!')
else:
    print('❌ No data for this combination')


