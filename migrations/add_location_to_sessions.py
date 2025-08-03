"""
Migration to add location columns to attendance_sessions table
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
from config.db import db

def run_migration():
    """Add location columns to attendance_sessions table."""
    try:
        print("Running migration: Add location columns to attendance_sessions table")
        
        # Check if columns already exist
        check_query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'attendance_sessions' AND column_name = 'latitude'
        """
        
        # For SQLite compatibility, use a different approach
        try:
            # Try PostgreSQL-style query first
            result = db.session.execute(db.text(check_query)).fetchone()
        except Exception:
            # Fallback for SQLite
            try:
                result = db.session.execute(db.text("PRAGMA table_info(attendance_sessions)")).fetchall()
                column_names = [col[1] for col in result]
                result = 'latitude' in column_names
            except Exception as e:
                print(f"Error checking column existence: {str(e)}")
                result = None
        
        if not result:
            print("Adding location columns to attendance_sessions table...")
            
            # Add location columns
            try:
                # For PostgreSQL/Production
                db.session.execute(db.text("ALTER TABLE attendance_sessions ADD COLUMN latitude REAL"))
                db.session.execute(db.text("ALTER TABLE attendance_sessions ADD COLUMN longitude REAL"))
                db.session.execute(db.text("ALTER TABLE attendance_sessions ADD COLUMN radius INTEGER DEFAULT 100"))
                db.session.commit()
                print("✅ Location columns added to attendance_sessions table")
            except Exception as postgres_error:
                print(f"PostgreSQL add failed: {postgres_error}")
                db.session.rollback()
                
                # Try SQLite syntax
                try:
                    db.session.execute(db.text("ALTER TABLE attendance_sessions ADD COLUMN latitude REAL"))
                    db.session.execute(db.text("ALTER TABLE attendance_sessions ADD COLUMN longitude REAL"))
                    db.session.execute(db.text("ALTER TABLE attendance_sessions ADD COLUMN radius INTEGER DEFAULT 100"))
                    db.session.commit()
                    print("✅ Location columns added to attendance_sessions table (SQLite)")
                except Exception as sqlite_error:
                    print(f"SQLite add also failed: {sqlite_error}")
                    db.session.rollback()
                    raise sqlite_error
        else:
            print("✅ Location columns already exist in attendance_sessions table")
            
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        db.session.rollback()
        raise e

if __name__ == "__main__":
    from app import create_app
    
    app = create_app()
    with app.app_context():
        run_migration()
