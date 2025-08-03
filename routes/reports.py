# routes/reports.py
"""
Reports routes for attendance analytics, statistics, and data export.
"""

from flask import Blueprint, request, jsonify
from services.attendance_service import get_session_report, get_user_attendance_history
from models.attendance import get_session_attendance, get_user_attendance, AttendanceSession, AttendanceRecord
from models.user import get_users_by_org, find_user_by_id
from utils.auth import token_required, teacher_or_admin_required, get_current_user
from utils.response import success_response, error_response, paginated_response
from utils.validators import validate_pagination_params
from datetime import datetime, timedelta
from sqlalchemy import func, and_

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/session/<session_id>/detailed', methods=['GET'])
@teacher_or_admin_required
def get_detailed_session_report(session_id):
    """Get detailed attendance report for a specific session."""
    try:
        report = get_session_report(session_id)
        return success_response(
            data=report,
            message="Detailed session report retrieved successfully"
        )
    except Exception as e:
        return error_response(str(e), 500)

@reports_bp.route('/organization/summary', methods=['GET'])
@teacher_or_admin_required
def get_organization_summary():
    """Get organization-wide attendance summary."""
    try:
        current_user = get_current_user()
        org_id = current_user.get('org_id')
        
        # Get date range from query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Default to last 30 days if no dates provided
        if not end_date:
            end_date = datetime.now()
        else:
            end_date = datetime.fromisoformat(end_date)
            
        if not start_date:
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.fromisoformat(start_date)
        
        from models import db
        
        # Get session statistics
        sessions_query = db.session.query(AttendanceSession).filter(
            and_(
                AttendanceSession.org_id == org_id,
                AttendanceSession.start_time >= start_date,
                AttendanceSession.start_time <= end_date,
                AttendanceSession.is_active == True
            )
        )
        
        total_sessions = sessions_query.count()
        sessions = sessions_query.all()
        
        # Get attendance statistics
        session_ids = [s.session_id for s in sessions]
        if session_ids:
            attendance_query = db.session.query(AttendanceRecord).filter(
                AttendanceRecord.session_id.in_(session_ids)
            )
            
            total_attendance_records = attendance_query.count()
            present_count = attendance_query.filter(AttendanceRecord.status == 'present').count()
            late_count = attendance_query.filter(AttendanceRecord.status == 'late').count()
            
            # Calculate attendance rate
            if total_attendance_records > 0:
                attendance_rate = ((present_count + late_count) / total_attendance_records) * 100
            else:
                attendance_rate = 0
        else:
            total_attendance_records = 0
            present_count = 0
            late_count = 0
            attendance_rate = 0
        
        # Get user statistics
        all_users = get_users_by_org(org_id)
        active_users = [u for u in all_users if u.is_active]
        
        summary = {
            'date_range': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'sessions': {
                'total_sessions': total_sessions,
                'active_sessions': len([s for s in sessions if s.is_active])
            },
            'attendance': {
                'total_records': total_attendance_records,
                'present_count': present_count,
                'late_count': late_count,
                'attendance_rate': round(attendance_rate, 2)
            },
            'users': {
                'total_users': len(all_users),
                'active_users': len(active_users)
            }
        }
        
        return success_response(
            data=summary,
            message="Organization summary retrieved successfully"
        )
    except Exception as e:
        return error_response(str(e), 500)

@reports_bp.route('/user/<user_id>/detailed', methods=['GET'])
@teacher_or_admin_required
def get_detailed_user_report(user_id):
    """Get detailed attendance report for a specific user."""
    try:
        current_user = get_current_user()
        
        # Check if user exists and belongs to same organization
        user = find_user_by_id(user_id)
        if not user:
            return error_response("User not found", 404)
        
        if current_user.get('org_id') != user.org_id and current_user.get('role') != 'admin':
            return error_response("Access denied", 403)
        
        # Get date range from query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Default to last 30 days if no dates provided
        if not end_date:
            end_date = datetime.now()
        else:
            end_date = datetime.fromisoformat(end_date)
            
        if not start_date:
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.fromisoformat(start_date)
        
        from models import db
        
        # Get user's attendance records in date range
        attendance_query = db.session.query(AttendanceRecord).join(AttendanceSession).filter(
            and_(
                AttendanceRecord.user_id == user_id,
                AttendanceSession.start_time >= start_date,
                AttendanceSession.start_time <= end_date
            )
        )
        
        attendance_records = attendance_query.all()
        
        # Calculate statistics
        total_records = len(attendance_records)
        present_count = len([r for r in attendance_records if r.status == 'present'])
        late_count = len([r for r in attendance_records if r.status == 'late'])
        
        if total_records > 0:
            attendance_rate = ((present_count + late_count) / total_records) * 100
        else:
            attendance_rate = 0
        
        # Get sessions user should have attended
        sessions_in_range = db.session.query(AttendanceSession).filter(
            and_(
                AttendanceSession.org_id == user.org_id,
                AttendanceSession.start_time >= start_date,
                AttendanceSession.start_time <= end_date,
                AttendanceSession.is_active == True
            )
        ).count()
        
        report = {
            'user': user.to_dict(),
            'date_range': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'statistics': {
                'total_sessions_available': sessions_in_range,
                'total_attended': total_records,
                'present_count': present_count,
                'late_count': late_count,
                'missed_sessions': max(0, sessions_in_range - total_records),
                'attendance_rate': round(attendance_rate, 2)
            },
            'attendance_records': [record.to_dict() for record in attendance_records]
        }
        
        return success_response(
            data=report,
            message="Detailed user report retrieved successfully"
        )
    except Exception as e:
        return error_response(str(e), 500)

