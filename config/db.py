"""
🗄️ DATABASE CONFIGURATION - config/db.py

🎯 WHAT THIS FILE DOES:
This file sets up the database connection and initialization for the Flask app.
It configures SQLAlchemy to handle all database operations.

🔧 DATABASE SETUP:
- Creates SQLAlchemy instance for database operations
- Provides init_db() function to initialize database with app
- Handles database table creation and setup
"""

from flask_sqlalchemy import SQLAlchemy

# Create SQLAlchemy instance
db = SQLAlchemy()

def init_db(app):
    """Initialize database with Flask app."""
    db.init_app(app)
    
    with app.app_context():
        # Import all models to ensure they're registered with SQLAlchemy
        from models.user import User
        from models.organisation import Organisation
        from models.session import UserSession
        from models.attendance import AttendanceSession, AttendanceRecord
        
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # Run migration for attendance_sessions location columns
        _migrate_attendance_sessions_location_columns()
        
    return db

def _migrate_attendance_sessions_location_columns():
    """Add location columns to attendance_sessions if they don't exist."""
    try:
        # Check if we're using PostgreSQL (production) or SQLite (development)
        engine_name = db.engine.name
        
        if engine_name == 'postgresql':
            # PostgreSQL migration
            print("🔄 Checking attendance_sessions location columns (PostgreSQL)...")
            
            # Check if columns exist
            with db.engine.connect() as connection:
                result = connection.execute(db.text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'attendance_sessions' 
                    AND column_name IN ('latitude', 'longitude', 'radius', 'updated_at')
                """)).fetchall()
                
                existing_columns = [row[0] for row in result]
                
                columns_to_add = []
                if 'latitude' not in existing_columns:
                    columns_to_add.append("latitude FLOAT")
                if 'longitude' not in existing_columns:
                    columns_to_add.append("longitude FLOAT")
                if 'radius' not in existing_columns:
                    columns_to_add.append("radius INTEGER DEFAULT 100")
                if 'updated_at' not in existing_columns:
                    columns_to_add.append("updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                
                if columns_to_add:
                    print(f"➕ Adding missing location columns: {columns_to_add}")
                    for column_def in columns_to_add:
                        alter_query = f"ALTER TABLE attendance_sessions ADD COLUMN {column_def}"
                        connection.execute(db.text(alter_query))
                        connection.commit()
                        print(f"✅ Added column: {column_def}")
                else:
                    print("✅ All location columns already exist")
                
        elif engine_name == 'sqlite':
            # SQLite migration (simpler check)
            print("🔄 Checking attendance_sessions location columns (SQLite)...")
            
            with db.engine.connect() as connection:
                # Get table info
                result = connection.execute(db.text("PRAGMA table_info(attendance_sessions)")).fetchall()
                column_names = [row[1] for row in result]
                
                missing_columns = []
                if 'latitude' not in column_names:
                    missing_columns.append("ADD COLUMN latitude FLOAT")
                if 'longitude' not in column_names:
                    missing_columns.append("ADD COLUMN longitude FLOAT")
                if 'radius' not in column_names:
                    missing_columns.append("ADD COLUMN radius INTEGER DEFAULT 100")
                if 'updated_at' not in column_names:
                    missing_columns.append("ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP")
                
                if missing_columns:
                    print(f"➕ Adding missing location columns: {missing_columns}")
                    for column_def in missing_columns:
                        alter_query = f"ALTER TABLE attendance_sessions {column_def}"
                        connection.execute(db.text(alter_query))
                        connection.commit()
                        print(f"✅ Added column: {column_def}")
                else:
                    print("✅ All location columns already exist")
        
        print("✅ Migration check completed successfully!")
        
    except Exception as e:
        print(f"⚠️ Migration check failed (non-critical): {str(e)}")
        # Don't fail the entire app startup for migration issues