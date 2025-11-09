import sqlite3
import pandas as pd

DB_NAME = 'farmermarket.db'

def get_connection():
    """Get a connection to the database"""
    return sqlite3.connect(DB_NAME)

def init_db():
    """Initializes the database file and creates tables if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Create Tools Table
    c.execute("""CREATE TABLE IF NOT EXISTS tools (
        Farmer TEXT,
        Location TEXT,
        Tool TEXT,
        Rate REAL,
        Contact TEXT,
        Notes TEXT
    )""")

    # Create Crops Table
    c.execute("""CREATE TABLE IF NOT EXISTS crops (
        Farmer TEXT,
        Location TEXT,
        Crop TEXT,
        Quantity TEXT,
        Expected_Price REAL,
        Contact TEXT,
        Listing_Date TEXT
    )""")

    # Create Farmers Table
    c.execute("""CREATE TABLE IF NOT EXISTS farmers (
        name TEXT PRIMARY KEY,
        location TEXT,
        farm_size REAL,
        farm_unit TEXT,
        contact TEXT,
        weather_location TEXT,
        latitude REAL,
        longitude REAL,
        password TEXT DEFAULT 'farmer123'
    )""")
    
    # Create Calendar Events Table
    c.execute("""CREATE TABLE IF NOT EXISTS calendar_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        farmer_name TEXT,
        event_date TEXT,
        event_time TEXT DEFAULT '09:00',
        event_title TEXT,
        event_description TEXT,
        weather_alert TEXT,
        created_at TEXT,
        FOREIGN KEY (farmer_name) REFERENCES farmers(name)
    )""")
    
    # Create User Onboarding Progress Table
    c.execute("""CREATE TABLE IF NOT EXISTS user_onboarding_progress (
        farmer_name TEXT PRIMARY KEY,
        profile_completed INTEGER DEFAULT 0,
        first_listing_created INTEGER DEFAULT 0,
        calendar_event_added INTEGER DEFAULT 0,
        weather_checked INTEGER DEFAULT 0,
        market_prices_viewed INTEGER DEFAULT 0,
        onboarding_dismissed INTEGER DEFAULT 0,
        last_updated TEXT,
        FOREIGN KEY (farmer_name) REFERENCES farmers(name)
    )""")
    
    conn.commit()
    conn.close()

def add_data(table_name, data_tuple):
    """Adds a new row of data to the specified SQLite table."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    if table_name == "tools":
        sql = "INSERT INTO tools (Farmer, Location, Tool, Rate, Contact, Notes) VALUES (?, ?, ?, ?, ?, ?)"
    elif table_name == "crops":
        sql = "INSERT INTO crops (Farmer, Location, Crop, Quantity, Expected_Price, Contact, Listing_Date) VALUES (?, ?, ?, ?, ?, ?, ?)"
    elif table_name == "farmers":
        sql = "INSERT OR REPLACE INTO farmers (name, location, farm_size, farm_unit, contact, weather_location, latitude, longitude, password) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    elif table_name == "calendar_events":
        sql = "INSERT INTO calendar_events (farmer_name, event_date, event_title, event_description, weather_alert, created_at) VALUES (?, ?, ?, ?, ?, ?)"
        
    c.execute(sql, data_tuple)
    conn.commit()
    conn.close()

def get_data(table_name):
    """Retrieves all data from the specified SQLite table and returns a Pandas DataFrame."""
    conn = sqlite3.connect(DB_NAME)
    # Using rowid allows us to uniquely identify rows, essential for update/delete later
    df = pd.read_sql_query(f"SELECT rowid, * FROM {table_name}", conn)
    conn.close()
    return df

def get_farmer_profile(name):
    """Retrieves a farmer's profile by name (case-insensitive)."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM farmers WHERE LOWER(name) = LOWER(?)", (name,))
    profile = c.fetchone()
    conn.close()
    return dict(profile) if profile else None

def verify_farmer_login(name, password):
    """Verify farmer login credentials."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM farmers WHERE LOWER(name) = LOWER(?) AND password = ?", (name, password))
    profile = c.fetchone()
    conn.close()
    return dict(profile) if profile else None

def get_farmer_events(farmer_name):
    """Retrieves all calendar events for a specific farmer (case-insensitive)."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(
        "SELECT * FROM calendar_events WHERE LOWER(farmer_name) = LOWER(?) ORDER BY event_date", 
        conn, 
        params=(farmer_name,)
    )
    conn.close()
    return df

def update_farmer_profile(name, location, farm_size, farm_unit, contact, weather_location, latitude, longitude):
    """Updates a farmer's profile (case-insensitive)."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        UPDATE farmers 
        SET location = ?, farm_size = ?, farm_unit = ?, contact = ?, 
            weather_location = ?, latitude = ?, longitude = ?
        WHERE LOWER(name) = LOWER(?)
    """, (location, farm_size, farm_unit, contact, weather_location, latitude, longitude, name))
    conn.commit()
    conn.close()

def delete_event(event_id):
    """Deletes a calendar event by ID."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM calendar_events WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()

def update_event(event_id, event_date, event_title, event_description, weather_alert):
    """Updates a calendar event by ID."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        UPDATE calendar_events
        SET event_date = ?, event_title = ?, event_description = ?, weather_alert = ?
        WHERE id = ?
    """, (event_date, event_title, event_description, weather_alert, event_id))
    conn.commit()
    conn.close()

def get_onboarding_progress(farmer_name):
    """Get onboarding progress for a farmer."""
    try:
        conn = sqlite3.connect(DB_NAME, timeout=30.0)
        conn.execute('PRAGMA journal_mode=WAL')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM user_onboarding_progress WHERE LOWER(farmer_name) = LOWER(?)", (farmer_name,))
        progress = c.fetchone()
        
        if progress:
            conn.close()
            return dict(progress)
        else:
            # Create initial progress record
            from datetime import datetime
            c.execute("""
                INSERT OR IGNORE INTO user_onboarding_progress 
                (farmer_name, profile_completed, first_listing_created, calendar_event_added, 
                 weather_checked, market_prices_viewed, onboarding_dismissed, last_updated)
                VALUES (?, 0, 0, 0, 0, 0, 0, ?)
            """, (farmer_name, datetime.now().isoformat()))
            conn.commit()
            conn.close()
            return {
                'farmer_name': farmer_name,
                'profile_completed': 0,
                'first_listing_created': 0,
                'calendar_event_added': 0,
                'weather_checked': 0,
                'market_prices_viewed': 0,
                'onboarding_dismissed': 0
            }
    except Exception as e:
        print(f"Error in get_onboarding_progress: {e}")
        return {
            'farmer_name': farmer_name,
            'profile_completed': 0,
            'first_listing_created': 0,
            'calendar_event_added': 0,
            'weather_checked': 0,
            'market_prices_viewed': 0,
            'onboarding_dismissed': 0
        }

def update_onboarding_progress(farmer_name, **kwargs):
    """Update onboarding progress fields."""
    from datetime import datetime
    try:
        conn = sqlite3.connect(DB_NAME, timeout=30.0)
        conn.execute('PRAGMA journal_mode=WAL')
        c = conn.cursor()
        
        # Build update query dynamically
        fields = []
        values = []
        for key, value in kwargs.items():
            fields.append(f"{key} = ?")
            values.append(value)
        
        if fields:
            fields.append("last_updated = ?")
            values.append(datetime.now().isoformat())
            values.append(farmer_name)
            
            query = f"UPDATE user_onboarding_progress SET {', '.join(fields)} WHERE LOWER(farmer_name) = LOWER(?)"
            c.execute(query, values)
            conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error updating onboarding progress: {e}")


