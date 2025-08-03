"""
🚀 BULLETPROOF ATTENDANCE - Main attendance system
Simple, reliable attendance check-in based on proven patterns
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from config.db import db
from models.attendance import AttendanceSession, AttendanceRecord
from utils.auth import token_required, get_current_user
from utils.response import success_response, error_response
import uuid
from math import radians, sin, cos, sqrt, atan2

bulletproof_bp = Blueprint('bulletproof', __name__)

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance using Haversine formula - same as your friend's"""
    R = 6371000  # Earth radius in meters
    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)
    a = sin(dLat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dLon / 2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

@bulletproof_bp.route('/simple-checkin', methods=['POST'])
@token_required
def simple_checkin():
    """Main attendance check-in endpoint."""
    try:
        data = request.get_json()
        current_user = get_current_user()
        
        # Required fields - Accept both lat/lon and latitude/longitude
        session_id = data.get('session_id')
        user_lat = data.get('lat') or data.get('latitude')
        user_lon = data.get('lon') or data.get('longitude')
        
        if not session_id:
            return error_response("session_id is required", 400)
        if user_lat is None or user_lon is None:
            return error_response("User location (lat/lon or latitude/longitude) is required", 400)
        
        # Get session - minimal validation
        session = AttendanceSession.query.filter_by(session_id=session_id).first()
        if not session:
            return error_response("Session not found", 404)
        
        # Check if already checked in
        existing = AttendanceRecord.query.filter_by(
            session_id=session_id,
            user_id=current_user['user_id']
        ).first()
        
        if existing:
            return error_response("Already checked in to this session", 400)
        
        # Calculate distance (like your friend's system)
        distance = 999999  # Default to far away
        status = "Absent"
        
        if session.location_lat and session.location_lon:
            distance = calculate_distance(
                user_lat, user_lon,
                session.location_lat, session.location_lon
            )
            
            # Within radius = Present, otherwise Absent
            radius = session.location_radius or 100
            status = "Present" if distance <= radius else "Absent"
        else:
            # No location set = always present
            status = "Present"
            distance = 0
        
        # Create attendance record - DIRECT INSERT
        record = AttendanceRecord(
            record_id=str(uuid.uuid4()),
            session_id=session_id,
            user_id=current_user['user_id'],
            org_id=session.org_id,
            status=status.lower(),
            check_in_time=datetime.now(),
            check_in_lat=user_lat,
            check_in_lon=user_lon,
            location_verified=(status == "Present"),
            created_by=current_user['user_id'],
            created_at=datetime.now()
        )
        
        # DIRECT DATABASE SAVE
        db.session.add(record)
        db.session.commit()
        
        return success_response(
            data={
                'record_id': record.record_id,
                'user_id': current_user['user_id'],
                'session_id': session_id,
                'status': status,
                'distance': round(distance, 2),
                'check_in_time': record.check_in_time.isoformat(),
                'location': {
                    'lat': user_lat,
                    'lon': user_lon
                },
                'message': f"Attendance marked as {status}"
            },
            message="Attendance recorded successfully"
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f"Failed to record attendance: {str(e)}", 500)

@bulletproof_bp.route('/get-active-sessions', methods=['GET'])
@token_required
def get_active_sessions_simple():
    """Get active sessions - no complex time validation"""
    try:
        current_user = get_current_user()
        
        # Get all active sessions for organization
        sessions = AttendanceSession.query.filter_by(
            org_id=current_user['org_id'],
            is_active=True
        ).all()
        
        result = []
        for session in sessions:
            result.append({
                'session_id': session.session_id,
                'session_name': session.session_name,
                'description': session.description,
                'start_time': session.start_time.isoformat() if session.start_time else None,
                'end_time': session.end_time.isoformat() if session.end_time else None,
                'location_lat': session.location_lat,
                'location_lon': session.location_lon,
                'location_radius': session.location_radius,
                'created_by': session.created_by
            })
        
        return success_response(
            data=result,
            message=f"Found {len(result)} active sessions"
        )
        
    except Exception as e:
        return error_response(f"Failed to get sessions: {str(e)}", 500)
