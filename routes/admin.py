"""
👑 ADMINISTRATIVE ROUTES - Admin management endpoints
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from config.db import db
from models.user import User
from models.organisation import Organisation  
from models.attendance import AttendanceSession, AttendanceRecord
from utils.auth import token_required, admin_required, teacher_or_admin_required, get_current_user
from utils.response import success_response, error_response
from services.hash_service import hash_password
import uuid
from sqlalchemy import text

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/users', methods=['GET'])
@token_required
@teacher_or_admin_required
def get_users():
    """Get all users in the organization with pagination."""
    try:
        current_user = get_current_user()
        org_id = current_user.get('org_id')
        
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        role = request.args.get('role')
        
        query = User.query.filter_by(org_id=org_id, is_active=True)
        if role:
            query = query.filter_by(role=role)
            
        result = query.paginate(page=page, per_page=per_page)
        
        return success_response(
            data={
                'users': [user.to_dict() for user in result.items],
                'pagination': {
                    'page': result.page,
                    'per_page': result.per_page,
                    'total': result.total,
                    'pages': result.pages
                }
            },
            message="Users retrieved successfully"
        )
    except Exception as e:
        return error_response(str(e), 500)

@admin_bp.route('/users', methods=['POST'])
@token_required
@admin_required
def create_new_user():
    """Create a new user."""
    try:
        data = request.get_json()
        if not data:
            return error_response("No data provided", 400)
        
        current_user = get_current_user()
        
        required_fields = ['name', 'email', 'password', 'role']
        for field in required_fields:
            if field not in data:
                return error_response(f"Missing required field: {field}", 400)
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return error_response("Email already exists", 400)
        
        user = User(
            name=data['name'],
            email=data['email'],
            password_hash=hash_password(data['password']),
            role=data['role'],
            org_id=current_user.get('org_id')
        )
        
        db.session.add(user)
        db.session.commit()
        
        return success_response(
            data=user.to_dict(),
            message="User created successfully",
            status_code=201
        )
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 400)

@admin_bp.route('/sessions', methods=['POST'])
@token_required
@teacher_or_admin_required
def create_attendance_session():
    """Create a new attendance session."""
    try:
        data = request.get_json()
        if not data:
            return error_response("No data provided", 400)
        
        current_user = get_current_user()
        
        session = AttendanceSession(
            session_id=str(uuid.uuid4()),
            session_name=data['session_name'],
            description=data.get('description', ''),
            org_id=current_user.get('org_id'),
            created_by=current_user['user_id'],
            start_time=datetime.fromisoformat(data['start_time']),
            end_time=datetime.fromisoformat(data['end_time']),
            location_lat=data.get('latitude'),
            location_lon=data.get('longitude'),
            location_radius=data.get('radius', 100),
            is_active=True
        )
        
        db.session.add(session)
        db.session.commit()
        
        return success_response(
            data=session.to_dict(),
            message="Attendance session created successfully",
            status_code=201
        )
    except Exception as e:
        db.session.rollback()
        return error_response(str(e), 400)

@admin_bp.route('/sessions', methods=['GET'])
@token_required
@teacher_or_admin_required
def get_sessions():
    """Get all sessions for the organization."""
    try:
        current_user = get_current_user()
        org_id = current_user.get('org_id')
        
        sessions = AttendanceSession.query.filter_by(
            org_id=org_id,
            is_active=True
        ).order_by(AttendanceSession.created_at.desc()).all()
        
        return success_response(
            data=[session.to_dict() for session in sessions],
            message="Sessions retrieved successfully"
        )
    except Exception as e:
        return error_response(str(e), 500)

@admin_bp.route('/dashboard/stats', methods=['GET'])
@token_required
@teacher_or_admin_required
def get_dashboard_stats():
    """Get dashboard statistics."""
    try:
        current_user = get_current_user()
        org_id = current_user.get('org_id')
        
        total_users = User.query.filter_by(org_id=org_id, is_active=True).count()
        total_students = User.query.filter_by(org_id=org_id, role='student', is_active=True).count()
        total_teachers = User.query.filter_by(org_id=org_id, role='teacher', is_active=True).count()
        active_sessions = AttendanceSession.query.filter_by(org_id=org_id, is_active=True).count()
        
        # Recent attendance (last 7 days)
        from datetime import datetime, timedelta
        week_ago = datetime.now() - timedelta(days=7)
        recent_attendance = AttendanceRecord.query.filter(
            AttendanceRecord.created_at >= week_ago,
            AttendanceRecord.org_id == org_id
        ).count()
        
        return success_response(
            data={
                'total_users': total_users,
                'total_students': total_students,
                'total_teachers': total_teachers,
                'active_sessions': active_sessions,
                'recent_attendance': recent_attendance,
                'organization_id': org_id
            },
            message="Dashboard statistics retrieved successfully"
        )
    except Exception as e:
        return error_response(str(e), 500)
