#!/usr/bin/env python3
"""Check current database schema"""

import sqlite3
import os

def check_database():
    db_path = 'instance/attendance.db'
    
    if not os.path.exists(db_path):
        print("❌ Database file does not exist")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"📋 Tables found: {[t[0] for t in tables]}")
        
        # Check each table for record counts
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   - {table_name}: {count} records")
            
        # Check if organizations table exists specifically
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='organizations'")
        org_exists = cursor.fetchone()[0]
        print(f"🏢 Organizations table exists: {org_exists > 0}")
        
        if org_exists == 0:
            print("⚠️ Organizations table is missing - this explains the foreign key issues")
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_database()
