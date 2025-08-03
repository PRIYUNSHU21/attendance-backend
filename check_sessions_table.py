#!/usr/bin/env python3
"""
Check the actual structure of attendance_sessions table
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from config.db import db
from app import create_app
import sqlite3

def main():
    app = create_app()
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Get table info
        connection = db.engine.raw_connection()
        cursor = connection.cursor()
        
        print("=== attendance_sessions table structure ===")
        cursor.execute("PRAGMA table_info(attendance_sessions)")
        columns = cursor.fetchall()
        
        for col in columns:
            print(f"Column: {col[1]}, Type: {col[2]}, NotNull: {col[3]}, Default: {col[4]}")
        
        print("\n=== Checking for location columns specifically ===")
        location_cols = ['latitude', 'longitude', 'radius']
        for col_name in location_cols:
            cursor.execute("PRAGMA table_info(attendance_sessions)")
            columns = cursor.fetchall()
            found = any(col[1] == col_name for col in columns)
            print(f"{col_name}: {'✅ EXISTS' if found else '❌ MISSING'}")
        
        connection.close()

if __name__ == "__main__":
    main()
