"""
Offline Manager - Handles offline data storage and sync for rural connectivity
"""
import streamlit as st
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import pickle


class OfflineManager:
    """Manages offline data caching and synchronization"""
    
    def __init__(self, db_path="farmermarket.db"):
        self.db_path = db_path
        self.init_offline_cache()
    
    def init_offline_cache(self):
        """Initialize offline cache tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Cache for weather data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_cache (
                location TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL
            )
        ''')
        
        # Cache for market prices
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_cache (
                commodity TEXT,
                market TEXT,
                state TEXT,
                data TEXT NOT NULL,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                PRIMARY KEY (commodity, market, state)
            )
        ''')
        
        # Cache for calendar events
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calendar_cache (
                user_id INTEGER,
                date TEXT,
                events TEXT NOT NULL,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, date)
            )
        ''')
        
        # Offline sync queue
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_type TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                synced INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def cache_weather(self, location, data, hours=6):
        """Cache weather data for offline access"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        expires_at = datetime.now() + timedelta(hours=hours)
        
        cursor.execute('''
            INSERT OR REPLACE INTO weather_cache (location, data, expires_at)
            VALUES (?, ?, ?)
        ''', (location, json.dumps(data), expires_at))
        
        conn.commit()
        conn.close()
    
    def get_cached_weather(self, location):
        """Get cached weather data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT data, cached_at FROM weather_cache
            WHERE location = ? AND expires_at > CURRENT_TIMESTAMP
        ''', (location,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            data = json.loads(result[0])
            data['_cached'] = True
            data['_cached_at'] = result[1]
            return data
        return None
    
    def cache_market_price(self, commodity, market, state, data, hours=24):
        """Cache market price data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        expires_at = datetime.now() + timedelta(hours=hours)
        
        cursor.execute('''
            INSERT OR REPLACE INTO price_cache 
            (commodity, market, state, data, expires_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (commodity, market, state, json.dumps(data), expires_at))
        
        conn.commit()
        conn.close()
    
    def get_cached_price(self, commodity, market, state):
        """Get cached market price"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT data, cached_at FROM price_cache
            WHERE commodity = ? AND market = ? AND state = ?
            AND expires_at > CURRENT_TIMESTAMP
        ''', (commodity, market, state))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            data = json.loads(result[0])
            data['_cached'] = True
            data['_cached_at'] = result[1]
            return data
        return None
    
    def cache_calendar_events(self, user_id, date, events):
        """Cache calendar events for offline access"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO calendar_cache (user_id, date, events)
            VALUES (?, ?, ?)
        ''', (user_id, date, json.dumps(events)))
        
        conn.commit()
        conn.close()
    
    def get_cached_calendar(self, user_id, date):
        """Get cached calendar events"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT events, cached_at FROM calendar_cache
            WHERE user_id = ? AND date = ?
        ''', (user_id, date))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'events': json.loads(result[0]),
                '_cached': True,
                '_cached_at': result[1]
            }
        return None
    
    def add_to_sync_queue(self, action_type, data):
        """Add action to sync queue for later processing"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sync_queue (action_type, data)
            VALUES (?, ?)
        ''', (action_type, json.dumps(data)))
        
        conn.commit()
        conn.close()
    
    def get_pending_syncs(self):
        """Get all pending sync actions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, action_type, data FROM sync_queue
            WHERE synced = 0
            ORDER BY created_at ASC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {'id': r[0], 'action_type': r[1], 'data': json.loads(r[2])}
            for r in results
        ]
    
    def mark_synced(self, sync_id):
        """Mark a sync action as completed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE sync_queue SET synced = 1
            WHERE id = ?
        ''', (sync_id,))
        
        conn.commit()
        conn.close()
    
    def clean_expired_cache(self):
        """Remove expired cache entries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM weather_cache WHERE expires_at < CURRENT_TIMESTAMP')
        cursor.execute('DELETE FROM price_cache WHERE expires_at < CURRENT_TIMESTAMP')
        cursor.execute('DELETE FROM sync_queue WHERE synced = 1 AND created_at < datetime("now", "-7 days")')
        
        conn.commit()
        conn.close()
    
    def get_cache_stats(self):
        """Get cache statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        cursor.execute('SELECT COUNT(*) FROM weather_cache WHERE expires_at > CURRENT_TIMESTAMP')
        stats['weather_cached'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM price_cache WHERE expires_at > CURRENT_TIMESTAMP')
        stats['prices_cached'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM calendar_cache')
        stats['calendar_cached'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM sync_queue WHERE synced = 0')
        stats['pending_syncs'] = cursor.fetchone()[0]
        
        conn.close()
        return stats


def render_offline_status():
    """Display offline status and cache information"""
    offline_mgr = OfflineManager()
    stats = offline_mgr.get_cache_stats()
    
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📡 Offline Status")
        
        # Check if online (simplified check)
        is_online = st.session_state.get('is_online', True)
        
        if is_online:
            st.success("🟢 Online")
        else:
            st.warning("🔴 Offline Mode")
            st.info("Using cached data")
        
        # Cache stats
        with st.expander("📊 Cache Info"):
            st.metric("Weather Cached", stats['weather_cached'])
            st.metric("Prices Cached", stats['prices_cached'])
            st.metric("Calendar Cached", stats['calendar_cached'])
            
            if stats['pending_syncs'] > 0:
                st.warning(f"⏳ {stats['pending_syncs']} pending syncs")
            
            if st.button("🗑️ Clear Cache"):
                offline_mgr.clean_expired_cache()
                st.success("Cache cleaned!")
                st.rerun()


def show_offline_banner(message="Using cached data"):
    """Show banner when using offline/cached data"""
    st.warning(f"📴 Offline Mode: {message}")
