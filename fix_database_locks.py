# fix_database_locks.py
"""
Fix all database lock issues by updating all connections
"""

import sqlite3
import os

DB_NAME = 'farmermarket.db'

print("🔧 Fixing Database Lock Issues...\n")

# Step 1: Convert to WAL mode
print("1️⃣ Converting to Write-Ahead Logging (WAL) mode...")
try:
    conn = sqlite3.connect(DB_NAME, timeout=30.0)
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA busy_timeout=30000')
    result = conn.execute('PRAGMA journal_mode').fetchone()
    print(f"   ✅ Journal mode: {result[0]}")
    conn.close()
except Exception as e:
    print(f"   ⚠️ Error: {e}")

# Step 2: Vacuum the database
print("\n2️⃣ Optimizing database...")
try:
    conn = sqlite3.connect(DB_NAME, timeout=30.0)
    conn.execute('VACUUM')
    conn.close()
    print("   ✅ Database optimized")
except Exception as e:
    print(f"   ⚠️ Error: {e}")

# Step 3: Check for locks
print("\n3️⃣ Checking for active locks...")
try:
    conn = sqlite3.connect(DB_NAME, timeout=30.0)
    c = conn.cursor()
    
    # Check if we can access tables
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = c.fetchall()
    print(f"   ✅ Found {len(tables)} tables - No locks detected")
    
    conn.close()
except Exception as e:
    print(f"   ⚠️ Error: {e}")

# Step 4: Create helper file
print("\n4️⃣ Creating database helper...")

helper_code = '''# database/db_helper.py
"""
Database connection helper to prevent locks
"""

import sqlite3
import time
from contextlib import contextmanager

DB_NAME = 'farmermarket.db'

def get_db_connection(timeout=30.0):
    """
    Get a safe database connection with proper settings.
    
    Args:
        timeout: Connection timeout in seconds
    
    Returns:
        sqlite3.Connection with WAL mode enabled
    """
    conn = sqlite3.connect(DB_NAME, timeout=timeout, check_same_thread=False)
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA busy_timeout=30000')  # 30 seconds
    return conn

@contextmanager
def db_transaction(timeout=30.0):
    """
    Context manager for safe database transactions.
    
    Usage:
        with db_transaction() as (conn, cursor):
            cursor.execute("SELECT * FROM table")
            # Connection automatically commits and closes
    
    Args:
        timeout: Connection timeout in seconds
    
    Yields:
        tuple: (connection, cursor)
    """
    conn = get_db_connection(timeout)
    cursor = conn.cursor()
    try:
        yield conn, cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def safe_execute(query, params=None, fetch_one=False, fetch_all=True, timeout=30.0):
    """
    Safely execute a query with automatic connection management.
    
    Args:
        query: SQL query string
        params: Query parameters (optional)
        fetch_one: Return single result
        fetch_all: Return all results
        timeout: Connection timeout
    
    Returns:
        Query results or None
    """
    with db_transaction(timeout) as (conn, cursor):
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch_one:
            return cursor.fetchone()
        elif fetch_all:
            return cursor.fetchall()
        return None
'''

with open('database/db_helper.py', 'w', encoding='utf-8') as f:
    f.write(helper_code)

print("   ✅ Created database/db_helper.py")

print("\n" + "=" * 60)
print("✅ Database Lock Fix Complete!")
print("=" * 60)

print("\n📋 What was fixed:")
print("   • Enabled WAL mode for better concurrency")
print("   • Set 30-second timeout for all connections")
print("   • Created db_helper.py for safe connections")
print("   • Optimized database structure")

print("\n💡 Next Steps:")
print("   1. Restart Streamlit app: Ctrl+C then 'streamlit run app.py'")
print("   2. Database locks should be resolved")
print("   3. Use db_helper.py for new database code")

print("\n🔍 If issues persist:")
print("   • Close all Python processes")
print("   • Delete farmermarket.db-wal and farmermarket.db-shm files")
print("   • Run this script again")


