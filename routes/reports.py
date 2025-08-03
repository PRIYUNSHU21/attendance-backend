"""
📊 REPORTS ROUTES - Attendance analytics and statistics
"""

from flask import Blueprint, request, jsonify
from models.attendance import AttendanceSession, AttendanceRecord
from models.user import User
from config.db import db
from utils.auth import token_required, teacher_or_admin_required, get_current_user
from utils.response import success_response, error_response
from datetime import datetime, timedelta
from sqlalchemy import func, and_

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/session/<session_id>/detailed', methods=['GET'])
@token_required
@teacher_or_admin_required
def get_detailed_session_report(session_id):
    """Get detailed attendance report for a specific session."""
    try:
        current_user = get_current_user()
        
        # Get session
        session = AttendanceSession.query.filter_by(
            session_id=session_id,
            org_id=current_user.get('org_id')
        ).first()
        
        if not session:
            return error_response("Session not found", 404)
        
        # Get attendance records
        records = AttendanceRecord.query.filter_by(session_id=session_id).all()
        
        # Calculate statistics
        total_records = len(records)
        present_count = len([r for r in records if r.status == 'present'])
        absent_count = total_records - present_count
        
        return success_response(
            data={
                'session': session.to_dict(),
                'attendance_records': [record.to_dict() for record in records],
                'statistics': {
                    'total_records': total_records,
                    'present_count': present_count,
                    'absent_count': absent_count,
                    'attendance_rate': (present_count / total_records * 100) if total_records > 0 else 0
                }
            },
            message="Detailed session report retrieved successfully"
        )
    except Exception as e:
        return error_response(str(e), 500)

@reports_bp.route('/user/<user_id>/history', methods=['GET'])
@token_required
@teacher_or_admin_required
def get_user_attendance_history(user_id):
    """Get attendance history for a specific user."""
    try:
        current_user = get_current_user()
        
        # Get user
        user = User.query.filter_by(
            user_id=user_id,
            org_id=current_user.get('org_id')
        ).first()
        
        if not user:
            return error_response("User not found", 404)
        
        # Get attendance records
        records = AttendanceRecord.query.filter_by(
            user_id=user_id,
            org_id=current_user.get('org_id')
        ).order_by(AttendanceRecord.created_at.desc()).all()
        
        # Calculate statistics
        total_records = len(records)
        present_count = len([r for r in records if r.status == 'present'])
        
        return success_response(
            data={
                'user': user.to_dict(),
                'attendance_records': [record.to_dict() for record in records],
                'statistics': {
                    'total_sessions': total_records,
                    'present_count': present_count,
                    'absent_count': total_records - present_count,
                    'attendance_rate': (present_count / total_records * 100) if total_records > 0 else 0
                }
            },
            message="User attendance history retrieved successfully"
        )
    except Exception as e:
        return error_response(str(e), 500)

@reports_bp.route('/organization/summary', methods=['GET'])
@token_required
@teacher_or_admin_required
def get_organization_summary():
    """Get organization-wide attendance summary."""
    try:
        current_user = get_current_user()
        org_id = current_user.get('org_id')
        
        # Get date range from query params
        days = request.args.get('days', 30, type=int)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get attendance records in date range
        records = AttendanceRecord.query.filter(
            and_(
                AttendanceRecord.org_id == org_id,
                AttendanceRecord.created_at >= start_date,
                AttendanceRecord.created_at <= end_date
            )
        ).all()
        
        # Calculate statistics
        total_records = len(records)
        present_count = len([r for r in records if r.status == 'present'])
        
        # Get active sessions count
        active_sessions = AttendanceSession.query.filter_by(
            org_id=org_id,
            is_active=True
        ).count()
        
        # Get total users count
        total_users = User.query.filter_by(
            org_id=org_id,
            is_active=True
        ).count()
        
        return success_response(
            data={
                'date_range': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': days
                },
                'statistics': {
                    'total_attendance_records': total_records,
                    'present_count': present_count,
                    'absent_count': total_records - present_count,
                    'attendance_rate': (present_count / total_records * 100) if total_records > 0 else 0,
                    'active_sessions': active_sessions,
                    'total_users': total_users
                }
            },
            message="Organization summary retrieved successfully"
        )
    except Exception as e:
        return error_response(str(e), 500)
