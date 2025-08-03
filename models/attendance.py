"""
📚 ATTENDANCE MODELS - Core attendance data models
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
    
    # Location data for geo-fencing (production database column names)
    location_lat = db.Column(db.Float)     # Production has location_lat 
    location_lon = db.Column(db.Float)     # Production has location_lon
    location_radius = db.Column(db.Float)  # Production has location_radius
    
    # Session management
    created_by = db.Column(db.String(36), db.ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
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
            'latitude': self.location_lat,    # Map production column to expected field
            'longitude': self.location_lon,   # Map production column to expected field
            'radius': self.location_radius,   # Map production column to expected field
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
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
    check_in_lat = db.Column(db.Float)
    check_in_lon = db.Column(db.Float)
    check_out_lat = db.Column(db.Float)
    check_out_lon = db.Column(db.Float)
    location_verified = db.Column(db.Boolean, default=False)
    
    # Metadata
    created_by = db.Column(db.String(36), db.ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
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
            'check_in_lat': self.check_in_lat,
            'check_in_lon': self.check_in_lon,
            'check_out_lat': self.check_out_lat,
            'check_out_lon': self.check_out_lon,
            'location_verified': self.location_verified,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
