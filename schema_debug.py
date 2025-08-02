#!/usr/bin/env python3
"""
🔧 BACKEND DEVELOPER: DATABASE SCHEMA DEBUGGING TOOL
Analyzes the production database schema vs our local model definitions
"""

import os
from config.db import db
from app import create_app
from sqlalchemy import text

def check_table_columns():
    """Check actual column definitions in production database"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check attendance_sessions table structure
            print("🔍 ATTENDANCE_SESSIONS TABLE STRUCTURE:")
            print("=" * 50)
            
            result = db.session.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'attendance_sessions' 
                ORDER BY ordinal_position
            """))
            
            columns = result.fetchall()
            if columns:
                for col in columns:
                    print(f"  {col[0]:<20} | {col[1]:<15} | NULL: {col[2]:<5} | Default: {col[3]}")
            else:
                print("  ❌ No columns found or table doesn't exist")
            
            print("\n🔍 ATTENDANCE_RECORDS TABLE STRUCTURE:")
            print("=" * 50)
            
            result2 = db.session.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'attendance_records' 
                ORDER BY ordinal_position
            """))
            
            columns2 = result2.fetchall()
            if columns2:
                for col in columns2:
                    print(f"  {col[0]:<20} | {col[1]:<15} | NULL: {col[2]:<5} | Default: {col[3]}")
            else:
                print("  ❌ No columns found or table doesn't exist")
                
            # Test what happens when we query these tables
            print("\n🧪 TESTING ACTUAL QUERIES:")
            print("=" * 50)
            
            sessions = db.session.execute(text("SELECT * FROM attendance_sessions LIMIT 5")).fetchall()
            print(f"  Sessions found: {len(sessions)}")
            
            if sessions:
                # Check what columns actually exist in the result
                print("  First session column count:", len(sessions[0]))
                print("  Sample data keys available:")
                for i, session in enumerate(sessions[:2]):
                    print(f"    Session {i+1}: {len(session)} columns")
            
        except Exception as e:
            print(f"❌ Database Error: {str(e)}")
            print("This might be the SQL column error we're looking for!")
            
            # Try alternative method for SQLite
            try:
                print("\n🔄 TRYING SQLITE-STYLE SCHEMA CHECK:")
                result = db.session.execute(text("PRAGMA table_info(attendance_sessions)"))
                columns = result.fetchall()
                if columns:
                    print("  Columns found:")
                    for col in columns:
                        print(f"    {col}")
                        
            except Exception as e2:
                print(f"❌ Alternative check also failed: {str(e2)}")

if __name__ == "__main__":
    check_table_columns()
