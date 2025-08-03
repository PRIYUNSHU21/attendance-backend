"""
Migration to add location columns to organisations table
"""
from datetime import datetime
from config.db import db

def run_migration():
    """Add location columns to organisations table."""
    try:
        print("Running migration: Add location columns to organisations table")
        
        # Check if columns already exist
        check_query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'organisations' AND column_name = 'location_lat'
        """
        
        # For SQLite compatibility, use a different approach
        try:
            # Try PostgreSQL-style query first
            result = db.session.execute(db.text(check_query)).fetchone()
        except Exception:
            # Fallback for SQLite
            try:
                result = db.session.execute(db.text("PRAGMA table_info(organisations)")).fetchall()
                column_names = [col[1] for col in result]
                result = 'location_lat' in column_names
            except Exception as e:
                print(f"Error checking column existence: {str(e)}")
                result = None
        
        # If columns don't exist (result is None or False), add them
        if not result:
            if db.engine.url.drivername == 'sqlite':
                # SQLite syntax
                migrations = [
                    "ALTER TABLE organisations ADD COLUMN location_lat REAL;",
                    "ALTER TABLE organisations ADD COLUMN location_lon REAL;",
                    "ALTER TABLE organisations ADD COLUMN location_radius INTEGER DEFAULT 100;"
                ]
            else:
                # PostgreSQL syntax
                migrations = [
                    "ALTER TABLE organisations ADD COLUMN location_lat DECIMAL(10, 8);",
                    "ALTER TABLE organisations ADD COLUMN location_lon DECIMAL(11, 8);",
                    "ALTER TABLE organisations ADD COLUMN location_radius INTEGER DEFAULT 100;"
                ]
            
            for migration in migrations:
                db.session.execute(db.text(migration))
            
            # Log the migration
            print("✅ Added location columns to organisations table")
            
            # Commit changes
            db.session.commit()
        else:
            print("ℹ️ Location columns already exist, skipping migration")
        
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Migration failed: {str(e)}")
        return False

if __name__ == "__main__":
    run_migration()
