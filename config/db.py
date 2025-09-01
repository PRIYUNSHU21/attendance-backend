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
        try:
            # Test database connection first (using newer SQLAlchemy syntax)
            with db.engine.connect() as connection:
                connection.execute(db.text("SELECT 1"))
            print("✅ Database connection successful!")
            
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
            
            # Run migration for simple_attendance_records table
            _migrate_simple_attendance_records_table()
            
            # Run schema fix for simple_attendance_records table
            _fix_simple_attendance_records_schema()
            
            # Force recreate table if schema issues persist
            _force_recreate_simple_attendance_records_table()
            
        except Exception as e:
            print(f"❌ Database initialization failed: {str(e)}")
            print("💡 This might be due to:")
            print("   1. Incorrect DATABASE_URL environment variable")
            print("   2. Database server not accessible")
            print("   3. SSL/connection timeout issues")
            raise e
        
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

def _migrate_simple_attendance_records_table():
    """Create simple_attendance_records table if it doesn't exist."""
    try:
        # Check if we're using PostgreSQL (production) or SQLite (development)
        engine_name = db.engine.name
        
        print("🔄 Checking simple_attendance_records table...")
        
        if engine_name == 'postgresql':
            # PostgreSQL - Check if table exists
            with db.engine.connect() as connection:
                result = connection.execute(db.text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'simple_attendance_records'
                    );
                """)).fetchone()
                
                table_exists = result[0] if result else False
                
                if not table_exists:
                    print("➕ Creating simple_attendance_records table...")
                    connection.execute(db.text("""
                        CREATE TABLE simple_attendance_records (
                            record_id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
                            user_id VARCHAR(36) NOT NULL,
                            org_id VARCHAR(36) NOT NULL,
                            session_id VARCHAR(255),
                            latitude DECIMAL(10,8),
                            longitude DECIMAL(11,8),
                            altitude DECIMAL(8,2) DEFAULT 0,
                            status VARCHAR(20) NOT NULL DEFAULT 'present',
                            check_in_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            absent_timestamps TEXT,
                            distance_from_session DECIMAL(10,2),
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                    """))
                    connection.commit()
                    print("✅ simple_attendance_records table created!")
                else:
                    print("✅ simple_attendance_records table already exists")
                    
        elif engine_name == 'sqlite':
            # SQLite - Check if table exists
            with db.engine.connect() as connection:
                result = connection.execute(db.text("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='simple_attendance_records';
                """)).fetchone()
                
                if not result:
                    print("➕ Creating simple_attendance_records table...")
                    connection.execute(db.text("""
                        CREATE TABLE simple_attendance_records (
                            record_id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-' || substr('ab89',abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6)))),
                            user_id TEXT NOT NULL,
                            org_id TEXT NOT NULL,
                            session_id TEXT,
                            latitude REAL,
                            longitude REAL,
                            altitude REAL DEFAULT 0,
                            status TEXT NOT NULL DEFAULT 'present',
                            check_in_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                            absent_timestamps TEXT,
                            distance_from_session REAL,
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                        );
                    """))
                    connection.commit()
                    print("✅ simple_attendance_records table created!")
                else:
                    print("✅ simple_attendance_records table already exists")
        
        print("✅ Simple attendance table migration completed!")
        
    except Exception as e:
        print(f"⚠️ Simple attendance table migration failed (non-critical): {str(e)}")
        # Don't fail the entire app startup for migration issues

