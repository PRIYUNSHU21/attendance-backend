#!/usr/bin/env python3
"""
🔧 PRODUCTION DATABASE SCHEMA CHECKER
Connects to the actual production database to diagnose SQL column errors
"""

import os
from config.db import db
from app import create_app
from sqlalchemy import text

def check_production_schema():
    """Check what's actually in the production database"""
    
    # Use production database URL if available
    if os.getenv('DATABASE_URL'):
        print("🌐 CONNECTING TO PRODUCTION DATABASE")
        print("=" * 50)
    else:
        print("📱 USING LOCAL DATABASE FOR TESTING")
        print("=" * 50)
    
    app = create_app()
    
    with app.app_context():
        try:
            # Check current active sessions first
            print("📊 CURRENT SESSIONS ANALYSIS:")
            sessions = db.session.execute(text("""
                SELECT COUNT(*) as total_sessions FROM attendance_sessions
            """)).fetchone()
            print(f"  Total sessions: {sessions[0]}")
            
            # Check if location column exists and has data
            try:
                location_data = db.session.execute(text("""
                    SELECT location, COUNT(*) as count 
                    FROM attendance_sessions 
                    WHERE location IS NOT NULL 
                    GROUP BY location
                    LIMIT 5
                """)).fetchall()
                
                print(f"  Sessions with location data: {len(location_data)}")
                for row in location_data:
                    print(f"    Location: '{row[0]}' (Count: {row[1]})")
                    
            except Exception as e:
                print(f"  ❌ Location column query failed: {e}")
            
            # Test the specific query that might be failing in our model
            print(f"\n🔍 TESTING MODEL COMPATIBILITY:")
            try:
                # This simulates what our AttendanceSession.query.all() would do
                result = db.session.execute(text("""
                    SELECT session_id, session_name, description, org_id,
                           start_time, end_time, latitude, longitude, radius,
                           created_by, created_at, updated_at, is_active
                    FROM attendance_sessions 
                    ORDER BY created_at DESC
                    LIMIT 3
                """)).fetchall()
                
                print(f"  ✅ Model-compatible query works: {len(result)} sessions")
                
                if result:
                    print("  Sample session data:")
                    for i, row in enumerate(result):
                        print(f"    Session {i+1}: {row[1]} (ID: {row[0][:8]}...)")
                        
            except Exception as e:
                print(f"  ❌ Model query failed: {e}")
                
            # Check if we can query without the location column  
            print(f"\n💊 TESTING THE FIX:")
            try:
                # Try to query all sessions excluding the problematic location column
                fixed_sessions = db.session.execute(text("""
                    SELECT session_id, session_name, start_time, end_time
                    FROM attendance_sessions
                    WHERE is_active = true
                    ORDER BY start_time DESC
                """)).fetchall()
                
                print(f"  ✅ Fixed query (no location column): {len(fixed_sessions)} sessions")
                
            except Exception as e:
                print(f"  ❌ Fixed query also failed: {e}")
                
        except Exception as e:
            print(f"❌ Database connection failed: {e}")

if __name__ == "__main__":
    check_production_schema()
