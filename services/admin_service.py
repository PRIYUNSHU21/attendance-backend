# services/admin_service.py
"""
Admin Service Module
This module handles administrative operations like user management,
organization management, and system administration tasks.
"""

from datetime import datetime, timedelta
from models.user import User, create_user, find_user_by_id, update_user, delete_user, get_users_by_org
from models.organisation import Organisation, create_organisation, find_organisation_by_id, update_organisation
from models.attendance import AttendanceSession, AttendanceRecord, get_active_sessions
from services.hash_service import hash_password
from config.db import db

def get_organization_statistics(org_id):
    """
    Get comprehensive statistics for an organization.
    
    Args:
        org_id: Organization ID
        
    Returns:
        Dictionary containing organization statistics
    """
    try:
        # Get organization details
        org = find_organisation_by_id(org_id)
        if not org:
            raise Exception("Organization not found")
        
        # Get user statistics
        all_users = get_users_by_org(org_id)
        active_users = [u for u in all_users if u.is_active]
        students = [u for u in active_users if u.role == 'student']
        teachers = [u for u in active_users if u.role == 'teacher']
        admins = [u for u in active_users if u.role == 'admin']
        
        # Get session statistics
        all_sessions = get_active_sessions(org_id)
        current_time = datetime.now()
        
        ongoing_sessions = []
        upcoming_sessions = []
        past_sessions = []
        
        for session in all_sessions:
            if session.start_time <= current_time <= session.end_time:
                ongoing_sessions.append(session)
            elif session.start_time > current_time:
                upcoming_sessions.append(session)
            else:
                past_sessions.append(session)
        
        # Get attendance statistics for the last 30 days
        thirty_days_ago = current_time - timedelta(days=30)
        recent_sessions = [s for s in all_sessions if s.start_time >= thirty_days_ago]
        
        total_attendance_records = 0
        present_count = 0
        late_count = 0
        
        for session in recent_sessions:
            records = AttendanceRecord.query.filter_by(session_id=session.session_id).all()
            total_attendance_records += len(records)
            present_count += len([r for r in records if r.status == 'present'])
            late_count += len([r for r in records if r.status == 'late'])
        
        attendance_rate = 0
        if total_attendance_records > 0:
            attendance_rate = ((present_count + late_count) / total_attendance_records) * 100
        
        return {
            'organization': org.to_dict(),
            'users': {
                'total': len(all_users),
                'active': len(active_users),
                'students': len(students),
                'teachers': len(teachers),
                'admins': len(admins)
            },
            'sessions': {
                'total': len(all_sessions),
                'ongoing': len(ongoing_sessions),
                'upcoming': len(upcoming_sessions),
                'past': len(past_sessions)
            },
            'attendance_last_30_days': {
                'total_records': total_attendance_records,
                'present_count': present_count,
                'late_count': late_count,
                'attendance_rate': round(attendance_rate, 2)
            }
        }
    except Exception as e:
        raise e

def bulk_create_users(users_data, org_id, created_by_user_id):
    """
    Create multiple users in bulk.
    
    Args:
        users_data: List of user data dictionaries
        org_id: Organization ID
        created_by_user_id: ID of the user creating these accounts
        
    Returns:
        Dictionary with creation results
    """
    try:
        created_users = []
        errors = []
        
        for i, user_data in enumerate(users_data):
            try:
                # Set organization ID
                user_data['org_id'] = org_id
                
                # Hash password if provided
                if 'password' in user_data:
                    user_data['password_hash'] = hash_password(user_data['password'])
                    del user_data['password']
                elif 'password_hash' not in user_data:
                    # Generate a default password if none provided
                    default_password = f"temp{datetime.now().strftime('%Y%m%d')}"
                    user_data['password_hash'] = hash_password(default_password)
                
                user = create_user(user_data)
                created_users.append(user.to_dict())
            except Exception as e:
                errors.append({
                    'index': i,
                    'data': user_data,
                    'error': str(e)
                })
        
        return {
            'created_count': len(created_users),
            'error_count': len(errors),
            'created_users': created_users,
            'errors': errors
        }
    except Exception as e:
        raise e

