"""
Database migration endpoint to fix production schema
"""
from flask import Blueprint, request
from config.db import db
from sqlalchemy import text
from utils.auth import token_required, admin_required
from utils.response import success_response, error_response

migration_bp = Blueprint('migration', __name__, url_prefix='/migration')

@migration_bp.route('/check-attendance-records-schema', methods=['GET'])
@token_required
@admin_required  
def check_attendance_records_schema():
    """Check the schema of attendance_records table"""
    try:
        # Get column information for attendance_records table
        result = db.session.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'attendance_records'
            ORDER BY ordinal_position
        """))
        
        columns = []
        for row in result.fetchall():
            columns.append({
                "name": row[0],
                "type": row[1], 
                "nullable": row[2],
                "default": row[3]
            })
        
        return success_response(
            message="attendance_records schema retrieved successfully",
            data={"columns": columns}
        )
        
    except Exception as e:
        return error_response(f"Failed to check attendance_records schema: {str(e)}", 500)

@migration_bp.route('/check-tables', methods=['GET'])
@token_required
@admin_required
def check_tables():
    """Check what tables exist in the database"""
    try:
        # Get all tables
        result = db.session.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """))
        
        tables = [row[0] for row in result.fetchall()]
        
        return success_response(
            message="Tables retrieved successfully",
            data={"tables": tables}
        )
        
    except Exception as e:
        return error_response(f"Failed to check tables: {str(e)}", 500)

@migration_bp.route('/create-attendance-records-table', methods=['POST'])
@token_required
@admin_required
def create_attendance_records_table():
    """Create attendance_records table if it doesn't exist"""
    try:
        # Check if table exists
        result = db.session.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = 'attendance_records'
        """))
        
        existing = result.fetchone()
        if existing:
            return success_response(
                message="attendance_records table already exists",
                data={"status": "already_exists"}
            )
        
        # Create the attendance_records table
        db.session.execute(text("""
            CREATE TABLE attendance_records (
                record_id VARCHAR(36) PRIMARY KEY,
                session_id VARCHAR(36) NOT NULL,
                user_id VARCHAR(36) NOT NULL,
                org_id VARCHAR(36) NOT NULL,
                status VARCHAR(20) DEFAULT 'present',
                check_in_time TIMESTAMP,
                check_out_time TIMESTAMP,
                check_in_latitude DOUBLE PRECISION,
                check_in_longitude DOUBLE PRECISION,
                check_out_latitude DOUBLE PRECISION,
                check_out_longitude DOUBLE PRECISION,
                location_verified BOOLEAN DEFAULT FALSE,
                created_by VARCHAR(36),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES attendance_sessions(session_id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (org_id) REFERENCES organisations(org_id) ON DELETE CASCADE,
                FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL
            )
        """))
        
        # Create indexes
        db.session.execute(text("""
            CREATE INDEX idx_attendance_records_session_id ON attendance_records(session_id)
        """))
        
        db.session.execute(text("""
            CREATE INDEX idx_attendance_records_user_id ON attendance_records(user_id)
        """))
        
        db.session.execute(text("""
            CREATE INDEX idx_attendance_records_user_session ON attendance_records(user_id, session_id)
        """))
        
        db.session.commit()
        
        return success_response(
            message="attendance_records table created successfully",
            data={"status": "created"}
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to create attendance_records table: {str(e)}", 500)

@migration_bp.route('/add-location-column', methods=['POST'])
@token_required
@admin_required
def add_location_column():
    """Add missing location column to attendance_sessions table in production"""
    try:
        # Check if column already exists
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'attendance_sessions' 
            AND column_name = 'location'
        """))
        
        existing = result.fetchone()
        if existing:
            return success_response(
                message="Location column already exists",
                data={"status": "already_exists"}
            )
        
        # Add the missing column
        db.session.execute(text("""
            ALTER TABLE attendance_sessions 
            ADD COLUMN location VARCHAR(500)
        """))
        
        db.session.commit()
        
        return success_response(
            message="Location column added successfully",
            data={"status": "added"}
        )
        
    except Exception as e:
        db.session.rollback()
        # Try SQLite syntax if PostgreSQL fails
        try:
            # For SQLite databases
            db.session.execute(text("""
                ALTER TABLE attendance_sessions 
                ADD COLUMN location TEXT
            """))
            db.session.commit()
            
            return success_response(
                message="Location column added successfully (SQLite)",
                data={"status": "added_sqlite"}
            )
            
        except Exception as e2:
            db.session.rollback()
            return error_response(f"Failed to add column: {str(e)} | {str(e2)}", 500)

@migration_bp.route('/check-schema', methods=['GET'])
@token_required
@admin_required  
def check_schema():
    """Check current database schema"""
    try:
        # Try PostgreSQL first
        result = db.session.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'attendance_sessions'
            ORDER BY ordinal_position
        """))
        
        columns = [{"name": row[0], "type": row[1]} for row in result.fetchall()]
        
        return success_response(
            message="Schema retrieved successfully",
            data={"columns": columns, "database_type": "postgresql"}
        )
        
    except Exception as e:
        # Try SQLite
        try:
            result = db.session.execute(text("PRAGMA table_info(attendance_sessions)"))
            columns = []
            for row in result.fetchall():
                columns.append({
                    "name": row[1], 
                    "type": row[2],
                    "nullable": not bool(row[3]),
                    "primary_key": bool(row[5])
                })
            
            return success_response(
                message="Schema retrieved successfully", 
                data={"columns": columns, "database_type": "sqlite"}
            )
            
        except Exception as e2:
            return error_response(f"Failed to check schema: {str(e)} | {str(e2)}", 500)
