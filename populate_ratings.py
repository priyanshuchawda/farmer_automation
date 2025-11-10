#!/usr/bin/env python3
"""Script to populate database with random ratings for existing listings."""

import sqlite3
import random
from datetime import datetime, timedelta

DB_NAME = 'farmermarket.db'

# Sample review comments by rating
COMMENTS = {
    5: [
        "Excellent quality! Highly recommended!",
        "Very satisfied with the product and service!",
        "Great seller! Will buy again!",
        "Perfect condition! Very happy!",
        "Outstanding! Best in the market!",
        "Amazing quality and fair price!",
        "Very reliable seller!",
        "Superb! Exceeded expectations!"
    ],
    4: [
        "Good quality overall!",
        "Satisfied with the purchase!",
        "Nice product, good seller!",
        "Pretty good! Would recommend!",
        "Good experience!",
        "Very good quality!",
        "Happy with the deal!"
    ],
    3: [
        "Average quality, okay price",
        "Decent product",
        "It's okay, nothing special",
        "Fair deal",
        "Good enough for the price",
        "Acceptable quality"
    ],
    2: [
        "Below expectations",
        "Not very good quality",
        "Could be better",
        "Not satisfied",
        "Quality needs improvement"
    ],
    1: [
        "Very poor quality",
        "Disappointed with the product",
        "Not as described",
        "Would not recommend"
    ]
}

def get_all_listings():
    """Get all tools and crops listings."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Get all tools (using rowid as id)
    c.execute("SELECT rowid, Farmer FROM tools")
    tools = [{'type': 'tool', 'id': row[0], 'seller': row[1]} for row in c.fetchall()]
    
    # Get all crops (using rowid as id)
    c.execute("SELECT rowid, Farmer FROM crops")
    crops = [{'type': 'crop', 'id': row[0], 'seller': row[1]} for row in c.fetchall()]
    
    # Get all farmers (potential raters)
    c.execute("SELECT name FROM farmers")
    farmers = [row[0] for row in c.fetchall()]
    
    conn.close()
    
    return tools + crops, farmers

def add_random_ratings(num_ratings_per_listing=None):
    """Add random ratings to existing listings."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    listings, farmers = get_all_listings()
    
    if not listings:
        print("❌ No listings found in database!")
        return
    
    if not farmers:
        print("❌ No farmers found in database!")
        return
    
    print(f"📊 Found {len(listings)} listings and {len(farmers)} farmers\n")
    
    ratings_added = 0
    
    for listing in listings:
        listing_type = listing['type']
        listing_id = listing['id']
        seller_name = listing['seller']
        
        # Random number of ratings per listing (2-8)
        if num_ratings_per_listing is None:
            num_ratings = random.randint(2, 8)
        else:
            num_ratings = num_ratings_per_listing
        
        # Get random raters (excluding the seller)
        potential_raters = [f for f in farmers if f.lower() != seller_name.lower()]
        
        if not potential_raters:
            print(f"⚠️ No potential raters for {seller_name}'s {listing_type}")
            continue
        
        # Ensure we don't try to get more raters than available
        num_ratings = min(num_ratings, len(potential_raters))
        raters = random.sample(potential_raters, num_ratings)
        
        for rater_name in raters:
            # Check if this rater already rated this listing
            c.execute("""
                SELECT COUNT(*) FROM ratings 
                WHERE listing_type = ? AND listing_id = ? AND LOWER(rater_name) = LOWER(?)
            """, (listing_type, listing_id, rater_name))
            
            if c.fetchone()[0] > 0:
                continue  # Skip if already rated
            
            # Generate weighted random rating (more 4s and 5s)
            stars = random.choices(
                [1, 2, 3, 4, 5],
                weights=[5, 10, 15, 35, 35],  # Weighted towards higher ratings
                k=1
            )[0]
            
            # Pick random comment for this rating
            comment = random.choice(COMMENTS[stars])
            
            # Random date within last 60 days
            days_ago = random.randint(0, 60)
            created_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")
            
            # Insert rating
            c.execute("""
                INSERT INTO ratings (listing_type, listing_id, seller_name, rater_name, stars, comment, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (listing_type, listing_id, seller_name, rater_name, stars, comment, created_date))
            
            ratings_added += 1
            
            emoji = "⭐" * stars
            print(f"{emoji} {rater_name} rated {seller_name}'s {listing_type} #{listing_id}: {stars}/5")
    
    conn.commit()
    
    # Update all farmer ratings
    print(f"\n🔄 Updating farmer rating statistics...")
    
    unique_sellers = set(listing['seller'] for listing in listings)
    for seller in unique_sellers:
        # Calculate average rating
        c.execute("""
            SELECT COUNT(*) as total, AVG(stars) as avg 
            FROM ratings 
            WHERE LOWER(seller_name) = LOWER(?)
        """, (seller,))
        
        result = c.fetchone()
        total_ratings = result[0] if result else 0
        avg_rating = result[1] if result else 0.0
        
        # Update farmer profile
        c.execute("""
            UPDATE farmers 
            SET total_ratings = ?, avg_rating = ? 
            WHERE LOWER(name) = LOWER(?)
        """, (total_ratings, avg_rating, seller))
        
        if total_ratings > 0:
            print(f"📊 {seller}: {avg_rating:.1f}/5 stars ({total_ratings} reviews)")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Successfully added {ratings_added} ratings!")
    print(f"✅ Updated ratings for {len(unique_sellers)} sellers!")

def clear_all_ratings():
    """Clear all existing ratings (for testing)."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute("DELETE FROM ratings")
    c.execute("UPDATE farmers SET total_ratings = 0, avg_rating = 0.0")
    
    conn.commit()
    conn.close()
    
    print("🗑️ All ratings cleared!")

if __name__ == "__main__":
    import sys
    
    print("🎲 RATING POPULATION SCRIPT\n")
    print("=" * 60)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--clear":
        print("\n⚠️ Clearing all existing ratings...\n")
        clear_all_ratings()
    
    print("\n🔄 Adding random ratings to listings...\n")
    add_random_ratings()
    
    print("\n" + "=" * 60)
    print("🎉 DONE! Your marketplace now has realistic ratings!")
    print("\nRun your app with: streamlit run app.py")
