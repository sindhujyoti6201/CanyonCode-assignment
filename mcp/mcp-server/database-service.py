#!/usr/bin/env python3
"""
Database utilities - Connection management and data loading
"""

# Standard library imports
import os
from typing import Optional

# Third-party imports
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor

# Local imports
from constants import (
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, 
    POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_URLS,
    DB_CONNECTION_ERROR
)

# =============================================================================
# DATABASE CONNECTION (SINGLETON)
# =============================================================================

class DatabaseConnection:
    """Singleton database connection manager"""
    _instance = None
    _connection = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def get_connection(self):
        """Get or create database connection"""
        if self._connection is None or self._connection.closed:
            self._connection = self._create_connection()
        return self._connection
    
    def _create_connection(self):
        """Create new database connection"""
        try:
            # Try Docker service name first, then localhost
            for host in POSTGRES_URLS:
                try:
                    conn = psycopg2.connect(
                        host=host,
                        port=POSTGRES_PORT,
                        database=POSTGRES_DB,
                        user=POSTGRES_USER,
                        password=POSTGRES_PASSWORD
                    )
                    print(f"Connected to PostgreSQL at {host}:{POSTGRES_PORT}")
                    return conn
                except:
                    continue
            
            print(DB_CONNECTION_ERROR)
            return None
        except Exception as e:
            print(f"Database connection error: {e}")
            return None
    
    def close_connection(self):
        """Close database connection"""
        if self._connection and not self._connection.closed:
            self._connection.close()
            self._connection = None

# Global database connection instance
db_connection = DatabaseConnection()

def get_db_connection():
    """Get database connection (singleton)"""
    return db_connection.get_connection()

# =============================================================================
# DATABASE INITIALIZATION
# =============================================================================

def create_tables():
    """Create database tables if they don't exist"""
    try:
        conn = get_db_connection()
        if conn is None:
            return False
        
        cursor = conn.cursor()
        
        # Create table if not exists
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS camera_feeds (
            feed_id VARCHAR(50) PRIMARY KEY,
            theater VARCHAR(20),
            frrate DECIMAL(10,3),
            res_w INTEGER,
            res_h INTEGER,
            codec VARCHAR(20),
            encr BOOLEAN,
            lat_ms INTEGER,
            modl_tag VARCHAR(50),
            civ_ok BOOLEAN
        );
        """
        cursor.execute(create_table_sql)
        conn.commit()
        cursor.close()
        
        print("Database tables created successfully")
        return True
        
    except Exception as e:
        print(f"Error creating tables: {e}")
        return False

def load_csv_to_database(csv_file_path: str = "../../db-data/Table_feeds_v2.csv"):
    """Load CSV data into PostgreSQL database (preload function)"""
    try:
        # Read CSV file
        df = pd.read_csv(csv_file_path)
        print(f"Loaded CSV with {len(df)} rows and {len(df.columns)} columns")
        
        # Get database connection
        conn = get_db_connection()
        if conn is None:
            return False
        
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute("DELETE FROM camera_feeds;")
        
        # Insert data
        for _, row in df.iterrows():
            insert_sql = """
            INSERT INTO camera_feeds 
            (feed_id, theater, frrate, res_w, res_h, codec, encr, lat_ms, modl_tag, civ_ok)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (feed_id) DO UPDATE SET
                theater = EXCLUDED.theater,
                frrate = EXCLUDED.frrate,
                res_w = EXCLUDED.res_w,
                res_h = EXCLUDED.res_h,
                codec = EXCLUDED.codec,
                encr = EXCLUDED.encr,
                lat_ms = EXCLUDED.lat_ms,
                modl_tag = EXCLUDED.modl_tag,
                civ_ok = EXCLUDED.civ_ok;
            """
            cursor.execute(insert_sql, tuple(row))
        
        conn.commit()
        cursor.close()
        
        print(f"Successfully loaded {len(df)} records into camera_feeds table")
        return True
        
    except Exception as e:
        print(f"Error loading CSV to database: {e}")
        return False

def initialize_database():
    """Initialize database (create tables and load data)"""
    print("Initializing database...")
    
    # Create tables
    if not create_tables():
        return False
    
    # Load CSV data
    if not load_csv_to_database():
        return False
    
    print("Database initialization completed successfully!")
    return True
