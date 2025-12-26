"""
Database Migration Script: Add password column to farmers table
This script adds the password column to existing farmers table if it doesn't exist
"""

import sqlite3
import os

import os; DB_NAME = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'farmermarket.db')

def migrate_database():
    """Add password column to farmers table if it doesn't exist"""
    
    if not os.path.exists(DB_NAME):
        print(f"❌ Database file '{DB_NAME}' not found!")
        print("The database will be created when you run the app.")
        return
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    try:
        # Check if password column exists
        c.execute("PRAGMA table_info(farmers)")
        columns = [column[1] for column in c.fetchall()]
        
        if 'password' in columns:
            print("✅ Password column already exists!")
        else:
            print("📝 Adding password column to farmers table...")
            # Add password column with default value
            c.execute("ALTER TABLE farmers ADD COLUMN password TEXT DEFAULT 'farmer123'")
            conn.commit()
            print("✅ Password column added successfully!")
            
            # Update existing records to have default password
            c.execute("UPDATE farmers SET password = 'farmer123' WHERE password IS NULL")
            conn.commit()
            
            # Count updated records
            c.execute("SELECT COUNT(*) FROM farmers")
            count = c.fetchone()[0]
            print(f"✅ Updated {count} existing farmer records with default password 'farmer123'")
            
        # Display table structure
        print("\n📋 Current farmers table structure:")
        c.execute("PRAGMA table_info(farmers)")
        for col in c.fetchall():
            print(f"   - {col[1]} ({col[2]})")
        
        # Display existing farmers
        c.execute("SELECT name, location FROM farmers")
        farmers = c.fetchall()
        if farmers:
            print(f"\n👥 Existing farmers ({len(farmers)}):")
            for farmer in farmers:
                print(f"   - {farmer[0]} ({farmer[1]})")
            print("\n💡 All existing farmers can now login with password: 'farmer123'")
            print("   They can change their password after logging in (future feature)")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 DATABASE MIGRATION: Adding Password Column")
    print("=" * 60)
    migrate_database()
    print("\n" + "=" * 60)
    print("✅ Migration Complete!")
    print("=" * 60)
    print("\n🚀 You can now run the app: streamlit run app.py")


