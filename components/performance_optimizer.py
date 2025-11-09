"""
Performance Optimizer - Database indexing, query optimization, lazy loading
"""
import sqlite3
import streamlit as st
from functools import wraps
from time import time
import hashlib


def create_database_indexes():
    """Create indexes for frequently queried columns"""
    conn = sqlite3.connect('farmermarket.db')
    cursor = conn.cursor()
    
    # Farmers table indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_farmers_phone ON farmers(phone)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_farmers_location ON farmers(location)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_farmers_district ON farmers(district)')
    
    # Tool listings indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tools_farmer_id ON tool_listings(farmer_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tools_district ON tool_listings(district)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tools_category ON tool_listings(category)')
    
    # Crop listings indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_crops_farmer_id ON crop_listings(farmer_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_crops_district ON crop_listings(district)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_crops_category ON crop_listings(category)')
    
    # Weather cache indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_weather_location ON weather_cache(location)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_weather_expires ON weather_cache(expires_at)')
    
    # Price cache indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_price_commodity ON price_cache(commodity)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_price_market ON price_cache(market)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_price_expires ON price_cache(expires_at)')
    
    conn.commit()
    conn.close()
    print("✅ Database indexes created")


def query_timer(func):
    """Decorator to measure query execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time()
        result = func(*args, **kwargs)
        elapsed = time() - start
        if elapsed > 1.0:  # Log slow queries
            print(f"⚠️ Slow query: {func.__name__} took {elapsed:.2f}s")
        return result
    return wrapper


@st.cache_data(ttl=3600)
def cached_query(query, params=None):
    """Execute cached database query"""
    conn = sqlite3.connect('farmermarket.db')
    cursor = conn.cursor()
    
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    
    results = cursor.fetchall()
    conn.close()
    return results


@st.cache_data(ttl=3600, show_spinner=False)
def get_districts_cached():
    """Get cached list of districts"""
    query = "SELECT DISTINCT district FROM farmers WHERE district IS NOT NULL"
    return [row[0] for row in cached_query(query)]


@st.cache_data(ttl=1800, show_spinner=False)
def get_tool_categories_cached():
    """Get cached tool categories"""
    query = "SELECT DISTINCT category FROM tool_listings WHERE category IS NOT NULL"
    return [row[0] for row in cached_query(query)]


@st.cache_data(ttl=1800, show_spinner=False)
def get_crop_categories_cached():
    """Get cached crop categories"""
    query = "SELECT DISTINCT category FROM crop_listings WHERE category IS NOT NULL"
    return [row[0] for row in cached_query(query)]


def optimize_query(query):
    """Optimize SQL query by adding LIMIT and using indexes"""
    query_lower = query.lower()
    
    # Add LIMIT if not present
    if 'limit' not in query_lower and 'select' in query_lower:
        query += ' LIMIT 1000'
    
    return query


class LazyLoader:
    """Lazy loading for large datasets"""
    
    def __init__(self, query, page_size=50):
        self.query = query
        self.page_size = page_size
        self.current_page = 0
        self._cache = {}
    
    def get_page(self, page_num):
        """Get specific page of results"""
        if page_num in self._cache:
            return self._cache[page_num]
        
        offset = page_num * self.page_size
        query = f"{self.query} LIMIT {self.page_size} OFFSET {offset}"
        
        results = cached_query(query)
        self._cache[page_num] = results
        return results
    
    def next_page(self):
        """Get next page"""
        self.current_page += 1
        return self.get_page(self.current_page)
    
    def prev_page(self):
        """Get previous page"""
        if self.current_page > 0:
            self.current_page -= 1
        return self.get_page(self.current_page)


def compress_image_data(image_bytes, max_size_kb=500):
    """Compress image data for faster loading"""
    try:
        from PIL import Image
        import io
        
        # Open image
        img = Image.open(io.BytesIO(image_bytes))
        
        # Resize if too large
        max_dimension = 1024
        if max(img.size) > max_dimension:
            ratio = max_dimension / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # Compress
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=85, optimize=True)
        compressed = output.getvalue()
        
        # Check size
        if len(compressed) / 1024 > max_size_kb:
            # Try lower quality
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=60, optimize=True)
            compressed = output.getvalue()
        
        return compressed
    except Exception as e:
        print(f"Image compression failed: {e}")
        return image_bytes


def enable_connection_pooling():
    """Enable SQLite connection pooling for better performance"""
    import sqlite3
    
    # Set pragmas for better performance
    conn = sqlite3.connect('farmermarket.db')
    cursor = conn.cursor()
    
    # Performance pragmas
    cursor.execute('PRAGMA journal_mode=WAL')  # Write-Ahead Logging
    cursor.execute('PRAGMA synchronous=NORMAL')  # Faster writes
    cursor.execute('PRAGMA cache_size=10000')  # Larger cache
    cursor.execute('PRAGMA temp_store=MEMORY')  # Use memory for temp
    
    conn.commit()
    conn.close()
    print("✅ Database performance optimized")


def batch_insert(table, columns, data_list):
    """Optimized batch insert operation"""
    if not data_list:
        return
    
    conn = sqlite3.connect('farmermarket.db')
    cursor = conn.cursor()
    
    placeholders = ','.join(['?' for _ in columns])
    query = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
    
    cursor.executemany(query, data_list)
    conn.commit()
    conn.close()


def analyze_database():
    """Analyze database and optimize"""
    conn = sqlite3.connect('farmermarket.db')
    cursor = conn.cursor()
    
    # Analyze tables for query optimizer
    cursor.execute('ANALYZE')
    
    # Vacuum to reclaim space
    cursor.execute('VACUUM')
    
    conn.commit()
    conn.close()
    print("✅ Database analyzed and optimized")


def init_performance_optimizations():
    """Initialize all performance optimizations"""
    try:
        create_database_indexes()
        enable_connection_pooling()
        print("✅ Performance optimizations initialized")
    except Exception as e:
        print(f"⚠️ Performance optimization warning: {e}")
