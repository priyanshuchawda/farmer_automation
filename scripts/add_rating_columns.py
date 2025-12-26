#!/usr/bin/env python3
"""Migration script to add rating columns to farmers table."""

import sqlite3

import os; DB_NAME = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'farmermarket.db')

def add_rating_columns():
    """Add total_ratings and avg_rating columns to farmers table if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    try:
        # Check if columns exist
        c.execute("PRAGMA table_info(farmers)")
        columns = [col[1] for col in c.fetchall()]
        
        # Add total_ratings column if it doesn't exist
        if 'total_ratings' not in columns:
            print("Adding total_ratings column...")
            c.execute("ALTER TABLE farmers ADD COLUMN total_ratings INTEGER DEFAULT 0")
            print("✅ Added total_ratings column")
        else:
            print("✓ total_ratings column already exists")
        
        # Add avg_rating column if it doesn't exist
        if 'avg_rating' not in columns:
            print("Adding avg_rating column...")
            c.execute("ALTER TABLE farmers ADD COLUMN avg_rating REAL DEFAULT 0.0")
            print("✅ Added avg_rating column")
        else:
            print("✓ avg_rating column already exists")
        
        conn.commit()
        print("\n✅ Database migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("🔄 Starting database migration...\n")
    add_rating_columns()
