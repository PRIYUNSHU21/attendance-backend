"""
🔑 AUTHENTICATION ROUTES - User login, registration, profile management
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from config.db import db
from models.user import User
from models.organisation import Organisation
from models.session import UserSession
from utils.auth import token_required, get_current_user, generate_token
from utils.response import success_response, error_response
from services.hash_service import hash_password, verify_password
import uuid
import secrets

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint."""
    try:
        data = request.get_json()
        if not data:
            return error_response("No data provided", 400)
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return error_response("Email and password are required", 400)
        
        # Find user
        user = User.query.filter_by(email=email, is_active=True).first()
        if not user or not verify_password(password, user.password_hash):
            return error_response("Invalid email or password", 401)
        
        # Create session
        session = UserSession(
            session_id=str(uuid.uuid4()),
            user_id=user.user_id,
            session_token=secrets.token_urlsafe(32),
            device_info=data.get('device_info', 'Unknown'),
            ip_address=request.remote_addr,
            is_active=True
        )
        
        db.session.add(session)
        db.session.commit()
        
        # Generate JWT token
        token = generate_token(
            {
                'user_id': user.user_id,
                'org_id': user.org_id,
                'role': user.role,
                'session_id': session.session_id,
                'session_token': session.session_token
            }
        )
        
        return success_response(
            data={
                'user': user.to_dict(),
                'token': token,
                'session_id': session.session_id,
                'session_token': session.session_token
            },
            message="Login successful"
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)

@auth_bp.route('/register', methods=['POST'])
def register():
    """User registration endpoint."""
    try:
        data = request.get_json()
        if not data:
            return error_response("No data provided", 400)
        
        required_fields = ['name', 'email', 'password', 'role', 'org_id']
        for field in required_fields:
            if field not in data:
                return error_response(f"Missing required field: {field}", 400)
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return error_response("Email already exists", 400)
        
        # Check if organization exists
        org = Organisation.query.filter_by(org_id=data['org_id'], is_active=True).first()
        if not org:
            return error_response("Organization not found", 404)
        
        # Create user
        user = User(
            name=data['name'],
            email=data['email'],
            password_hash=hash_password(data['password']),
            role=data['role'],
            org_id=data['org_id']
        )
        
        db.session.add(user)
        db.session.commit()
        
        return success_response(
            data=user.to_dict(),
            message="Registration successful",
            status_code=201
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """User logout endpoint."""
    try:
        current_user = get_current_user()
        session_token = request.get_json().get('session_token') if request.get_json() else None
        
        # Deactivate session
        if session_token:
            session = UserSession.query.filter_by(
                user_id=current_user['user_id'],
                session_token=session_token,
                is_active=True
            ).first()
            
            if session:
                session.is_active = False
                session.logout_time = datetime.utcnow()
                db.session.commit()
        
        return success_response(
            message="Logout successful"
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile():
    """Get current user profile."""
    try:
        current_user = get_current_user()
        user = User.query.filter_by(user_id=current_user['user_id']).first()
        
        if not user:
            return error_response("User not found", 404)
            
        return success_response(
            data=user.to_dict(),
            message="Profile retrieved successfully"
        )
    except Exception as e:
        return error_response(str(e), 500)

@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password():
    """Change user password."""
    try:
        data = request.get_json()
        if not data:
            return error_response("No data provided", 400)
        
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if not old_password or not new_password:
            return error_response("Both old and new passwords are required", 400)
        
        current_user = get_current_user()
        user = User.query.filter_by(user_id=current_user['user_id']).first()
        
        if not user:
            return error_response("User not found", 404)
        
        # Verify old password
        if not verify_password(old_password, user.password_hash):
            return error_response("Current password is incorrect", 400)
        
        # Update password
        user.password_hash = hash_password(new_password)
        user.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return success_response(
            message="Password changed successfully"
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 500)

@auth_bp.route('/verify', methods=['GET'])
@token_required
def verify_token():
    """Verify JWT token validity."""
    try:
        current_user = get_current_user()
        return success_response(
            data={'user': current_user},
            message="Token is valid"
        )
    except Exception as e:
        return error_response(str(e), 401)

@auth_bp.route('/public/organizations', methods=['GET'])
def get_organizations():
    """Get list of all organizations for registration."""
    try:
        organizations = Organisation.query.filter_by(is_active=True).all()
        return success_response(
            data=[org.to_dict() for org in organizations],
            message="Organizations retrieved successfully"
        )
    except Exception as e:
        return error_response(str(e), 500)
