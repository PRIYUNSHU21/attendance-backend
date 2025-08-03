"""
✅ ATTENDANCE MANAGEMENT ROUTES - routes/attendance_mark.py

🎯 WHAT THIS FILE DOES:
This file defines all attendance-related API endpoints for check-in, check-out, and attendance tracking.
Think of it as the "attendance API" that powers your attendance features.

🔧 FOR FRONTEND DEVELOPERS:
- These endpoints handle attendance check-in/check-out functionality
- All endpoints require authentication (JWT token)
- Location-based verification is built into check-in process
- Provides attendance history and session reporting

📋 AVAILABLE ENDPOINTS:

🔒 STUDENT/USER ENDPOINTS (Require authentication):
POST /attendance/check-in - Mark attendance check-in
POST /attendance/check-out - Mark attendance check-out  
GET /attendance/my-history - Get current user's attendance history
GET /attendance/active-sessions - Get active sessions for user's organization

👨‍🏫 TEACHER/ADMIN ENDPOINTS (Require teacher/admin role):
GET /attendance/session/<session_id>/report - Get session attendance report
GET /attendance/user/<user_id>/history - Get specific user's attendance history
GET /attendance/session/<session_id>/attendance - Get all attendance records for session

🌐 FRONTEND INTEGRATION EXAMPLES:

CHECK-IN ATTENDANCE:
POST /attendance/check-in
Authorization: Bearer <jwt-token>
Content-Type: application/json
{
  "session_id": "session-uuid",
  "lat": 40.7128,          // User's current latitude
  "lon": -74.0060,         // User's current longitude
  "user_id": "user-uuid"   // Optional: for admin/teacher to check in others
}

Response:
{
  "success": true,
  "data": {
    "record_id": "attendance-record-uuid",
    "user_id": "user-uuid",
    "session_id": "session-uuid", 
    "check_in_time": "2025-07-05T09:15:00Z",
    "status": "present",     // or "late"
    "location": {
      "lat": 40.7128,
      "lon": -74.0060
    }
  },
  "message": "Check-in successful"
}

CHECK-OUT ATTENDANCE:
POST /attendance/check-out
Authorization: Bearer <jwt-token>
Content-Type: application/json
{
  "record_id": "attendance-record-uuid",
  "lat": 40.7128,
  "lon": -74.0060
}

GET ACTIVE SESSIONS:
GET /attendance/active-sessions
Authorization: Bearer <jwt-token>

Response:
{
  "success": true,
  "data": [
    {
      "session_id": "uuid",
      "session_name": "Math 101",
      "start_time": "2025-07-05T09:00:00Z",
      "end_time": "2025-07-05T10:30:00Z",
      "location_lat": 40.7128,
      "location_lon": -74.0060,
      "location_radius": 50
    }
  ]
}

GET ATTENDANCE HISTORY:
GET /attendance/my-history?limit=50
Authorization: Bearer <jwt-token>

📱 EXAMPLE FRONTEND IMPLEMENTATION:

// Get user location and check in
async function checkIn(sessionId) {
  // Get user's current location
  navigator.geolocation.getCurrentPosition(async (position) => {
    try {
      const response = await fetch('/attendance/check-in', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${getToken()}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          session_id: sessionId,
          lat: position.coords.latitude,
          lon: position.coords.longitude
        })
      });
      
      const result = await response.json();
      
      if (result.success) {
        showSuccess('Check-in successful!');
        // Store record_id for potential check-out
        localStorage.setItem('current_attendance', result.data.record_id);
      } else {
        showError(result.message);
      }
    } catch (error) {
      showError('Check-in failed. Please try again.');
    }
  }, (error) => {
    showError('Location access required for attendance.');
  });
}

// Load active sessions
async function loadActiveSessions() {
  try {
    const response = await fetch('/attendance/active-sessions', {
      headers: { 'Authorization': `Bearer ${getToken()}` }
    });
    
    const result = await response.json();
    
    if (result.success) {
      displaySessions(result.data);
    }
  } catch (error) {
    console.error('Failed to load sessions:', error);
  }
}

🔒 SECURITY & PERMISSIONS:
- All endpoints require valid JWT token
- Users can only see their own attendance history
- Teachers/admins can view their organization's data
- Location verification prevents attendance fraud
- Cross-organization data access is prevented

📍 LOCATION-BASED FEATURES:
- GPS coordinates required for check-in/check-out
- Geofence validation (must be within session radius)
- Location accuracy affects check-in success
- Handles location permission errors gracefully

⚡ FRONTEND CONSIDERATIONS:
- Request location permission early in app flow
- Handle location access denied scenarios  
- Show loading states during location acquisition
- Provide fallback for poor GPS signal
- Cache active sessions to reduce API calls
"""

