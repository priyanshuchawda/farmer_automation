import requests
from bs4 import BeautifulSoup

print("🔍 Analyzing Agmarknet Page Structure...\n")

try:
    url = "https://agmarknet.gov.in/PriceAndArrivals/CommodityDailyStateWise.aspx"
    response = requests.get(url, timeout=30)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        
        # Check for all tables
        tables = soup.find_all("table")
        print(f"Found {len(tables)} tables\n")
        
        # Check for table classes
        for i, table in enumerate(tables[:5], 1):
            print(f"Table {i}:")
            print(f"  Class: {table.get('class')}")
            print(f"  ID: {table.get('id')}")
            rows = table.find_all("tr")
            print(f"  Rows: {len(rows)}")
            if rows:
                cols = rows[0].find_all(['th', 'td'])
                print(f"  First row columns: {len(cols)}")
            print()
        
        # Look for any divs with data
        print("\n🔍 Checking for data containers...")
        data_divs = soup.find_all("div", {"class": lambda x: x and "data" in x.lower()})
        print(f"Found {len(data_divs)} data divs")
        
        # Check if it's an ASP.NET page with ViewState
        viewstate = soup.find("input", {"id": "__VIEWSTATE"})
        if viewstate:
            print("\n⚠️ This is an ASP.NET page - requires form submission")
            print("   May need different scraping approach")
        
        # Save HTML for inspection
        with open("agmarknet_page.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())
        print("\n✅ Page HTML saved to 'agmarknet_page.html' for inspection")
        
except Exception as e:
    print(f"❌ Error: {e}")


