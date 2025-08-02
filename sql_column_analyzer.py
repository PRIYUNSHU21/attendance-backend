#!/usr/bin/env python3
"""
🔧 BACKEND DEVELOPER: COMPREHENSIVE SQL COLUMN MISMATCH ANALYZER
Identifies all schema inconsistencies causing production errors
"""

import os
from config.db import db
from app import create_app
from sqlalchemy import text

def analyze_schema_mismatches():
    """Complete analysis of schema vs model mismatches"""
    app = create_app()
    
    with app.app_context():
        print("🏥 SCHEMA MISMATCH DIAGNOSIS")
        print("=" * 60)
        
        # Get actual database columns
        try:
            result = db.session.execute(text("PRAGMA table_info(attendance_sessions)"))
            db_columns = [row[1] for row in result.fetchall()]  # column names
            print("📊 DATABASE COLUMNS:")
            for col in db_columns:
                print(f"  ✓ {col}")
            
        except Exception as e:
            print(f"❌ Failed to get DB columns: {e}")
            return
        
        # Expected model columns from our models/attendance.py
        model_columns = [
            'session_id', 'session_name', 'description', 'org_id',
            'start_time', 'end_time', 'latitude', 'longitude', 'radius',
            'created_by', 'created_at', 'updated_at', 'is_active'
        ]
        
        print(f"\n🏗️  MODEL DEFINITION COLUMNS:")
        for col in model_columns:
            print(f"  ✓ {col}")
            
        # Find mismatches
        print(f"\n🚨 SCHEMA MISMATCH ANALYSIS:")
        print("-" * 40)
        
        # Columns in DB but not in model
        extra_in_db = set(db_columns) - set(model_columns)
        if extra_in_db:
            print("❌ COLUMNS IN DATABASE BUT NOT IN MODEL:")
            for col in extra_in_db:
                print(f"  🔥 {col} <- THIS CAUSES SQL ERRORS!")
        
        # Columns in model but not in DB  
        missing_in_db = set(model_columns) - set(db_columns)
        if missing_in_db:
            print("⚠️  COLUMNS IN MODEL BUT NOT IN DATABASE:")
            for col in missing_in_db:
                print(f"  📝 {col}")
        
        if not extra_in_db and not missing_in_db:
            print("✅ No schema mismatches found!")
            
        # Test actual query that might be failing
        print(f"\n🧪 TESTING PROBLEMATIC QUERIES:")
        print("-" * 40)
        
        try:
            # This is likely the query that's failing in production
            sessions = db.session.execute(text("""
                SELECT session_id, session_name, description, org_id, 
                       start_time, end_time, latitude, longitude, radius,
                       created_by, created_at, is_active
                FROM attendance_sessions 
                LIMIT 2
            """)).fetchall()
            
            print(f"✅ SELECT query works: {len(sessions)} sessions")
            
        except Exception as e:
            print(f"❌ SELECT query failed: {e}")
            
        # Check what happens when we try to use the extra column
        if 'location' in extra_in_db:
            try:
                result = db.session.execute(text("""
                    SELECT location FROM attendance_sessions LIMIT 1
                """)).fetchall()
                print(f"✅ 'location' column accessible: found {len(result)} rows")
                
            except Exception as e:
                print(f"❌ 'location' column query failed: {e}")

if __name__ == "__main__":
    analyze_schema_mismatches()