def deactivate_inactive_users(org_id, inactive_days=90):
    """
    Deactivate users who haven't been active for a specified number of days.
    
    Args:
        org_id: Organization ID
        inactive_days: Number of days to consider a user inactive
        
    Returns:
        List of deactivated users
    """
    try:
        cutoff_date = datetime.now() - timedelta(days=inactive_days)
        
        # Get all users from the organization
        users = get_users_by_org(org_id)
        deactivated_users = []
        
        for user in users:
            if not user.is_active:
                continue
            
            # Check if user has any recent attendance records
            recent_attendance = AttendanceRecord.query.filter(
                AttendanceRecord.user_id == user.user_id,
                AttendanceRecord.check_in_time >= cutoff_date
            ).first()
            
            if not recent_attendance and user.role == 'student':
                # Deactivate the user
                updated_user = update_user(user.user_id, {'is_active': False})
                if updated_user:
                    deactivated_users.append(updated_user.to_dict())
        
        return deactivated_users
    except Exception as e:
        raise e

def generate_organization_report(org_id, start_date=None, end_date=None):
    """
    Generate a comprehensive organization report.
    
    Args:
        org_id: Organization ID
        start_date: Start date for the report
        end_date: End date for the report
        
    Returns:
        Dictionary containing comprehensive report data
    """
    try:
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Get organization details
        org = find_organisation_by_id(org_id)
        if not org:
            raise Exception("Organization not found")
        
        # Get sessions in date range
        sessions = AttendanceSession.query.filter(
            AttendanceSession.org_id == org_id,
            AttendanceSession.start_time >= start_date,
            AttendanceSession.start_time <= end_date,
            AttendanceSession.is_active == True
        ).all()
        
        # Get attendance data for these sessions
        session_ids = [s.session_id for s in sessions]
        attendance_records = []
        
        if session_ids:
            attendance_records = AttendanceRecord.query.filter(
                AttendanceRecord.session_id.in_(session_ids)
            ).all()
        
        # Calculate statistics
        total_sessions = len(sessions)
        total_attendance = len(attendance_records)
        present_count = len([r for r in attendance_records if r.status == 'present'])
        late_count = len([r for r in attendance_records if r.status == 'late'])
        
        # Get user statistics
        all_users = get_users_by_org(org_id)
        active_students = [u for u in all_users if u.is_active and u.role == 'student']
        
        # Calculate average attendance rate
        if total_attendance > 0:
            attendance_rate = ((present_count + late_count) / total_attendance) * 100
        else:
            attendance_rate = 0
        
        # Get most active students
        student_attendance = {}
        for record in attendance_records:
            user_id = record.user_id
            if user_id not in student_attendance:
                student_attendance[user_id] = {'present': 0, 'late': 0, 'total': 0}
            
            student_attendance[user_id]['total'] += 1
            if record.status == 'present':
                student_attendance[user_id]['present'] += 1
            elif record.status == 'late':
                student_attendance[user_id]['late'] += 1
        
        # Sort students by attendance rate
        sorted_students = []
        for user_id, stats in student_attendance.items():
            user = find_user_by_id(user_id)
            if user and user.role == 'student':
                rate = ((stats['present'] + stats['late']) / stats['total']) * 100 if stats['total'] > 0 else 0
                sorted_students.append({
                    'user': user.to_dict(),
                    'attendance_stats': stats,
                    'attendance_rate': round(rate, 2)
                })
        
        sorted_students.sort(key=lambda x: x['attendance_rate'], reverse=True)
        
        return {
            'organization': org.to_dict(),
            'report_period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'summary': {
                'total_sessions': total_sessions,
                'total_attendance_records': total_attendance,
                'present_count': present_count,
                'late_count': late_count,
                'overall_attendance_rate': round(attendance_rate, 2),
                'total_students': len(active_students)
            },
            'sessions': [session.to_dict() for session in sessions],
            'top_students': sorted_students[:10],  # Top 10 students
            'attendance_records': [record.to_dict() for record in attendance_records]
        }
    except Exception as e:
        raise e

def cleanup_old_sessions(org_id, days_old=365):
    """
    Mark old sessions as inactive for cleanup.
    
    Args:
        org_id: Organization ID
        days_old: Number of days old to consider for cleanup
        
    Returns:
        Number of sessions cleaned up
    """
    try:
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        # Find old sessions
        old_sessions = AttendanceSession.query.filter(
            AttendanceSession.org_id == org_id,
            AttendanceSession.end_time < cutoff_date,
            AttendanceSession.is_active == True
        ).all()
        
        cleaned_count = 0
        for session in old_sessions:
            session.is_active = False
            cleaned_count += 1
        
        db.session.commit()
        return cleaned_count
    except Exception as e:
        db.session.rollback()
        raise e