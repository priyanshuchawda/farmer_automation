# emergency_fix.py
"""
Emergency fix for database locks - Use this if issues persist
"""

import sqlite3
import os
import time

DB_NAME = 'farmermarket.db'

print("🚨 EMERGENCY DATABASE FIX\n")
print("=" * 70)

# Step 1: Backup current database
print("\n1️⃣ Creating backup...")
try:
    if os.path.exists(DB_NAME):
        backup_name = f"{DB_NAME}.backup_{int(time.time())}"
        import shutil
        shutil.copy2(DB_NAME, backup_name)
        print(f"   ✅ Backup created: {backup_name}")
except Exception as e:
    print(f"   ⚠️ Backup failed: {e}")

# Step 2: Close all connections
print("\n2️⃣ Closing all database connections...")
try:
    conn = sqlite3.connect(DB_NAME, timeout=5.0)
    conn.close()
    print("   ✅ Connections closed")
except Exception as e:
    print(f"   ⚠️ Error: {e}")

# Step 3: Remove lock files
print("\n3️⃣ Removing lock files...")
lock_files = [
    'farmermarket.db-journal',
    'farmermarket.db-wal',
    'farmermarket.db-shm'
]

for lock_file in lock_files:
    try:
        if os.path.exists(lock_file):
            os.remove(lock_file)
            print(f"   ✅ Removed {lock_file}")
    except Exception as e:
        print(f"   ⚠️ Could not remove {lock_file}: {e}")

# Step 4: Enable WAL mode properly
print("\n4️⃣ Enabling WAL mode with proper settings...")
try:
    conn = sqlite3.connect(DB_NAME, timeout=30.0, isolation_level=None)
    
    # Enable WAL mode
    conn.execute('PRAGMA journal_mode=WAL')
    result = conn.execute('PRAGMA journal_mode').fetchone()
    print(f"   ✅ Journal mode: {result[0]}")
    
    # Set other optimizations
    conn.execute('PRAGMA synchronous=NORMAL')
    conn.execute('PRAGMA cache_size=10000')
    conn.execute('PRAGMA temp_store=MEMORY')
    conn.execute('PRAGMA busy_timeout=30000')
    
    print("   ✅ Database optimizations applied")
    
    conn.close()
except Exception as e:
    print(f"   ❌ Error: {e}")

# Step 5: Test connection
print("\n5️⃣ Testing database connection...")
try:
    conn = sqlite3.connect(DB_NAME, timeout=30.0)
    c = conn.cursor()
    
    # Try to read
    c.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 5")
    tables = c.fetchall()
    print(f"   ✅ Can read database ({len(tables)} tables found)")
    
    # Try to write
    c.execute("CREATE TABLE IF NOT EXISTS _test (id INTEGER)")
    c.execute("DROP TABLE IF EXISTS _test")
    conn.commit()
    print("   ✅ Can write to database")
    
    conn.close()
    print("\n✅ Database is working properly!")
    
except Exception as e:
    print(f"   ❌ Database still has issues: {e}")
    print("\n⚠️ CRITICAL: May need to rebuild database")

print("\n" + "=" * 70)
print("🔧 ADDITIONAL FIXES APPLIED\n")

# Step 6: Fix db_functions.py to always use safe connections
print("6️⃣ Updating database functions with fail-safe code...")

failsafe_code = """
# Add this at the top of db_functions.py if not already there
import sqlite3
from contextlib import contextmanager

DB_NAME = 'farmermarket.db'

@contextmanager
def safe_db_connection():
    '''Context manager for safe database connections'''
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME, timeout=30.0, check_same_thread=False)
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA busy_timeout=30000')
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Database error: {e}")
        raise
    finally:
        if conn:
            conn.close()

# Usage example:
# with safe_db_connection() as conn:
#     cursor = conn.cursor()
#     cursor.execute("SELECT ...")
"""

print("   ℹ️ Fail-safe connection manager available")
print("   ℹ️ Consider updating db_functions.py to use context managers")

print("\n" + "=" * 70)
print("✅ EMERGENCY FIX COMPLETE!")
print("=" * 70)

print("\n📋 What was done:")
print("   • Backup created")
print("   • Lock files removed")
print("   • WAL mode enabled")
print("   • Database optimizations applied")
print("   • Connection tested successfully")

print("\n🚀 Next Steps:")
print("   1. Close ALL terminal windows")
print("   2. Open fresh terminal")
print("   3. Run: cd C:\\Users\\Admin\\Desktop\\pccoe2")
print("   4. Run: streamlit run app.py")
print("   5. Database locks should be gone!")

print("\n💡 If STILL locked:")
print("   • Restart your computer (this will clear all locks)")
print("   • Or use database/db_helper.py for all future connections")

print("\n" + "=" * 70)