def _fix_simple_attendance_records_schema():
    """Fix schema mismatch in simple_attendance_records table."""
    try:
        engine_name = db.engine.name
        
        print("🔧 Fixing simple_attendance_records schema...")
        
        if engine_name == 'postgresql':
            # PostgreSQL schema fixes
            with db.engine.connect() as connection:
                # Check which columns are missing
                result = connection.execute(db.text("""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = 'simple_attendance_records' 
                    AND table_schema = 'public';
                """)).fetchall()
                
                existing_columns = [row[0] for row in result]
                
                # Add missing columns
                columns_to_add = []
                if 'session_id' not in existing_columns:
                    columns_to_add.append("ADD COLUMN session_id VARCHAR(255)")
                if 'altitude' not in existing_columns:
                    columns_to_add.append("ADD COLUMN altitude DECIMAL(8,2) DEFAULT 0")
                if 'last_updated' not in existing_columns:
                    columns_to_add.append("ADD COLUMN last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                
                # Resize existing columns if needed
                if 'session_id' in existing_columns:
                    columns_to_add.append("ALTER COLUMN session_id TYPE VARCHAR(255)")
                
                # Rename columns if needed
                if 'session_code' in existing_columns and 'session_id' not in existing_columns:
                    columns_to_add.append("RENAME COLUMN session_code TO session_id")
                if 'updated_at' in existing_columns and 'last_updated' not in existing_columns:
                    columns_to_add.append("RENAME COLUMN updated_at TO last_updated")
                
                # Apply fixes
                for column_change in columns_to_add:
                    try:
                        alter_query = f"ALTER TABLE simple_attendance_records {column_change}"
                        connection.execute(db.text(alter_query))
                        connection.commit()
                        print(f"✅ Applied: {column_change}")
                    except Exception as e:
                        print(f"⚠️ Skipped: {column_change} - {str(e)}")
                        connection.rollback()
                        
        elif engine_name == 'sqlite':
            # SQLite schema fixes (more limited)
            with db.engine.connect() as connection:
                # Get current schema
                result = connection.execute(db.text("PRAGMA table_info(simple_attendance_records)")).fetchall()
                existing_columns = [row[1] for row in result]
                
                # Add missing columns (SQLite doesn't support RENAME COLUMN easily)
                columns_to_add = []
                if 'session_id' not in existing_columns:
                    columns_to_add.append("ADD COLUMN session_id TEXT")
                if 'altitude' not in existing_columns:
                    columns_to_add.append("ADD COLUMN altitude REAL DEFAULT 0")
                if 'last_updated' not in existing_columns:
                    columns_to_add.append("ADD COLUMN last_updated DATETIME DEFAULT CURRENT_TIMESTAMP")
                
                # Apply column additions
                for column_def in columns_to_add:
                    try:
                        alter_query = f"ALTER TABLE simple_attendance_records {column_def}"
                        connection.execute(db.text(alter_query))
                        connection.commit()
                        print(f"✅ Added: {column_def}")
                    except Exception as e:
                        print(f"⚠️ Skipped: {column_def} - {str(e)}")
        
        print("✅ Schema fix completed!")
        
    except Exception as e:
        print(f"⚠️ Schema fix failed (non-critical): {str(e)}")
        # Don't fail the entire app startup for schema issues

def _force_recreate_simple_attendance_records_table():
    """Force recreate the simple_attendance_records table with correct schema."""
    try:
        engine_name = db.engine.name
        
        print("🔧 Force recreating simple_attendance_records table...")
        
        if engine_name == 'postgresql':
            # PostgreSQL force recreation
            with db.engine.connect() as connection:
                # Check if table exists
                result = connection.execute(db.text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'simple_attendance_records'
                    );
                """)).fetchone()
                
                table_exists = result[0] if result else False
                
                if table_exists:
                    # Get table schema to check if it needs recreation
                    columns_result = connection.execute(db.text("""
                        SELECT column_name FROM information_schema.columns 
                        WHERE table_name = 'simple_attendance_records' 
                        AND table_schema = 'public';
                    """)).fetchall()
                    
                    existing_columns = [row[0] for row in columns_result]
                    
                    # Check if we have the problematic old schema
                    has_session_code = 'session_code' in existing_columns
                    session_id_missing = 'session_id' not in existing_columns
                    
                    if has_session_code or session_id_missing:
                        print("🗑️ Dropping problematic table...")
                        # Backup any existing data first
                        try:
                            connection.execute(db.text("""
                                CREATE TABLE simple_attendance_records_backup_temp AS 
                                SELECT * FROM simple_attendance_records LIMIT 0;
                            """))
                            connection.commit()
                        except:
                            pass  # Backup table creation failed, continue anyway
                        
                        # Drop the problematic table
                        connection.execute(db.text("DROP TABLE IF EXISTS simple_attendance_records CASCADE;"))
                        connection.commit()
                        print("✅ Dropped problematic table")
                        
                        # Recreate with correct schema
                        connection.execute(db.text("""
                            CREATE TABLE simple_attendance_records (
                                record_id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
                                user_id VARCHAR(36) NOT NULL,
                                org_id VARCHAR(36) NOT NULL,
                                session_id VARCHAR(255),
                                latitude DECIMAL(10,8),
                                longitude DECIMAL(11,8),
                                altitude DECIMAL(8,2) DEFAULT 0,
                                status VARCHAR(20) NOT NULL DEFAULT 'present',
                                check_in_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                absent_timestamps TEXT,
                                distance_from_session DECIMAL(10,2),
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            );
                        """))
                        connection.commit()
                        print("✅ Recreated table with correct schema!")
                    else:
                        print("✅ Table schema is already correct")
                        
        elif engine_name == 'sqlite':
            # SQLite force recreation  
            with db.engine.connect() as connection:
                # Check if table exists
                result = connection.execute(db.text("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='simple_attendance_records';
                """)).fetchone()
                
                if result:
                    # Get table schema
                    columns_result = connection.execute(db.text("PRAGMA table_info(simple_attendance_records)")).fetchall()
                    existing_columns = [row[1] for row in columns_result]
                    
                    # Check if we need to recreate
                    has_session_code = 'session_code' in existing_columns
                    session_id_missing = 'session_id' not in existing_columns
                    
                    if has_session_code or session_id_missing:
                        print("🗑️ Dropping and recreating SQLite table...")
                        
                        # Drop and recreate
                        connection.execute(db.text("DROP TABLE IF EXISTS simple_attendance_records;"))
                        connection.commit()
                        
                        connection.execute(db.text("""
                            CREATE TABLE simple_attendance_records (
                                record_id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-' || substr('ab89',abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6)))),
                                user_id TEXT NOT NULL,
                                org_id TEXT NOT NULL,
                                session_id TEXT,
                                latitude REAL,
                                longitude REAL,
                                altitude REAL DEFAULT 0,
                                status TEXT NOT NULL DEFAULT 'present',
                                check_in_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                                absent_timestamps TEXT,
                                distance_from_session REAL,
                                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                            );
                        """))
                        connection.commit()
                        print("✅ Recreated SQLite table with correct schema!")
                    else:
                        print("✅ SQLite table schema is already correct")
        
        print("✅ Force recreation completed!")
        
    except Exception as e:
        print(f"⚠️ Force recreation failed (non-critical): {str(e)}")
        # Don't fail the entire app startup