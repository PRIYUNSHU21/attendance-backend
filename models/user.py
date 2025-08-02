"""
👤 USER MODEL - models/user.py

🎯 WHAT THIS FILE DOES:
This file defines the User model for the database.
Users are individuals who access the system with different roles.

🔧 DATABASE STRUCTURE:
- user_id: Primary key (UUID)
- name: User's full name
- email: User's email address (unique)
- password_hash: Securely stored password hash
- role: User's role (student, teacher, admin)
- org_id: Organization the user belongs to

📋 AVAILABLE METHODS:
- to_dict(): Convert user to dictionary for API responses
- find_by_email(): Find user by email address
- find_by_id(): Find user by ID
- get_users_by_org(): Get all users in an organization
"""

import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from config.db import db

class User(db.Model):
    """Model for users in the system."""
    __tablename__ = 'users'
    
    user_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # student, teacher, admin
    org_id = db.Column(db.String(36), db.ForeignKey('organisations.org_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    organization = db.relationship('Organisation', backref=db.backref('users', lazy=True))
    attendance_records = db.relationship('AttendanceRecord', foreign_keys='AttendanceRecord.user_id', backref='user', lazy=True, cascade="all, delete-orphan")
    sessions = db.relationship('UserSession', backref='user', lazy=True, cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert user object to dictionary."""
        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'org_id': self.org_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    @staticmethod
    def find_by_email(email):
        """Find a user by their email."""
        return User.query.filter_by(email=email, is_active=True).first()

    @staticmethod
    def find_by_id(user_id):
        """Find a user by their ID."""
        return User.query.filter_by(user_id=user_id, is_active=True).first()

    @staticmethod
    def get_users_by_org(org_id, role=None, page=1, per_page=20):
        """Get all users in an organization."""
        query = User.query.filter_by(org_id=org_id, is_active=True)
        
        if role:
            query = query.filter_by(role=role)
            
        return query.paginate(page=page, per_page=per_page)

# Additional helper functions for backward compatibility
def create_user(data):
    """Create a new user (compatibility function)."""
    user = User(
        name=data["name"],
        email=data["email"],
        password_hash=data["password_hash"],
        role=data["role"],
        org_id=data["org_id"]
    )
    
    db.session.add(user)
    db.session.commit()
    return user

def find_user_by_id(user_id):
    """Find a user by their ID (compatibility function)."""
    return User.find_by_id(user_id)

def update_user(user_id, data):
    """Update a user (compatibility function)."""
    user = User.find_by_id(user_id)
    if not user:
        return None
    
    for key, value in data.items():
        if hasattr(user, key) and key != 'user_id':
            setattr(user, key, value)
    
    db.session.commit()
    return user

def delete_user(user_id):
    """Soft delete a user (compatibility function)."""
    user = User.find_by_id(user_id)
    if not user:
        return None
    
    user.is_active = False
    db.session.commit()
    return user

def get_users_by_org(org_id, page=1, per_page=20):
    """Get all users in an organization (compatibility function)."""
    result = User.get_users_by_org(org_id, page=page, per_page=per_page)
    return result.items

def get_users_by_role(role, org_id=None, page=1, per_page=20):
    """Get users by role (compatibility function)."""
    query = User.query.filter_by(role=role, is_active=True)
    
    if org_id:
        query = query.filter_by(org_id=org_id)
    
    result = query.paginate(page=page, per_page=per_page)
    return result.items