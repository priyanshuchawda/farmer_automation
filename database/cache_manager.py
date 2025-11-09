# database/cache_manager.py
"""
Smart Caching System for Price Predictions, Weather, and Market Data
Reduces API calls by caching data for 24 hours per user/location
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

DB_NAME = 'farmermarket.db'

class CacheManager:
    """Manages caching of weather, market prices, and predictions."""
    
    def __init__(self):
        """Initialize cache tables."""
        self._init_cache_tables()
    
    def _init_cache_tables(self):
        """Create cache tables if they don't exist."""
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # Weather Cache Table
        c.execute("""CREATE TABLE IF NOT EXISTS weather_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT NOT NULL,
            weather_data TEXT NOT NULL,
            cached_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            UNIQUE(location)
        )""")
        
        # Market Price Cache Table
        c.execute("""CREATE TABLE IF NOT EXISTS market_price_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crop_name TEXT NOT NULL,
            location TEXT NOT NULL,
            price_data TEXT NOT NULL,
            cached_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            UNIQUE(crop_name, location)
        )""")
        
        # Price Prediction Cache Table
        c.execute("""CREATE TABLE IF NOT EXISTS prediction_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crop_name TEXT NOT NULL,
            location TEXT NOT NULL,
            reference_price REAL NOT NULL,
            prediction_data TEXT NOT NULL,
            cached_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            UNIQUE(crop_name, location, reference_price)
        )""")
        
        # Cache Statistics Table (for monitoring)
        c.execute("""CREATE TABLE IF NOT EXISTS cache_statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cache_type TEXT NOT NULL,
            hits INTEGER DEFAULT 0,
            misses INTEGER DEFAULT 0,
            last_updated TEXT NOT NULL
        )""")
        
        conn.commit()
        conn.close()
    
    def _is_expired(self, expires_at_str: str) -> bool:
        """Check if cache entry has expired."""
        try:
            expires_at = datetime.fromisoformat(expires_at_str)
            return datetime.now() >= expires_at
        except:
            return True
    
    def _update_statistics(self, cache_type: str, is_hit: bool):
        """Update cache hit/miss statistics."""
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # Check if stats exist
        c.execute("SELECT id, hits, misses FROM cache_statistics WHERE cache_type = ?", (cache_type,))
        result = c.fetchone()
        
        if result:
            stat_id, hits, misses = result
            if is_hit:
                c.execute("UPDATE cache_statistics SET hits = ?, last_updated = ? WHERE id = ?",
                         (hits + 1, datetime.now().isoformat(), stat_id))
            else:
                c.execute("UPDATE cache_statistics SET misses = ?, last_updated = ? WHERE id = ?",
                         (misses + 1, datetime.now().isoformat(), stat_id))
        else:
            # Create new stats entry
            hits = 1 if is_hit else 0
            misses = 0 if is_hit else 1
            c.execute("INSERT INTO cache_statistics (cache_type, hits, misses, last_updated) VALUES (?, ?, ?, ?)",
                     (cache_type, hits, misses, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    # ========================================
    # WEATHER CACHE
    # ========================================
    
    def get_weather_cache(self, location: str) -> Optional[Dict[str, Any]]:
        """
        Get cached weather data for a location.
        
        Args:
            location: Location string
        
        Returns:
            Cached weather data or None if expired/not found
        """
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute("SELECT * FROM weather_cache WHERE LOWER(location) = LOWER(?)", (location,))
        result = c.fetchone()
        conn.close()
        
        if result:
            if not self._is_expired(result['expires_at']):
                self._update_statistics('weather', True)
                return json.loads(result['weather_data'])
            else:
                # Expired, delete it
                self.clear_weather_cache(location)
        
        self._update_statistics('weather', False)
        return None
    
    def set_weather_cache(self, location: str, weather_data: Dict[str, Any], hours: int = 24):
        """
        Cache weather data for a location.
        
        Args:
            location: Location string
            weather_data: Weather data dictionary
            hours: Cache validity in hours (default: 24)
        """
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        cached_at = datetime.now()
        expires_at = cached_at + timedelta(hours=hours)
        
        c.execute("""
            INSERT OR REPLACE INTO weather_cache 
            (location, weather_data, cached_at, expires_at)
            VALUES (?, ?, ?, ?)
        """, (location, json.dumps(weather_data), cached_at.isoformat(), expires_at.isoformat()))
        
        conn.commit()
        conn.close()
    
    def clear_weather_cache(self, location: str = None):
        """Clear weather cache for specific location or all."""
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        if location:
            c.execute("DELETE FROM weather_cache WHERE LOWER(location) = LOWER(?)", (location,))
        else:
            c.execute("DELETE FROM weather_cache")
        
        conn.commit()
        conn.close()
    
    # ========================================
    # MARKET PRICE CACHE
    # ========================================
    
    def get_market_price_cache(self, crop_name: str, location: str) -> Optional[Dict[str, Any]]:
        """
        Get cached market price data.
        
        Args:
            crop_name: Name of crop
            location: Location string
        
        Returns:
            Cached price data or None if expired/not found
        """
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute("""
            SELECT * FROM market_price_cache 
            WHERE LOWER(crop_name) = LOWER(?) AND LOWER(location) = LOWER(?)
        """, (crop_name, location))
        result = c.fetchone()
        conn.close()
        
        if result:
            if not self._is_expired(result['expires_at']):
                self._update_statistics('market_price', True)
                return json.loads(result['price_data'])
            else:
                self.clear_market_price_cache(crop_name, location)
        
        self._update_statistics('market_price', False)
        return None
    
    def set_market_price_cache(self, crop_name: str, location: str, 
                               price_data: Dict[str, Any], hours: int = 24):
        """
        Cache market price data.
        
        Args:
            crop_name: Name of crop
            location: Location string
            price_data: Market data dictionary
            hours: Cache validity in hours (default: 24)
        """
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        cached_at = datetime.now()
        expires_at = cached_at + timedelta(hours=hours)
        
        c.execute("""
            INSERT OR REPLACE INTO market_price_cache 
            (crop_name, location, price_data, cached_at, expires_at)
            VALUES (?, ?, ?, ?, ?)
        """, (crop_name, location, json.dumps(price_data), 
              cached_at.isoformat(), expires_at.isoformat()))
        
        conn.commit()
        conn.close()
    
    def clear_market_price_cache(self, crop_name: str = None, location: str = None):
        """Clear market price cache."""
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        if crop_name and location:
            c.execute("""
                DELETE FROM market_price_cache 
                WHERE LOWER(crop_name) = LOWER(?) AND LOWER(location) = LOWER(?)
            """, (crop_name, location))
        elif crop_name:
            c.execute("DELETE FROM market_price_cache WHERE LOWER(crop_name) = LOWER(?)", (crop_name,))
        elif location:
            c.execute("DELETE FROM market_price_cache WHERE LOWER(location) = LOWER(?)", (location,))
        else:
            c.execute("DELETE FROM market_price_cache")
        
        conn.commit()
        conn.close()
    
    # ========================================
    # PREDICTION CACHE
    # ========================================
    
    def get_prediction_cache(self, crop_name: str, location: str, 
                            reference_price: float, tolerance: float = 100.0) -> Optional[Dict[str, Any]]:
        """
        Get cached prediction data.
        
        Args:
            crop_name: Name of crop
            location: Location string
            reference_price: Reference price
            tolerance: Price tolerance for cache match (default: 100 rupees)
        
        Returns:
            Cached prediction or None if expired/not found
        """
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        # Find predictions within price tolerance
        c.execute("""
            SELECT * FROM prediction_cache 
            WHERE LOWER(crop_name) = LOWER(?) 
            AND LOWER(location) = LOWER(?)
            AND ABS(reference_price - ?) <= ?
            ORDER BY cached_at DESC
            LIMIT 1
        """, (crop_name, location, reference_price, tolerance))
        result = c.fetchone()
        conn.close()
        
        if result:
            if not self._is_expired(result['expires_at']):
                self._update_statistics('prediction', True)
                return json.loads(result['prediction_data'])
            else:
                self.clear_prediction_cache(crop_name, location)
        
        self._update_statistics('prediction', False)
        return None
    
    def set_prediction_cache(self, crop_name: str, location: str, reference_price: float,
                           prediction_data: Dict[str, Any], hours: int = 24):
        """
        Cache prediction data.
        
        Args:
            crop_name: Name of crop
            location: Location string
            reference_price: Reference price used
            prediction_data: Prediction dictionary
            hours: Cache validity in hours (default: 24)
        """
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        cached_at = datetime.now()
        expires_at = cached_at + timedelta(hours=hours)
        
        c.execute("""
            INSERT OR REPLACE INTO prediction_cache 
            (crop_name, location, reference_price, prediction_data, cached_at, expires_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (crop_name, location, reference_price, json.dumps(prediction_data), 
              cached_at.isoformat(), expires_at.isoformat()))
        
        conn.commit()
        conn.close()
    
    def clear_prediction_cache(self, crop_name: str = None, location: str = None):
        """Clear prediction cache."""
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        if crop_name and location:
            c.execute("""
                DELETE FROM prediction_cache 
                WHERE LOWER(crop_name) = LOWER(?) AND LOWER(location) = LOWER(?)
            """, (crop_name, location))
        elif crop_name:
            c.execute("DELETE FROM prediction_cache WHERE LOWER(crop_name) = LOWER(?)", (crop_name,))
        elif location:
            c.execute("DELETE FROM prediction_cache WHERE LOWER(location) = LOWER(?)", (location,))
        else:
            c.execute("DELETE FROM prediction_cache")
        
        conn.commit()
        conn.close()
    
    # ========================================
    # CACHE MANAGEMENT
    # ========================================
    
    def get_cache_statistics(self) -> Dict[str, Dict[str, int]]:
        """Get cache hit/miss statistics."""
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute("SELECT * FROM cache_statistics")
        results = c.fetchall()
        conn.close()
        
        stats = {}
        for row in results:
            total = row['hits'] + row['misses']
            hit_rate = (row['hits'] / total * 100) if total > 0 else 0
            
            stats[row['cache_type']] = {
                'hits': row['hits'],
                'misses': row['misses'],
                'total_requests': total,
                'hit_rate': round(hit_rate, 2),
                'last_updated': row['last_updated']
            }
        
        return stats
    
    def clear_expired_cache(self):
        """Clear all expired cache entries."""
        now = datetime.now().isoformat()
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        c.execute("DELETE FROM weather_cache WHERE expires_at < ?", (now,))
        weather_deleted = c.rowcount
        
        c.execute("DELETE FROM market_price_cache WHERE expires_at < ?", (now,))
        price_deleted = c.rowcount
        
        c.execute("DELETE FROM prediction_cache WHERE expires_at < ?", (now,))
        prediction_deleted = c.rowcount
        
        conn.commit()
        conn.close()
        
        return {
            'weather_deleted': weather_deleted,
            'market_price_deleted': price_deleted,
            'prediction_deleted': prediction_deleted,
            'total_deleted': weather_deleted + price_deleted + prediction_deleted
        }
    
    def clear_all_cache(self):
        """Clear all cache data."""
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        c.execute("DELETE FROM weather_cache")
        c.execute("DELETE FROM market_price_cache")
        c.execute("DELETE FROM prediction_cache")
        c.execute("DELETE FROM cache_statistics")
        
        conn.commit()
        conn.close()
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get overall cache information."""
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM weather_cache")
        weather_count = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM market_price_cache")
        price_count = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM prediction_cache")
        prediction_count = c.fetchone()[0]
        
        conn.close()
        
        return {
            'weather_cached': weather_count,
            'market_prices_cached': price_count,
            'predictions_cached': prediction_count,
            'total_cached': weather_count + price_count + prediction_count,
            'statistics': self.get_cache_statistics()
        }


