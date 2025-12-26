"""Database migration script to add new columns and tables"""

import sqlite3

import os; DB_NAME = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'farmermarket.db')

def migrate_database():
    """Add new columns to existing farmers table and create calendar_events table"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    print("Starting database migration...")
    
    # Check if columns exist
    c.execute("PRAGMA table_info(farmers)")
    columns = [col[1] for col in c.fetchall()]
    
    # Add new columns if they don't exist
    if 'weather_location' not in columns:
        print("Adding 'weather_location' column...")
        c.execute("ALTER TABLE farmers ADD COLUMN weather_location TEXT")
    
    if 'latitude' not in columns:
        print("Adding 'latitude' column...")
        c.execute("ALTER TABLE farmers ADD COLUMN latitude REAL")
    
    if 'longitude' not in columns:
        print("Adding 'longitude' column...")
        c.execute("ALTER TABLE farmers ADD COLUMN longitude REAL")
    
    # Create calendar_events table if it doesn't exist
    print("Creating 'calendar_events' table...")
    c.execute("""CREATE TABLE IF NOT EXISTS calendar_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farmer_name TEXT,
        event_date TEXT,
        event_title TEXT,
        event_description TEXT,
        weather_alert TEXT,
        created_at TEXT,
        FOREIGN KEY (farmer_name) REFERENCES farmers(name)
    )""")
    
    conn.commit()
    conn.close()
    
    print("✅ Database migration completed successfully!")

if __name__ == "__main__":
    migrate_database()


