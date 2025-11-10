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
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Farmer TEXT,
        Location TEXT,
        Tool TEXT,
        Rate REAL,
        Contact TEXT,
        Notes TEXT,
        Photo TEXT,
        Created_Date TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    # Create Crops Table
    c.execute("""CREATE TABLE IF NOT EXISTS crops (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Farmer TEXT,
        Location TEXT,
        Crop TEXT,
        Quantity TEXT,
        Expected_Price REAL,
        Contact TEXT,
        Listing_Date TEXT,
        Photo TEXT,
        Created_Date TEXT DEFAULT CURRENT_TIMESTAMP
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
        password TEXT DEFAULT 'farmer123',
        created_date TEXT DEFAULT CURRENT_TIMESTAMP,
        total_ratings INTEGER DEFAULT 0,
        avg_rating REAL DEFAULT 0.0
    )""")
    
    # Create Ratings Table
    c.execute("""CREATE TABLE IF NOT EXISTS ratings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        listing_type TEXT NOT NULL,
        listing_id INTEGER NOT NULL,
        seller_name TEXT NOT NULL,
        rater_name TEXT NOT NULL,
        stars INTEGER NOT NULL,
        comment TEXT,
        created_date TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (seller_name) REFERENCES farmers(name)
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
    
    # Create Labor/Worker Jobs Table
    c.execute("""CREATE TABLE IF NOT EXISTS labor_jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        posted_by TEXT NOT NULL,
        location TEXT NOT NULL,
        work_type TEXT NOT NULL,
        workers_needed INTEGER NOT NULL,
        duration_days INTEGER NOT NULL,
        wage_per_day REAL NOT NULL,
        contact TEXT NOT NULL,
        description TEXT,
        start_date TEXT,
        status TEXT DEFAULT 'Open',
        created_date TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (posted_by) REFERENCES farmers(name)
    )""")
    
    # Create Worker Availability Table
    c.execute("""CREATE TABLE IF NOT EXISTS worker_availability (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        worker_name TEXT NOT NULL,
        location TEXT NOT NULL,
        skills TEXT NOT NULL,
        wage_expected REAL NOT NULL,
        contact TEXT NOT NULL,
        experience_years INTEGER,
        availability_status TEXT DEFAULT 'Available',
        description TEXT,
        created_date TEXT DEFAULT CURRENT_TIMESTAMP
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
        # Updated to include photo - backward compatible (photo can be None)
        if len(data_tuple) == 7:
            sql = "INSERT INTO tools (Farmer, Location, Tool, Rate, Contact, Notes, Photo) VALUES (?, ?, ?, ?, ?, ?, ?)"
        else:
            sql = "INSERT INTO tools (Farmer, Location, Tool, Rate, Contact, Notes) VALUES (?, ?, ?, ?, ?, ?)"
    elif table_name == "crops":
        # Updated to include photo - backward compatible
        if len(data_tuple) == 8:
            sql = "INSERT INTO crops (Farmer, Location, Crop, Quantity, Expected_Price, Contact, Listing_Date, Photo) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        else:
            sql = "INSERT INTO crops (Farmer, Location, Crop, Quantity, Expected_Price, Contact, Listing_Date) VALUES (?, ?, ?, ?, ?, ?, ?)"
    elif table_name == "farmers":
        sql = "INSERT OR REPLACE INTO farmers (name, location, farm_size, farm_unit, contact, weather_location, latitude, longitude, password) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    elif table_name == "calendar_events":
        sql = "INSERT INTO calendar_events (farmer_name, event_date, event_time, event_title, event_description, weather_alert, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)"
    elif table_name == "labor_jobs":
        sql = "INSERT INTO labor_jobs (posted_by, location, work_type, workers_needed, duration_days, wage_per_day, contact, description, start_date, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    elif table_name == "worker_availability":
        sql = "INSERT INTO worker_availability (worker_name, location, skills, wage_expected, contact, experience_years, availability_status, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        
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
    c.execute("SELECT ROWID as id, * FROM farmers WHERE LOWER(name) = LOWER(?)", (name,))
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

def update_farmer_location(farmer_name, location, latitude, longitude):
    """Update farmer's location and coordinates."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        UPDATE farmers
        SET location = ?, weather_location = ?, latitude = ?, longitude = ?
        WHERE LOWER(name) = LOWER(?)
    """, (location, location, latitude, longitude, farmer_name))
    conn.commit()
    conn.close()


# ========================================
# RATING SYSTEM FUNCTIONS
# ========================================

def add_rating(listing_type, listing_id, seller_name, rater_name, stars, comment=""):
    """Add a rating for a listing/seller."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO ratings (listing_type, listing_id, seller_name, rater_name, stars, comment)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (listing_type, listing_id, seller_name, rater_name, stars, comment))
    conn.commit()
    
    # Update farmer's average rating
    update_farmer_rating(seller_name)
    conn.close()


def get_ratings_for_seller(seller_name):
    """Get all ratings for a specific seller."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("""
        SELECT * FROM ratings 
        WHERE LOWER(seller_name) = LOWER(?) 
        ORDER BY created_date DESC
    """, conn, params=(seller_name,))
    conn.close()
    return df


def get_ratings_for_listing(listing_type, listing_id):
    """Get all ratings for a specific listing."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("""
        SELECT * FROM ratings 
        WHERE listing_type = ? AND listing_id = ? 
        ORDER BY created_date DESC
    """, conn, params=(listing_type, listing_id))
    conn.close()
    return df


def update_farmer_rating(farmer_name):
    """Update farmer's average rating based on all their ratings."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Calculate average rating
    c.execute("""
        SELECT COUNT(*) as total, AVG(stars) as avg 
        FROM ratings 
        WHERE LOWER(seller_name) = LOWER(?)
    """, (farmer_name,))
    
    result = c.fetchone()
    total_ratings = result[0] if result else 0
    avg_rating = result[1] if result else 0.0
    
    # Update farmer profile
    c.execute("""
        UPDATE farmers 
        SET total_ratings = ?, avg_rating = ? 
        WHERE LOWER(name) = LOWER(?)
    """, (total_ratings, avg_rating, farmer_name))
    
    conn.commit()
    conn.close()


def get_farmer_rating(farmer_name):
    """Get farmer's rating statistics."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        SELECT total_ratings, avg_rating 
        FROM farmers 
        WHERE LOWER(name) = LOWER(?)
    """, (farmer_name,))
    
    result = c.fetchone()
    conn.close()
    
    if result:
        return {
            'total_ratings': result[0] if result[0] else 0,
            'avg_rating': result[1] if result[1] else 0.0
        }
    return {'total_ratings': 0, 'avg_rating': 0.0}


def has_user_rated_listing(rater_name, listing_type, listing_id):
    """Check if user has already rated a listing."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        SELECT COUNT(*) FROM ratings 
        WHERE LOWER(rater_name) = LOWER(?) 
        AND listing_type = ? AND listing_id = ?
    """, (rater_name, listing_type, listing_id))
    count = c.fetchone()[0]
    conn.close()
    return count > 0


