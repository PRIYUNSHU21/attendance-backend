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
    user_id = db.Column(db.String(36), db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
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

class InvalidatedSession(db.Model):
    """Model for tracking invalidated sessions (security audit trail)."""
    __tablename__ = 'invalidated_sessions'
    
    session_id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    org_id = db.Column(db.String(36), db.ForeignKey('organisations.org_id', ondelete='CASCADE'), nullable=False)
    session_token = db.Column(db.String(255), nullable=False)
    invalidated_at = db.Column(db.DateTime, default=datetime.utcnow)
    reason = db.Column(db.String(255), nullable=False)
    
    def __repr__(self):
        return f'<InvalidatedSession {self.session_id}>'
    
    def to_dict(self):
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'org_id': self.org_id,
            'session_token': self.session_token,
            'invalidated_at': self.invalidated_at.isoformat() if self.invalidated_at else None,
            'reason': self.reason
        }

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

def invalidate_session(session_token, reason='manual_logout'):
    """Invalidate a session (logout) with audit trail."""
    try:
        session = find_session_by_token(session_token)
        if session:
            # Get user info for audit trail
            from models.user import User
            user = User.query.filter(User.user_id == session.user_id).first()
            org_id = user.org_id if user else None
            
            # Mark session as inactive
            session.is_active = False
            
            # Add to invalidated sessions audit trail
            invalidated_session = InvalidatedSession(
                session_id=session.session_id,
                user_id=session.user_id,
                org_id=org_id,
                session_token=session_token,
                reason=reason
            )
            
            db.session.add(invalidated_session)
            db.session.commit()
            return True
        return False
    except Exception as e:
        db.session.rollback()
        raise e

def invalidate_user_sessions(user_id, reason='user_deleted'):
    """Invalidate all active sessions for a specific user with audit trail."""
    try:
        sessions = UserSession.query.filter(
            UserSession.user_id == user_id,
            UserSession.is_active == True
        ).all()
        
        # Get user info for audit trail
        from models.user import User
        user = User.query.filter(User.user_id == user_id).first()
        org_id = user.org_id if user else None
        
        count = 0
        for session in sessions:
            # Mark session as inactive
            session.is_active = False
            
            # Add to audit trail
            invalidated_session = InvalidatedSession(
                session_id=session.session_id,
                user_id=session.user_id,
                org_id=org_id,
                session_token=session.session_token,
                reason=reason
            )
            db.session.add(invalidated_session)
            count += 1
        
        db.session.commit()
        return count
    except Exception as e:
        db.session.rollback()
        raise e

def invalidate_organization_sessions(org_id, reason='org_deleted'):
    """
    Invalidate all active sessions for users in a specific organization.
    
    🔒 SECURITY FEATURE: When an organization is deleted, this function
    ensures all user sessions from that organization are immediately invalidated.
    """
    try:
        from models.user import User
        
        # Get all sessions for users in the organization
        sessions = db.session.query(UserSession).join(
            User, UserSession.user_id == User.user_id
        ).filter(
            User.org_id == org_id,
            UserSession.is_active == True
        ).all()
        
        count = 0
        for session in sessions:
            # Mark session as inactive
            session.is_active = False
            
            # Add to audit trail
            invalidated_session = InvalidatedSession(
                session_id=session.session_id,
                user_id=session.user_id,
                org_id=org_id,
                session_token=session.session_token,
                reason=reason
            )
            db.session.add(invalidated_session)
            count += 1
        
        db.session.commit()
        return count
    except Exception as e:
        db.session.rollback()
        raise e

def is_session_blacklisted(session_token):
    """Check if a session token is in the blacklist."""
    try:
        blacklisted = InvalidatedSession.query.filter(
            InvalidatedSession.session_token == session_token
        ).first()
        return blacklisted is not None
    except Exception as e:
        return False

def is_session_valid(session_token):
    """
    Check if a session token is valid and active.
    
    🔒 SECURITY ENHANCEMENT: Also checks if the user's organization still exists
    and if the session is blacklisted.
    """
    try:
        # Check if session is blacklisted
        if is_session_blacklisted(session_token):
            return False, "Session has been invalidated"
        
        session = UserSession.query.filter(
            UserSession.session_token == session_token,
            UserSession.is_active == True
        ).first()
        
        if not session:
            return False, "Session not found or inactive"
        
        if session.is_expired():
            # Mark expired session as inactive and add to blacklist
            session.is_active = False
            
            # Add to blacklist
            from models.user import User
            user = User.query.filter(User.user_id == session.user_id).first()
            org_id = user.org_id if user else None
            
            invalidated_session = InvalidatedSession(
                session_id=session.session_id,
                user_id=session.user_id,
                org_id=org_id,
                session_token=session_token,
                reason='expired'
            )
            db.session.add(invalidated_session)
            db.session.commit()
            return False, "Session expired"
        
        # Check if user's organization still exists and is active
        from models.user import User
        from models.organisation import Organisation
        
        user = User.query.filter(User.user_id == session.user_id).first()
        if not user:
            return False, "User not found"
        
        org = Organisation.query.filter(
            Organisation.org_id == user.org_id,
            Organisation.is_active == True
        ).first()
        
        if not org:
            # Organization deleted or deactivated - invalidate session
            invalidate_session(session_token, 'org_deleted')
            return False, "Organization no longer exists"
        
        return True, "Valid session"
        
    except Exception as e:
        return False, f"Session validation error: {str(e)}"

def cleanup_expired_sessions():
    """Remove expired sessions from database (maintenance function)."""
    try:
        expired_sessions = UserSession.query.filter(
            UserSession.expires_at < datetime.utcnow()
        ).all()
        
        count = len(expired_sessions)
        for session in expired_sessions:
            db.session.delete(session)
        
        db.session.commit()
        return count
    except Exception as e:
        db.session.rollback()
        raise e