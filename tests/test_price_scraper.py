import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import pandas as pd
from google import genai

# Load environment variables
load_dotenv()

print("=" * 70)
print("🧪 Testing Market Price Scraper & AI Integration")
print("=" * 70)

# Test 1: Check AI AI
print("\n1️⃣ Testing AI AI Connection...")
try:
    ai_client = genai.Client()
    print("✅ AI AI client initialized successfully")
except Exception as e:
    ai_client = None
    print(f"❌ AI AI failed: {e}")

# Test 2: Scrape Agmarknet
print("\n2️⃣ Testing Agmarknet Web Scraping...")
try:
    base_url = "https://agmarknet.gov.in/PriceAndArrivals/CommodityDailyStateWise.aspx"
    print(f"📡 Connecting to: {base_url}")
    
    response = requests.get(base_url, timeout=30)
    print(f"✅ Status Code: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        table = soup.find("table", {"class": "tableagmark_new"})
        
        if table:
            print("✅ Found data table!")
            rows = table.find_all("tr")[1:]  # skip header
            
            # Extract first 3 records
            data = []
            for row in rows[:3]:
                cols = [col.text.strip() for col in row.find_all("td")]
                if len(cols) >= 9:
                    data.append({
                        "State": cols[0],
                        "District": cols[1],
                        "Market": cols[2],
                        "Commodity": cols[3],
                        "Min Price": cols[6],
                        "Max Price": cols[7],
                        "Modal Price": cols[8],
                    })
            
            print(f"✅ Scraped {len(data)} sample records")
            
            # Display sample records
            print("\n📊 Sample Records:")
            for i, record in enumerate(data, 1):
                print(f"\n   Record {i}:")
                print(f"   State: {record['State']}")
                print(f"   Market: {record['Market']}")
                print(f"   Commodity: {record['Commodity']}")
                print(f"   Modal Price: ₹{record['Modal Price']}/qtl")
        else:
            print("❌ Data table not found on page")
            print("🔍 Checking page structure...")
            tables = soup.find_all("table")
            print(f"   Found {len(tables)} tables on page")
            
except requests.Timeout:
    print("❌ Connection timeout - Agmarknet server is slow")
except Exception as e:
    print(f"❌ Scraping error: {str(e)}")

# Test 3: AI Market Insights
if ai_client:
    print("\n3️⃣ Testing AI Market Insights...")
    try:
        test_price_data = {
            "min": 18,
            "modal": 22,
            "max": 26
        }
        
        prompt = f"""
As an agricultural market expert, analyze this price data:

Commodity: Tomato
Location: Pune, Maharashtra
Min Price: ₹{test_price_data['min']}/kg
Modal Price: ₹{test_price_data['modal']}/kg
Max Price: ₹{test_price_data['max']}/kg

Provide:
1. Brief price assessment (2 sentences)
2. Two selling recommendations
3. One action item

Keep it concise and practical for Indian farmers.
"""
        
        print("🤖 Asking AI for market insights...")
        response = ai_client.models.generate_content(
            model='AI-2.0-flash-exp',
            contents=prompt
        )
        
        print("✅ AI Response received!")
        print("\n" + "=" * 70)
        print("AI MARKET INSIGHTS:")
        print("=" * 70)
        print(response.text)
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ AI insights failed: {str(e)}")

# Test 4: AI Chat Assistant
if ai_client:
    print("\n4️⃣ Testing AI Chat Assistant...")
    try:
        test_question = "When is the best time to sell tomatoes in Maharashtra?"
        
        prompt = f"""
You are an expert agricultural market advisor for Indian farmers.

Farmer's Question: {test_question}

Provide a practical, short answer (3-4 sentences) in simple language.
"""
        
        print(f"💬 Question: {test_question}")
        print("🤖 AI is thinking...")
        
        response = ai_client.models.generate_content(
            model='AI-2.0-flash-exp',
            contents=prompt
        )
        
        print("✅ AI Response:")
        print("\n" + "-" * 70)
        print(response.text)
        print("-" * 70)
        
    except Exception as e:
        print(f"❌ AI chat failed: {str(e)}")

# Final Summary
print("\n" + "=" * 70)
print("📋 TEST SUMMARY")
print("=" * 70)
print(f"AI AI: {'✅ Working' if ai_client else '❌ Not Working'}")
print(f"Web Scraping: Check results above")
print(f"AI Insights: {'✅ Tested' if ai_client else '❌ Skipped'}")
print(f"AI Chat: {'✅ Tested' if ai_client else '❌ Skipped'}")
print("=" * 70)


