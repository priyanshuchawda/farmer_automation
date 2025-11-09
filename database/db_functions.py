import sqlite3
import pandas as pd

DB_NAME = 'farmermarket.db'

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
        longitude REAL
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
        sql = "INSERT OR REPLACE INTO farmers (name, location, farm_size, farm_unit, contact, weather_location, latitude, longitude) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
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