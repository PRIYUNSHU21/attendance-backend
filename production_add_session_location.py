#!/usr/bin/env python3
"""
Production migration to add location columns to attendance_sessions table
This script should be run on the production server to add missing location columns
"""

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def run_production_migration():
    """Add location columns to attendance_sessions table in production."""
    try:
        # Get the DATABASE_URL from environment (Render sets this automatically)
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL environment variable not found")
            return False
        
        print("🔗 Connecting to production database...")
        
        # Connect to the database
        conn = psycopg2.connect(database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("📊 Checking current table structure...")
        
        # Check if columns already exist
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'attendance_sessions' 
            AND column_name IN ('latitude', 'longitude', 'radius')
        """)
        existing_columns = [row[0] for row in cursor.fetchall()]
        print(f"Existing location columns: {existing_columns}")
        
        columns_to_add = []
        if 'latitude' not in existing_columns:
            columns_to_add.append("latitude FLOAT")
        if 'longitude' not in existing_columns:
            columns_to_add.append("longitude FLOAT")
        if 'radius' not in existing_columns:
            columns_to_add.append("radius INTEGER DEFAULT 100")
        
        if not columns_to_add:
            print("✅ All location columns already exist")
            return True
        
        print(f"➕ Adding columns: {columns_to_add}")
        
        # Add missing columns
        for column_def in columns_to_add:
            alter_query = f"ALTER TABLE attendance_sessions ADD COLUMN {column_def}"
            print(f"Executing: {alter_query}")
            cursor.execute(alter_query)
            print(f"✅ Added column: {column_def}")
        
        # Verify the changes
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'attendance_sessions' 
            AND column_name IN ('latitude', 'longitude', 'radius')
            ORDER BY column_name
        """)
        
        print("\n📋 Final table structure for location columns:")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} (nullable: {row[2]}, default: {row[3]})")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = run_production_migration()
    exit(0 if success else 1)