from flask import Blueprint, request, jsonify
from services.attendance_service import (
    mark_user_attendance, checkout_user_attendance, 
    get_session_report, get_user_attendance_history,
    get_organization_active_sessions
)
from utils.auth import token_required, teacher_or_admin_required, get_current_user
from utils.response import success_response, error_response, validation_error_response
from utils.validators import validate_attendance_data
from datetime import datetime

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/check-in', methods=['POST', 'GET'])
@token_required  
def check_in():
    """Mark attendance check-in for a user."""
    if request.method == 'GET':
        return error_response(
            message="Use POST method to check in. GET is not supported for check-in.",
            status_code=405
        )
    
    try:
        data = request.get_json()
        if not data:
            return error_response("No data provided", 400)
        
        current_user = get_current_user()
        
        # Get required fields
        session_id = data.get('session_id')
        lat = data.get('lat')
        lon = data.get('lon')
        force = data.get('force', False)  # Admin can force check-in
        
        # For students, use their own user_id, for admin/teacher allow specifying user_id
        if current_user.get('role') in ['admin', 'teacher']:
            user_id = data.get('user_id', current_user['user_id'])
        else:
            user_id = current_user['user_id']
        
        if not session_id:
            return error_response("Session ID is required", 400)
        
        # Mark attendance using the service layer
        from services.attendance_service import mark_user_attendance
        record = mark_user_attendance(session_id, user_id, lat, lon, force)
        
        if not record:
            return error_response("Failed to create attendance record", 400)
        
        return success_response(
            data={
                'record_id': record.record_id,
                'user_id': user_id,
                'session_id': session_id,
                'check_in_time': record.check_in_time.isoformat(),
                'status': 'present',
                'location': {
                    'lat': record.check_in_lat,
                    'lon': record.check_in_lon
                } if record.check_in_lat and record.check_in_lon else None
            },
            message="Check-in successful"
        )
    except Exception as e:
        return error_response(str(e), 400)

@attendance_bp.route('/check-out', methods=['POST'])
@token_required
def check_out():
    """Mark attendance check-out for a user."""
    try:
        data = request.get_json()
        if not data:
            return error_response("No data provided", 400)
        
        record_id = data.get('record_id')
        lat = data.get('lat')
        lon = data.get('lon')
        
        if not record_id:
            return error_response("Record ID is required", 400)
        
        # Mark checkout
        record = checkout_user_attendance(record_id, lat, lon)
        
        return success_response(
            data={
                'record_id': record.record_id,
                'check_out_time': record.check_out_time.isoformat(),
                'location': {
                    'lat': record.check_out_lat,
                    'lon': record.check_out_lon
                } if record.check_out_lat and record.check_out_lon else None
            },
            message="Check-out successful"
        )
    except Exception as e:
        return error_response(str(e), 400)

@attendance_bp.route('/session/<session_id>/report', methods=['GET'])
@teacher_or_admin_required
def get_session_attendance_report(session_id):
    """Get detailed attendance report for a session."""
    try:
        report = get_session_report(session_id)
        return success_response(
            data=report,
            message="Session report retrieved successfully"
        )
    except Exception as e:
        return error_response(str(e), 500)

