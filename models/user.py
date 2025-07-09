"""
👤 USER MODEL - models/user.py

🎯 WHAT THIS FILE DOES:
This file defines the User data structure and provides functions to manage users.
Think of it as the "user database table" plus helpful functions to work with users.

🔧 FOR FRONTEND DEVELOPERS:
- This defines what user data looks like in API responses
- All user-related API calls use these functions behind the scenes
- Understanding this helps you know what user data is available
- User authentication and profile features are built on this model

📋 USER DATA STRUCTURE (API Response Format):
{
  "user_id": "unique-uuid-string",
  "name": "John Doe",
  "email": "john.doe@example.com", 
  "role": "student|teacher|admin",
  "org_id": "organization-uuid",
  "created_at": "2025-07-05T10:30:00Z",
  "updated_at": "2025-07-05T10:30:00Z",
  "is_active": true
}

🔒 SECURITY NOTES:
- password_hash is NEVER returned in API responses
- Only admins can see users from other organizations
- Users can only see/edit their own profile (unless admin)
- Email addresses must be unique across the entire system

🌐 AVAILABLE FUNCTIONS FOR FRONTEND:
- create_user(): Register new users
- find_user_by_email(): Login authentication 
- find_user_by_id(): Get user profile
- update_user(): Edit user profile
- delete_user(): Deactivate user account
- get_users_by_org(): List users in organization
- get_users_by_role(): Filter users by role

⚡ FRONTEND INTEGRATION EXAMPLES:
- Registration: POST /auth/register uses create_user()
- Login: POST /auth/login uses find_user_by_email()
- Profile: GET /auth/profile uses find_user_by_id()
- User List: GET /admin/users uses get_users_by_org()

🔄 USER ROLES EXPLAINED:
- "student": Can only check in/out and view own attendance
- "teacher": Can manage sessions and view student attendance
- "admin": Full system access, user management, reports

📱 EXAMPLE FRONTEND USAGE:
// Login response includes user data
{
  "success": true,
  "data": {
    "token": "jwt-token-here",
    "user": { ...user object... }
  }
}
"""

import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from config.db import db

class User(db.Model):
    """User model for storing user information."""
    __tablename__ = 'users'
    
    user_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # 'admin', 'teacher', 'student'
    org_id = db.Column(db.String(36), db.ForeignKey('organisations.org_id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def to_dict(self):
        """Convert user object to dictionary."""
        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'org_id': self.org_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active
        }

def find_user_by_email(email):
    """Find a user by their email."""
    return User.query.filter_by(email=email, is_active=True).first()

def find_user_by_id(user_id):
    """Find a user by their user_id."""
    return User.query.filter_by(user_id=user_id, is_active=True).first()

def create_user(data):
    """Create a new user."""
    try:
        user = User(
            name=data["name"],
            email=data["email"],
            password_hash=data["password_hash"],
            role=data.get("role", "student"),
            org_id=data["org_id"]
        )
        db.session.add(user)
        db.session.commit()
        return user
    except Exception as e:
        db.session.rollback()
        raise e

def update_user(user_id, data):
    """Update an existing user."""
    try:
        user = find_user_by_id(user_id)
        if not user:
            return None
        
        for key, value in data.items():
            if hasattr(user, key) and key != 'user_id':
                setattr(user, key, value)
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        return user
    except Exception as e:
        db.session.rollback()
        raise e

def delete_user(user_id):
    """Soft delete a user (set is_active to False)."""
    try:
        user = find_user_by_id(user_id)
        if not user:
            return None
        
        user.is_active = False
        user.updated_at = datetime.utcnow()
        db.session.commit()
        return user
    except Exception as e:
        db.session.rollback()
        raise e

def get_users_by_org(org_id):
    """Get all active users in an organization."""
    return User.query.filter_by(org_id=org_id, is_active=True).all()

def get_users_by_role(role, org_id=None):
    """Get all active users with a specific role, optionally filtered by organization."""
    query = User.query.filter_by(role=role, is_active=True)
    if org_id:
        query = query.filter_by(org_id=org_id)
    return query.all()