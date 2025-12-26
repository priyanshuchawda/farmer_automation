"""
View all populated data from the database
Shows farmers, tools, crops, and calendar events in a readable format
"""

import sqlite3
import pandas as pd

import os; DB_NAME = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'farmermarket.db')

def view_all_data():
    """Display all populated data"""
    conn = sqlite3.connect(DB_NAME)
    
    print("="*80)
    print("🌾 MAHARASHTRA FARMER DATABASE - COMPLETE DATA VIEW")
    print("="*80)
    
    # Farmers
    print("\n" + "="*80)
    print("👨‍🌾 FARMERS (Total: {})".format(pd.read_sql_query("SELECT COUNT(*) as count FROM farmers", conn)['count'][0]))
    print("="*80)
    
    farmers_df = pd.read_sql_query("""
        SELECT name, location, farm_size, farm_unit, contact, 
               ROUND(latitude, 4) as lat, ROUND(longitude, 4) as lon
        FROM farmers 
        ORDER BY location, name
    """, conn)
    
    print(farmers_df.to_string(index=False))
    
    # Tools
    print("\n\n" + "="*80)
    print("🔧 TOOLS FOR RENT (Total: {})".format(pd.read_sql_query("SELECT COUNT(*) as count FROM tools", conn)['count'][0]))
    print("="*80)
    
    tools_df = pd.read_sql_query("""
        SELECT Farmer, Location, Tool, Rate as 'Rate/Day (₹)', Contact, Notes
        FROM tools 
        ORDER BY Location, Tool
        LIMIT 50
    """, conn)
    
    print(tools_df.to_string(index=False))
    print("\n... (showing first 50 entries)")
    
    # Crops
    print("\n\n" + "="*80)
    print("🌾 CROPS FOR SALE (Total: {})".format(pd.read_sql_query("SELECT COUNT(*) as count FROM crops", conn)['count'][0]))
    print("="*80)
    
    crops_df = pd.read_sql_query("""
        SELECT Farmer, Location, Crop, Quantity, Expected_Price as 'Price/Quintal (₹)', 
               Contact, Listing_Date
        FROM crops 
        ORDER BY Listing_Date DESC
    """, conn)
    
    print(crops_df.to_string(index=False))
    
    # Calendar Events
    print("\n\n" + "="*80)
    print("📅 CALENDAR EVENTS (Total: {})".format(pd.read_sql_query("SELECT COUNT(*) as count FROM calendar_events", conn)['count'][0]))
    print("="*80)
    
    events_df = pd.read_sql_query("""
        SELECT farmer_name as Farmer, event_date as Date, event_time as Time, 
               event_title as Activity, event_description as Description
        FROM calendar_events 
        ORDER BY event_date, event_time
        LIMIT 30
    """, conn)
    
    print(events_df.to_string(index=False))
    print("\n... (showing first 30 entries)")
    
    # Statistics by location
    print("\n\n" + "="*80)
    print("📊 STATISTICS BY LOCATION")
    print("="*80)
    
    stats_df = pd.read_sql_query("""
        SELECT 
            f.location as Location,
            COUNT(DISTINCT f.name) as Farmers,
            COUNT(DISTINCT t.Tool) as 'Tools Listed',
            COUNT(DISTINCT c.Crop) as 'Crops Listed'
        FROM farmers f
        LEFT JOIN tools t ON f.name = t.Farmer
        LEFT JOIN crops c ON f.name = c.Farmer
        GROUP BY f.location
        ORDER BY Farmers DESC
        LIMIT 15
    """, conn)
    
    print(stats_df.to_string(index=False))
    
    # Popular tools
    print("\n\n" + "="*80)
    print("🔧 MOST AVAILABLE TOOLS")
    print("="*80)
    
    popular_tools = pd.read_sql_query("""
        SELECT Tool, COUNT(*) as 'Available', 
               ROUND(AVG(Rate), 0) as 'Avg Rate/Day (₹)',
               MIN(Rate) as 'Min Rate (₹)',
               MAX(Rate) as 'Max Rate (₹)'
        FROM tools
        GROUP BY Tool
        ORDER BY COUNT(*) DESC
    """, conn)
    
    print(popular_tools.to_string(index=False))
    
    # Popular crops
    print("\n\n" + "="*80)
    print("🌾 CROPS IN MARKET")
    print("="*80)
    
    popular_crops = pd.read_sql_query("""
        SELECT Crop, COUNT(*) as 'Listings',
               ROUND(AVG(Expected_Price), 0) as 'Avg Price/Quintal (₹)',
               MIN(Expected_Price) as 'Min Price (₹)',
               MAX(Expected_Price) as 'Max Price (₹)'
        FROM crops
        GROUP BY Crop
        ORDER BY COUNT(*) DESC
    """, conn)
    
    print(popular_crops.to_string(index=False))
    
    print("\n" + "="*80)
    print("✅ DATA VIEW COMPLETE")
    print("="*80)
    print("\n💡 Login Credentials:")
    print("   Username: Any farmer name from above (e.g., 'Ramesh Patil')")
    print("   Password: farmer123")
    
    conn.close()

if __name__ == "__main__":
    view_all_data()
