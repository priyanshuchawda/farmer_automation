import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

print("=" * 70)
print("🧪 Testing AI with Google Search for Market Prices")
print("=" * 70)

# Initialize AI with Google Search
try:
    client = genai.Client()
    print("✅ AI AI client initialized")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Test 1: Search for current market prices
print("\n1️⃣ Testing: Current market price search...")
query = "What is the current market price of tomatoes in Pune Maharashtra today? Give me the mandi price in rupees per kg"

try:
    print(f"🔍 Query: {query}")
    print("🤖 AI searching...")
    
    response = client.models.generate_content(
        model='AI-2.0-flash-exp',
        contents=query,
        config={
            'tools': [{'google_search': {}}],  # Enable Google Search
        }
    )
    
    print("\n✅ Response:")
    print("=" * 70)
    print(response.text)
    print("=" * 70)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Search for specific location
print("\n\n2️⃣ Testing: Location-specific price search...")
query2 = "Find today's onion prices in Mumbai mandis. What is the wholesale price per kg?"

try:
    print(f"🔍 Query: {query2}")
    print("🤖 AI searching...")
    
    response = client.models.generate_content(
        model='AI-2.0-flash-exp',
        contents=query2,
        config={
            'tools': [{'google_search': {}}],
        }
    )
    
    print("\n✅ Response:")
    print("=" * 70)
    print(response.text)
    print("=" * 70)
    
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: With farmer context
print("\n\n3️⃣ Testing: Farmer-specific query with advice...")
query3 = """
I am a farmer in Nashik, Maharashtra. I want to sell my tomatoes tomorrow.
Please search for:
1. Current tomato mandi prices in Nashik
2. Tell me if it's a good price to sell
3. Give me specific advice
"""

try:
    print(f"🔍 Query: Farmer asking about selling tomatoes in Nashik")
    print("🤖 AI searching and analyzing...")
    
    response = client.models.generate_content(
        model='AI-2.0-flash-exp',
        contents=query3,
        config={
            'tools': [{'google_search': {}}],
        }
    )
    
    print("\n✅ Response:")
    print("=" * 70)
    print(response.text)
    print("=" * 70)
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 70)
print("✅ TEST COMPLETE")
print("=" * 70)


