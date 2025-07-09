# models/attendance.py
"""
Attendance model module for handling attendance-related operations.
This module provides SQLAlchemy database models and functions to manage attendance records.
It includes functionality to create attendance records, mark check-ins/check-outs,
and retrieve attendance data for reporting purposes.
"""

import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from config.db import db

class AttendanceSession(db.Model):
    """Model for attendance sessions (classes/meetings)."""
    __tablename__ = 'attendance_sessions'
    
    session_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = db.Column(db.String(36), db.ForeignKey('organisations.org_id', ondelete='CASCADE'), nullable=False)
    session_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    location_lat = db.Column(db.Float)
    location_lon = db.Column(db.Float)
    location_radius = db.Column(db.Float, default=100.0)  # radius in meters
    created_by = db.Column(db.String(36), db.ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<AttendanceSession {self.session_name}>'
    
    def to_dict(self):
        return {
            'session_id': self.session_id,
            'org_id': self.org_id,
            'session_name': self.session_name,
            'description': self.description,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'location_lat': self.location_lat,
            'location_lon': self.location_lon,
            'location_radius': self.location_radius,
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
    check_in_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    check_out_time = db.Column(db.DateTime)
    check_in_lat = db.Column(db.Float)
    check_in_lon = db.Column(db.Float)
    check_out_lat = db.Column(db.Float)
    check_out_lon = db.Column(db.Float)
    status = db.Column(db.String(20), default='present')  # 'present', 'late', 'absent'
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AttendanceRecord {self.user_id} - {self.session_id}>'
    
    def to_dict(self):
        return {
            'record_id': self.record_id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'check_in_time': self.check_in_time.isoformat() if self.check_in_time else None,
            'check_out_time': self.check_out_time.isoformat() if self.check_out_time else None,
            'check_in_lat': self.check_in_lat,
            'check_in_lon': self.check_in_lon,
            'check_out_lat': self.check_out_lat,
            'check_out_lon': self.check_out_lon,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Helper functions for attendance operations

def create_attendance_session(data):
    """Create a new attendance session."""
    try:
        session = AttendanceSession(
            org_id=data["org_id"],
            session_name=data["session_name"],
            description=data.get("description"),
            start_time=data["start_time"],
            end_time=data["end_time"],
            location_lat=data.get("location_lat"),
            location_lon=data.get("location_lon"),
            location_radius=data.get("location_radius", 100.0),
            created_by=data["created_by"]
        )
        db.session.add(session)
        db.session.commit()
        return session
    except Exception as e:
        db.session.rollback()
        raise e

def mark_attendance(session_id, user_id, lat=None, lon=None, status='present'):
    """Mark attendance for a user in a session."""
    try:
        # Check if attendance already exists
        existing_record = AttendanceRecord.query.filter_by(
            session_id=session_id,
            user_id=user_id
        ).first()
        
        if existing_record:
            return {"error": "Attendance already marked for this session"}
        
        record = AttendanceRecord(
            session_id=session_id,
            user_id=user_id,
            check_in_lat=lat,
            check_in_lon=lon,
            status=status
        )
        db.session.add(record)
        db.session.commit()
        return record
    except Exception as e:
        db.session.rollback()
        raise e

def mark_checkout(record_id, lat=None, lon=None):
    """Mark checkout for an attendance record."""
    try:
        record = AttendanceRecord.query.filter_by(record_id=record_id).first()
        if not record:
            return None
        
        record.check_out_time = datetime.utcnow()
        record.check_out_lat = lat
        record.check_out_lon = lon
        db.session.commit()
        return record
    except Exception as e:
        db.session.rollback()
        raise e

def get_session_attendance(session_id):
    """Get all attendance records for a session."""
    return AttendanceRecord.query.filter_by(session_id=session_id).all()

def get_user_attendance(user_id, org_id=None):
    """Get all attendance records for a user."""
    query = AttendanceRecord.query.filter_by(user_id=user_id)
    if org_id:
        query = query.join(AttendanceSession).filter(AttendanceSession.org_id == org_id)
    return query.all()

def get_active_sessions(org_id):
    """Get all active attendance sessions for an organization."""
    return AttendanceSession.query.filter_by(org_id=org_id, is_active=True).all()