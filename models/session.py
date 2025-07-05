# models/session.py
"""
Session model module for handling user session-related operations.
This module provides functions to manage user authentication sessions.
It includes functionality to create, validate, and manage user sessions.
"""

import uuid
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from config.db import db

class UserSession(db.Model):
    """Model for user authentication sessions."""
    __tablename__ = 'user_sessions'
    
    session_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.user_id'), nullable=False)
    session_token = db.Column(db.String(255), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    device_info = db.Column(db.Text)  # Store device/browser info
    ip_address = db.Column(db.String(45))  # IPv4 or IPv6
    
    def __repr__(self):
        return f'<UserSession {self.session_id}>'
    
    def to_dict(self):
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'session_token': self.session_token,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active,
            'device_info': self.device_info,
            'ip_address': self.ip_address
        }
    
    def is_expired(self):
        """Check if the session is expired."""
        return datetime.utcnow() > self.expires_at

def create_session(user_id, session_token, device_info=None, ip_address=None, duration_hours=24):
    """Create a new user session."""
    try:
        expires_at = datetime.utcnow() + timedelta(hours=duration_hours)
        
        session = UserSession(
            user_id=user_id,
            session_token=session_token,
            expires_at=expires_at,
            device_info=device_info,
            ip_address=ip_address
        )
        db.session.add(session)
        db.session.commit()
        return session
    except Exception as e:
        db.session.rollback()
        raise e

def find_session_by_token(session_token):
    """Find a session by its token."""
    return UserSession.query.filter_by(
        session_token=session_token,
        is_active=True
    ).first()

def validate_session(session_token):
    """Validate a session token and return the associated user."""
    session = find_session_by_token(session_token)
    if not session:
        return None
    
    if session.is_expired():
        # Deactivate expired session
        session.is_active = False
        db.session.commit()
        return None
    
    return session.user

def invalidate_session(session_token):
    """Invalidate a session (logout)."""
    try:
        session = find_session_by_token(session_token)
        if session:
            session.is_active = False
            db.session.commit()
            return True
        return False
    except Exception as e:
        db.session.rollback()
        raise e

def cleanup_expired_sessions():
    """Clean up expired sessions."""
    try:
        expired_sessions = UserSession.query.filter(
            UserSession.expires_at < datetime.utcnow(),
            UserSession.is_active == True
        ).all()
        
        for session in expired_sessions:
            session.is_active = False
        
        db.session.commit()
        return len(expired_sessions)
    except Exception as e:
        db.session.rollback()
        raise e

def get_user_active_sessions(user_id):
    """Get all active sessions for a user."""
    return UserSession.query.filter_by(
        user_id=user_id,
        is_active=True
    ).filter(UserSession.expires_at > datetime.utcnow()).all()

def invalidate_all_user_sessions(user_id):
    """Invalidate all sessions for a user."""
    try:
        sessions = get_user_active_sessions(user_id)
        for session in sessions:
            session.is_active = False
        db.session.commit()
        return len(sessions)
    except Exception as e:
        db.session.rollback()
        raise e