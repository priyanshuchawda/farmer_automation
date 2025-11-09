# database/db_helper.py
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


