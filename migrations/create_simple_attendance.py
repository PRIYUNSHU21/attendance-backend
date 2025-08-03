"""
📦 SIMPLIFIED ATTENDANCE DATABASE MIGRATION - migrations/create_simple_attendance.py

🎯 WHAT THIS DOES:
Creates a simplified attendance table inspired by Firebase approach.
Reduces complexity while maintaining SQL database benefits.

Key simplifications:
1. Single table for attendance records
2. Daily attendance records (one per user per day)
3. Simple status tracking
4. JSON/text storage for absent timestamps
5. Minimal foreign key constraints
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.db import db
from datetime import datetime

def create_simple_attendance_table():
    """Create simplified attendance table."""
    
    # Create simplified attendance records table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS simple_attendance_records (
        -- Primary identifier
        record_id VARCHAR(36) PRIMARY KEY,
        
        -- User and organization
        user_id VARCHAR(36) NOT NULL,
        org_id VARCHAR(36) NOT NULL,
        session_id VARCHAR(36),  -- Optional: for session-based attendance
        
        -- Location data
        latitude DECIMAL(10, 8) NOT NULL,
        longitude DECIMAL(11, 8) NOT NULL,
        altitude DECIMAL(10, 2) DEFAULT 0,
        
        -- Attendance status
        status VARCHAR(20) NOT NULL DEFAULT 'present' 
            CHECK (status IN ('present', 'absent')),
        
        -- Timing - simplified to daily attendance
        check_in_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        
        -- Store absent timestamps as comma-separated or JSON
        absent_timestamps TEXT,
        
        -- Indexes for performance
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
        FOREIGN KEY (org_id) REFERENCES organisations(org_id) ON DELETE CASCADE
    );
    """
    
    # Create indexes for performance
    create_indexes_sql = [
        "CREATE INDEX IF NOT EXISTS idx_simple_attendance_user_org ON simple_attendance_records(user_id, org_id);",
        "CREATE INDEX IF NOT EXISTS idx_simple_attendance_date ON simple_attendance_records(DATE(check_in_time));",
        "CREATE INDEX IF NOT EXISTS idx_simple_attendance_org ON simple_attendance_records(org_id);",
        "CREATE INDEX IF NOT EXISTS idx_simple_attendance_status ON simple_attendance_records(status);"
    ]
    
    # Add location columns to organisations table if they don't exist
    add_location_columns_sql = [
        """
        ALTER TABLE organisations 
        ADD COLUMN IF NOT EXISTS location_lat DECIMAL(10, 8);
        """,
        """
        ALTER TABLE organisations 
        ADD COLUMN IF NOT EXISTS location_lon DECIMAL(11, 8);
        """,
        """
        ALTER TABLE organisations 
        ADD COLUMN IF NOT EXISTS location_radius INTEGER DEFAULT 50;
        """
    ]
    
    try:
        # Execute table creation
        db.session.execute(db.text(create_table_sql))
        print("✅ Created simple_attendance_records table")
        
        # Execute indexes
        for index_sql in create_indexes_sql:
            db.session.execute(db.text(index_sql))
        print("✅ Created indexes for simple_attendance_records")
        
        # Add location columns to organisations
        for column_sql in add_location_columns_sql:
            try:
                db.session.execute(db.text(column_sql))
            except Exception as e:
                # Column might already exist
                print(f"Note: {e}")
        
        print("✅ Added location columns to organisations table")
        
        db.session.commit()
        print("✅ Simple attendance migration completed successfully")
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error in simple attendance migration: {str(e)}")
        return False

def rollback_simple_attendance_table():
    """Rollback simplified attendance table creation."""
    
    rollback_sql = [
        "DROP INDEX IF EXISTS idx_simple_attendance_user_org;",
        "DROP INDEX IF EXISTS idx_simple_attendance_date;", 
        "DROP INDEX IF EXISTS idx_simple_attendance_org;",
        "DROP INDEX IF EXISTS idx_simple_attendance_status;",
        "DROP TABLE IF EXISTS simple_attendance_records;"
    ]
    
    try:
        for sql in rollback_sql:
            db.session.execute(db.text(sql))
        
        db.session.commit()
        print("✅ Simple attendance table rollback completed")
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error in rollback: {str(e)}")
        return False

if __name__ == "__main__":
    """Run migration when script is executed directly."""
    from app import create_app
    
    app = create_app()
    with app.app_context():
        print("🚀 Running simplified attendance migration...")
        success = create_simple_attendance_table()
        
        if success:
            print("✅ Migration completed successfully!")
        else:
            print("❌ Migration failed!")