@reports_bp.route('/attendance/trends', methods=['GET'])
@teacher_or_admin_required
def get_attendance_trends():
    """Get attendance trends over time."""
    try:
        current_user = get_current_user()
        org_id = current_user.get('org_id')
        
        # Get date range (default to last 30 days)
        days = request.args.get('days', 30, type=int)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        from models import db
        
        # Get daily attendance statistics
        daily_stats = []
        current_date = start_date
        
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            
            # Get sessions for this day
            sessions_query = db.session.query(AttendanceSession).filter(
                and_(
                    AttendanceSession.org_id == org_id,
                    AttendanceSession.start_time >= current_date,
                    AttendanceSession.start_time < next_date,
                    AttendanceSession.is_active == True
                )
            )
            
            daily_sessions = sessions_query.all()
            session_ids = [s.session_id for s in daily_sessions]
            
            if session_ids:
                # Get attendance for these sessions
                attendance_query = db.session.query(AttendanceRecord).filter(
                    AttendanceRecord.session_id.in_(session_ids)
                )
                
                total_attendance = attendance_query.count()
                present_count = attendance_query.filter(AttendanceRecord.status == 'present').count()
                late_count = attendance_query.filter(AttendanceRecord.status == 'late').count()
                
                attendance_rate = ((present_count + late_count) / total_attendance * 100) if total_attendance > 0 else 0
            else:
                total_attendance = 0
                present_count = 0
                late_count = 0
                attendance_rate = 0
            
            daily_stats.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'sessions_count': len(daily_sessions),
                'total_attendance': total_attendance,
                'present_count': present_count,
                'late_count': late_count,
                'attendance_rate': round(attendance_rate, 2)
            })
            
            current_date = next_date
        
        return success_response(
            data={
                'date_range': {
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d'),
                    'days': days
                },
                'daily_trends': daily_stats
            },
            message="Attendance trends retrieved successfully"
        )
    except Exception as e:
        return error_response(str(e), 500)

@reports_bp.route('/export/csv', methods=['GET'])
@teacher_or_admin_required
def export_attendance_csv():
    """Export attendance data as CSV."""
    try:
        current_user = get_current_user()
        org_id = current_user.get('org_id')
        
        # Get query parameters
        session_id = request.args.get('session_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        from models import db
        import csv
        from io import StringIO
        
        # Build query
        query = db.session.query(AttendanceRecord).join(AttendanceSession)
        
        if session_id:
            query = query.filter(AttendanceRecord.session_id == session_id)
        else:
            query = query.filter(AttendanceSession.org_id == org_id)
        
        if start_date:
            start_date = datetime.fromisoformat(start_date)
            query = query.filter(AttendanceSession.start_time >= start_date)
        
        if end_date:
            end_date = datetime.fromisoformat(end_date)
            query = query.filter(AttendanceSession.start_time <= end_date)
        
        records = query.all()
        
        # Create CSV content
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Record ID', 'User ID', 'Session ID', 'Session Name',
            'Check In Time', 'Check Out Time', 'Status',
            'Check In Lat', 'Check In Lon', 'Check Out Lat', 'Check Out Lon'
        ])
        
        # Write data
        for record in records:
            writer.writerow([
                record.record_id,
                record.user_id,
                record.session_id,
                getattr(record.session, 'session_name', 'N/A'),
                record.check_in_time.isoformat() if record.check_in_time else '',
                record.check_out_time.isoformat() if record.check_out_time else '',
                record.status,
                record.check_in_lat or '',
                record.check_in_lon or '',
                record.check_out_lat or '',
                record.check_out_lon or ''
            ])
        
        csv_content = output.getvalue()
        output.close()
        
        return success_response(
            data={
                'csv_content': csv_content,
                'filename': f'attendance_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                'record_count': len(records)
            },
            message="CSV export generated successfully"
        )
    except Exception as e:
        return error_response(str(e), 500)