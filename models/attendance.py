"""
📚 ATTENDANCE MODELS - models/attendance.py

🎯 WHAT THIS FILE DOES:
This file defines attendance-related data models and database operations:
- AttendanceSession: Represents a class/meeting session
- AttendanceRecord: Individual attendance records for users
- Helper functions for attendance operations

🔧 DATABASE STRUCTURE:
- AttendanceSession: Sessions that users can attend
- AttendanceRecord: Individual check-ins/check-outs for sessions

📋 AVAILABLE FUNCTIONS:
- get_active_sessions(): Get active sessions for organization
- mark_attendance(): Record user attendance  
- get_session_attendance(): Get attendance for specific session
- get_user_attendance(): Get attendance history for user
"""

import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from config.db import db

class AttendanceSession(db.Model):
    """Model for attendance sessions (classes, meetings, etc.)."""
    __tablename__ = 'attendance_sessions'
    
    session_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    org_id = db.Column(db.String(36), db.ForeignKey('organisations.org_id', ondelete='CASCADE'), nullable=False)
    
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    
    # Location data for geo-fencing (optional fields for backward compatibility)
    location = db.Column(db.String(500))  # Legacy location field - exists in DB
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float) 
    radius = db.Column(db.Integer, default=100)  # meters
    
    # Session management
    created_by = db.Column(db.String(36), db.ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        """Convert session to dictionary."""
        return {
            'session_id': self.session_id,
            'session_name': self.session_name,
            'description': self.description,
            'org_id': self.org_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'location': self.location,  # Include legacy location field
            'latitude': self.latitude,
            'longitude': self.longitude,
            'radius': self.radius,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }

class AttendanceRecord(db.Model):
    """Model for individual attendance records."""
    __tablename__ = 'attendance_records'
    
    record_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = db.Column(db.String(36), db.ForeignKey('attendance_sessions.session_id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    org_id = db.Column(db.String(36), db.ForeignKey('organisations.org_id', ondelete='CASCADE'), nullable=False)
    
    # Attendance status
    status = db.Column(db.String(20), default='present')  # present, late, absent
    
    # Timing
    check_in_time = db.Column(db.DateTime)
    check_out_time = db.Column(db.DateTime)
    
    # Location verification
    check_in_latitude = db.Column(db.Float)
    check_in_longitude = db.Column(db.Float)
    check_out_latitude = db.Column(db.Float)
    check_out_longitude = db.Column(db.Float)
    location_verified = db.Column(db.Boolean, default=False)
    
    # Metadata
    created_by = db.Column(db.String(36), db.ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert record to dictionary."""
        return {
            'record_id': self.record_id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'org_id': self.org_id,
            'status': self.status,
            'check_in_time': self.check_in_time.isoformat() if self.check_in_time else None,
            'check_out_time': self.check_out_time.isoformat() if self.check_out_time else None,
            'check_in_latitude': self.check_in_latitude,
            'check_in_longitude': self.check_in_longitude,
            'check_out_latitude': self.check_out_latitude,
            'check_out_longitude': self.check_out_longitude,
            'location_verified': self.location_verified,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# Helper Functions
def get_active_sessions(org_id):
    """
    Get all active sessions for an organization.
    
    Args:
        org_id: Organization ID
        
    Returns:
        List of active sessions
    """
    try:
        current_time = datetime.now()
        sessions = AttendanceSession.query.filter(
            AttendanceSession.org_id == org_id,
            AttendanceSession.is_active == True,
            AttendanceSession.start_time <= current_time,
            AttendanceSession.end_time >= current_time
        ).all()
        
        return sessions
    except Exception as e:
        print(f"Error getting active sessions: {str(e)}")
        return []

def mark_attendance(session_id, user_id, org_id, latitude=None, longitude=None, created_by=None):
    """
    Mark attendance for a user in a session.
    
    Args:
        session_id: Session ID
        user_id: User ID
        org_id: Organization ID
        latitude: Check-in latitude
        longitude: Check-in longitude
        created_by: Who created this record
        
    Returns:
        AttendanceRecord object or None
    """
    try:
        # Check if already marked
        existing = AttendanceRecord.query.filter(
            AttendanceRecord.session_id == session_id,
            AttendanceRecord.user_id == user_id
        ).first()
        
        if existing:
            return existing
        
        # Create new record
        record = AttendanceRecord(
            session_id=session_id,
            user_id=user_id,
            org_id=org_id,
            check_in_time=datetime.now(),
            check_in_latitude=latitude,
            check_in_longitude=longitude,
            location_verified=True if latitude and longitude else False,
            created_by=created_by or user_id
        )
        
        db.session.add(record)
        db.session.commit()
        return record
        
    except Exception as e:
        print(f"Error marking attendance: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return None

def get_session_attendance(session_id):
    """
    Get all attendance records for a session.
    
    Args:
        session_id: Session ID
        
    Returns:
        List of attendance records
    """
    try:
        records = AttendanceRecord.query.filter(
            AttendanceRecord.session_id == session_id
        ).all()
        
        return [record.to_dict() for record in records]
    except Exception as e:
        print(f"Error getting session attendance: {str(e)}")
        return []

def get_user_attendance(user_id, org_id=None, limit=50):
    """
    Get attendance history for a user.
    
    Args:
        user_id: User ID
        org_id: Organization ID (optional filter)
        limit: Maximum records to return
        
    Returns:
        List of attendance records
    """
    try:
        query = AttendanceRecord.query.filter(
            AttendanceRecord.user_id == user_id
        )
        
        if org_id:
            query = query.filter(AttendanceRecord.org_id == org_id)
        
        records = query.order_by(
            AttendanceRecord.created_at.desc()
        ).limit(limit).all()
        
        return [record.to_dict() for record in records]
    except Exception as e:
        print(f"Error getting user attendance: {str(e)}")
        return []

def create_session_model(data):
    """
    Create a new attendance session.
    
    Args:
        data: Session data dictionary
        
    Returns:
        AttendanceSession object or None
    """
    try:
        print(f"DEBUG: Creating session with data: {data}")
        session = AttendanceSession(
            session_name=data.get('session_name'),
            description=data.get('description'),
            org_id=data.get('org_id'),
            start_time=data.get('start_time'),  # Already converted to datetime
            end_time=data.get('end_time'),      # Already converted to datetime
            location=data.get('location'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            radius=data.get('radius', 100),
            created_by=data.get('created_by'),
            is_active=data.get('is_active', True)
        )
        
        print(f"DEBUG: Session object created: {session.session_id}")
        db.session.add(session)
        db.session.commit()
        print(f"DEBUG: Session committed to database")
        return session
        
    except Exception as e:
        print(f"DEBUG: Error creating attendance session: {str(e)}")
        db.session.rollback()
        return None

def mark_checkout(session_id, user_id, latitude=None, longitude=None):
    """
    Mark checkout for a user in a session.
    
    Args:
        session_id: Session ID
        user_id: User ID
        latitude: Checkout latitude
        longitude: Checkout longitude
        
    Returns:
        AttendanceRecord object or None
    """
    try:
        # Find existing attendance record
        record = AttendanceRecord.query.filter(
            AttendanceRecord.session_id == session_id,
            AttendanceRecord.user_id == user_id
        ).first()
        
        if not record:
            print(f"No attendance record found for user {user_id} in session {session_id}")
            return None
        
        # Update checkout information
        record.check_out_time = datetime.now()
        if latitude and longitude:
            record.check_out_latitude = latitude
            record.check_out_longitude = longitude
        
        db.session.commit()
        return record
        
    except Exception as e:
        print(f"Error marking checkout: {str(e)}")
        db.session.rollback()
        return None