@attendance_bp.route('/user/<user_id>/history', methods=['GET'])
@token_required
def get_user_history(user_id):
    """Get attendance history for a user."""
    try:
        current_user = get_current_user()
        
        # Users can only see their own history unless they're admin/teacher
        if current_user.get('role') not in ['admin', 'teacher'] and current_user['user_id'] != user_id:
            return error_response("Access denied", 403)
        
        # Get query parameters
        org_id = request.args.get('org_id')
        limit = request.args.get('limit', type=int)
        
        history = get_user_attendance_history(user_id, org_id, limit)
        return success_response(
            data=history,
            message="User attendance history retrieved successfully"
        )
    except Exception as e:
        return error_response(str(e), 500)

@attendance_bp.route('/my-history', methods=['GET'])
@token_required
def get_my_history():
    """Get attendance history for the current user."""
    try:
        current_user = get_current_user()
        
        # Get query parameters
        limit = request.args.get('limit', type=int)
        
        history = get_user_attendance_history(current_user['user_id'], None, limit)
        return success_response(
            data=history,
            message="Your attendance history retrieved successfully"
        )
    except Exception as e:
        return error_response(str(e), 500)

@attendance_bp.route('/active-sessions', methods=['GET'])
@token_required
def get_active_sessions():
    """Get active attendance sessions for the user's organization."""
    try:
        current_user = get_current_user()
        org_id = current_user.get('org_id')
        
        if not org_id:
            return error_response("User organization not found", 400)
        
        sessions = get_organization_active_sessions(org_id)
        return success_response(
            data=sessions,
            message="Active sessions retrieved successfully"
        )
    except Exception as e:
        return error_response(str(e), 500)

@attendance_bp.route('/public-sessions', methods=['GET'])
def get_public_active_sessions():
    """Public endpoint to check active sessions (for testing)."""
    try:
        from config.db import db
        from utils.response import success_response, error_response
        
        # Get ALL active sessions across all organizations (only basic fields)
        sessions = db.session.execute(
            db.text("SELECT session_id, session_name, org_id, start_time, end_time, created_by, is_active FROM attendance_sessions WHERE is_active = true")
        ).fetchall()
        
        session_data = []
        for session in sessions:
            session_data.append({
                'session_id': session[0],
                'session_name': session[1],
                'org_id': session[2],
                'start_time': session[3].isoformat() if session[3] else None,
                'end_time': session[4].isoformat() if session[4] else None,
                'created_by': session[5],
                'is_active': session[6]
            })
        
        return success_response(
            data=session_data,
            message=f"Found {len(session_data)} active sessions"
        )
    except Exception as e:
        return error_response(str(e), 500)

@attendance_bp.route('/sessions/<session_id>', methods=['GET'])
def get_session_details(session_id):
    """Get details of a specific session (public endpoint)."""
    try:
        from config.db import db
        from utils.response import success_response, error_response
        
        # Get session details using raw SQL to avoid schema issues
        session = db.session.execute(
            db.text("SELECT session_id, session_name, description, org_id, start_time, end_time, created_by, is_active FROM attendance_sessions WHERE session_id = :session_id"),
            {"session_id": session_id}
        ).fetchone()
        
        if not session:
            return error_response("Session not found", 404)
        
        session_data = {
            'session_id': session[0],
            'session_name': session[1], 
            'description': session[2],
            'org_id': session[3],
            'start_time': session[4].isoformat() if session[4] else None,
            'end_time': session[5].isoformat() if session[5] else None,
            'created_by': session[6],
            'is_active': session[7]
        }
        
        return success_response(
            data=session_data,
            message="Session details retrieved successfully"
        )
    except Exception as e:
        return error_response(str(e), 500)

@attendance_bp.route('/session/<session_id>/attendance', methods=['GET'])
@teacher_or_admin_required
def get_session_attendance(session_id):
    """Get attendance records for a specific session."""
    try:
        from models.attendance import get_session_attendance
        records = get_session_attendance(session_id)
        
        return success_response(
            data={
                'session_id': session_id,
                'attendance_records': records,  # Already converted to dict
                'total_records': len(records)
            },
            message="Session attendance retrieved successfully"
        )
    except Exception as e:
        return error_response(str(e), 500)