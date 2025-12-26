#!/usr/bin/env python3
"""Add demo listings for farmer 'chandan' for testing."""

import sqlite3
from datetime import datetime

import os; DB_NAME = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'farmermarket.db')

def add_chandan_listings():
    """Add sample listings for chandan."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Check if chandan exists in farmers table
    c.execute("SELECT name FROM farmers WHERE LOWER(name) = 'chandan'")
    chandan_exists = c.fetchone()
    
    if not chandan_exists:
        print("Creating farmer profile for 'chandan'...")
        c.execute("""
            INSERT INTO farmers (name, location, farm_size, farm_unit, contact, weather_location, latitude, longitude, password)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ('chandan', 'Pune', 5.5, 'Acres', '9876543210', 'Pune', 18.5204, 73.8567, 'farmer123'))
        print("✅ Created farmer profile for chandan")
    else:
        print("✓ Farmer 'chandan' already exists")
    
    # Add tool listings
    tools = [
        ('chandan', 'Pune', 'Tractor', 800, '9876543210', 'John Deere 5310, good condition, available for rent'),
        ('chandan', 'Pune', 'Sprayer', 150, '9876543210', 'Manual sprayer, 16 liter capacity, perfect for pesticides'),
        ('chandan', 'Pune', 'Harvester', 1200, '9876543210', 'Mini harvester for wheat and paddy, well maintained'),
        ('chandan', 'Pune', 'Plow', 300, '9876543210', 'Disc plow, suitable for all soil types'),
    ]
    
    print("\nAdding tool listings for chandan...")
    for tool in tools:
        try:
            c.execute("""
                INSERT INTO tools (Farmer, Location, Tool, Rate, Contact, Notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, tool)
            print(f"  ✅ Added {tool[2]} - ₹{tool[3]}/day")
        except Exception as e:
            print(f"  ⚠️ {tool[2]} might already exist: {e}")
    
    # Add crop listings
    crops = [
        ('chandan', 'Pune', 'Wheat', '20 Quintals', 2200, '9876543210', datetime.now().strftime("%Y-%m-%d")),
        ('chandan', 'Pune', 'Rice', '15 Quintals', 3500, '9876543210', datetime.now().strftime("%Y-%m-%d")),
        ('chandan', 'Pune', 'Tomatoes', '500 Kilograms', 25, '9876543210', datetime.now().strftime("%Y-%m-%d")),
        ('chandan', 'Pune', 'Onions', '1000 Kilograms', 20, '9876543210', datetime.now().strftime("%Y-%m-%d")),
        ('chandan', 'Pune', 'Cotton', '10 Quintals', 5800, '9876543210', datetime.now().strftime("%Y-%m-%d")),
    ]
    
    print("\nAdding crop listings for chandan...")
    for crop in crops:
        try:
            c.execute("""
                INSERT INTO crops (Farmer, Location, Crop, Quantity, Expected_Price, Contact, Listing_Date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, crop)
            print(f"  ✅ Added {crop[2]} - {crop[3]} @ ₹{crop[4]}/unit")
        except Exception as e:
            print(f"  ⚠️ {crop[2]} might already exist: {e}")
    
    conn.commit()
    
    # Add some ratings for chandan's listings
    print("\n🌟 Adding sample ratings for chandan's listings...")
    
    # Get chandan's tool and crop IDs
    c.execute("SELECT rowid FROM tools WHERE LOWER(Farmer) = 'chandan' LIMIT 2")
    chandan_tools = [row[0] for row in c.fetchall()]
    
    c.execute("SELECT rowid FROM crops WHERE LOWER(Farmer) = 'chandan' LIMIT 3")
    chandan_crops = [row[0] for row in c.fetchall()]
    
    # Get some other farmers as raters
    c.execute("SELECT name FROM farmers WHERE LOWER(name) != 'chandan' LIMIT 5")
    raters = [row[0] for row in c.fetchall()]
    
    ratings_data = [
        # Tool ratings
        ('tool', chandan_tools[0] if chandan_tools else 1, 'chandan', raters[0] if raters else 'TestFarmer', 5, 'Excellent tractor! Very reliable!'),
        ('tool', chandan_tools[0] if chandan_tools else 1, 'chandan', raters[1] if len(raters) > 1 else 'John Farmer', 4, 'Good quality, reasonable price'),
        ('tool', chandan_tools[1] if len(chandan_tools) > 1 else 1, 'chandan', raters[2] if len(raters) > 2 else 'Jane Farmer', 5, 'Perfect sprayer for my farm!'),
        
        # Crop ratings
        ('crop', chandan_crops[0] if chandan_crops else 1, 'chandan', raters[3] if len(raters) > 3 else 'Rajesh Patil', 5, 'Top quality wheat! Highly recommended!'),
        ('crop', chandan_crops[1] if len(chandan_crops) > 1 else 1, 'chandan', raters[4] if len(raters) > 4 else 'Vitthal Shelar', 4, 'Good rice quality'),
        ('crop', chandan_crops[2] if len(chandan_crops) > 2 else 1, 'chandan', raters[0] if raters else 'TestFarmer', 5, 'Fresh tomatoes, great deal!'),
    ]
    
    for rating in ratings_data:
        try:
            c.execute("""
                INSERT INTO ratings (listing_type, listing_id, seller_name, rater_name, stars, comment)
                VALUES (?, ?, ?, ?, ?, ?)
            """, rating)
            print(f"  ⭐{'⭐' * rating[4]} {rating[3]} rated chandan's {rating[0]}")
        except Exception as e:
            print(f"  ⚠️ Rating might already exist: {e}")
    
    # Update chandan's average rating
    c.execute("""
        SELECT COUNT(*) as total, AVG(stars) as avg 
        FROM ratings 
        WHERE LOWER(seller_name) = 'chandan'
    """)
    result = c.fetchone()
    total_ratings = result[0] if result else 0
    avg_rating = result[1] if result else 0.0
    
    c.execute("""
        UPDATE farmers 
        SET total_ratings = ?, avg_rating = ? 
        WHERE LOWER(name) = 'chandan'
    """, (total_ratings, avg_rating))
    
    conn.commit()
    conn.close()
    
    print(f"\n📊 Chandan's final rating: {avg_rating:.1f}/5 stars ({total_ratings} reviews)")
    print("\n✅ Successfully added demo listings for 'chandan'!")
    print("\n🎯 Login as 'chandan' with password 'farmer123' to see these listings!")

if __name__ == "__main__":
    print("=" * 70)
    print("📦 ADDING DEMO LISTINGS FOR CHANDAN")
    print("=" * 70)
    print()
    
    add_chandan_listings()
    
    print()
    print("=" * 70)
    print("🎉 DONE! Now run: streamlit run app.py")
    print("=" * 70)
