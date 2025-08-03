"""
Database migration endpoint to fix production schema
"""
from flask import Blueprint, request
from config.db import db
from sqlalchemy import text
from utils.auth import token_required, admin_required
from utils.response import success_response, error_response

migration_bp = Blueprint('migration', __name__, url_prefix='/migration')

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
