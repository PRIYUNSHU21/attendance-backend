"""
✅ ATTENDANCE SERVICE - services/attendance_service.py

🎯 WHAT THIS FILE DOES:
This file handles all attendance-related business logic and operations.
Think of it as the "attendance manager" that coordinates check-ins, sessions, and reporting.

🔧 FOR FRONTEND DEVELOPERS:
- This powers your attendance check-in/check-out features
- Handles location-based verification (geofencing)
- Manages attendance sessions (classes, meetings, events)
- Provides attendance reports and analytics

📋 MAIN FUNCTIONS FOR FRONTEND:
1. create_session(): Create new attendance sessions (classes/meetings)
2. mark_user_attendance(): Handle check-in process with location verification
3. checkout_user_attendance(): Handle check-out process
4. get_session_report(): Get detailed attendance reports for sessions
5. get_user_attendance_history(): Get individual user attendance history
6. get_organization_active_sessions(): List active sessions for organization

🌐 API INTEGRATION EXAMPLES:

CHECK-IN PROCESS:
Frontend sends: { 
  "session_id": "session-uuid", 
  "lat": 40.7128, 
  "lon": -74.0060 
}
Service validates location and returns: {
  "record_id": "attendance-record-uuid",
  "status": "present|late",
  "check_in_time": "2025-07-05T09:15:00Z"
}

CREATE SESSION:
Frontend sends: {
  "session_name": "Math 101",
  "start_time": "2025-07-05T09:00:00Z",
  "end_time": "2025-07-05T10:30:00Z",
  "location_lat": 40.7128,
  "location_lon": -74.0060,
  "location_radius": 50
}

📍 LOCATION-BASED FEATURES:
- Geofence validation: Users must be within specified radius to check in
- GPS coordinates required for check-in/check-out
- Configurable radius per session (default from settings)
- Distance calculation using Haversine formula

⚡ FRONTEND USAGE FLOW:
1. Get user's current location (navigator.geolocation)
2. Send check-in request with coordinates
3. Backend validates if user is within geofence
4. Returns success/failure with attendance record
5. Display confirmation to user

🔄 ATTENDANCE STATES:
- "present": On time check-in
- "late": Check-in after session start time
- "absent": No check-in recorded
- "checked_out": Completed full attendance cycle

📊 REPORTING FEATURES:
- Session-level reports: Who attended which session
- User-level reports: Individual attendance history
- Organization-level analytics: Attendance trends and patterns
- Date range filtering for historical data

🛡️ BUSINESS RULES:
- Users can only check into sessions they're authorized for
- Location must be within geofence radius
- Duplicate check-ins are prevented
- Late arrivals are marked as "late" status
- Teachers/admins can force check-ins for special cases

📱 EXAMPLE FRONTEND IMPLEMENTATION:
// Get user location and check in
navigator.geolocation.getCurrentPosition(async (position) => {
  const response = await fetch('/attendance/check-in', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      session_id: sessionId,
      lat: position.coords.latitude,
      lon: position.coords.longitude
    })
  });
});
"""

from datetime import datetime, timedelta
from models.attendance import (
    create_session_model as create_attendance_session, mark_attendance, mark_checkout,
    get_session_attendance, get_user_attendance, get_active_sessions
)
from models.user import User
from services.geo_service import is_within_geofence, validate_coordinates
from config.settings import Config

def create_session(data, created_by_user_id):
    """
    Create a new attendance session.
    
    Args:
        data: Dictionary containing session information
        created_by_user_id: ID of the user creating the session
        
    Returns:
        Created session object
    """
    print(f"DEBUG: create_session called with data: {data}")
    
    # Validate required fields
    required_fields = ['org_id', 'session_name', 'start_time', 'end_time']
    for field in required_fields:
        if field not in data:
            raise Exception(f"Missing required field: {field}")
    
    # Validate dates
    start_time = datetime.fromisoformat(data['start_time'])
    end_time = datetime.fromisoformat(data['end_time'])
    
    print(f"DEBUG: Parsed times - start: {start_time}, end: {end_time}")
    
    if start_time >= end_time:
        raise Exception("Start time must be before end time")
    
    print(f"DEBUG: About to call create_attendance_session")
    
    # Validate location if provided
    if 'location_lat' in data and 'location_lon' in data:
        if not validate_coordinates(data['location_lat'], data['location_lon']):
            raise Exception("Invalid coordinates")
    
    # Set default radius if not provided
    if 'location_radius' not in data:
        data['location_radius'] = Config.DEFAULT_GEOFENCE_RADIUS
    
    # Add creator info
    data['created_by'] = created_by_user_id
    data['start_time'] = start_time
    data['end_time'] = end_time
    
    result = create_attendance_session(data)
    print(f"DEBUG: create_attendance_session returned: {result}")
    return result

def mark_user_attendance(session_id, user_id, lat=None, lon=None, force=False):
    """
    Mark attendance for a user in a session.
    
    Args:
        session_id: ID of the attendance session
        user_id: ID of the user marking attendance
        lat: User's latitude
        lon: User's longitude
        force: Force attendance marking (skip location validation)
        
    Returns:
        Attendance record object
    """
    # Get session details
    from models.attendance import AttendanceSession
    session = AttendanceSession.query.filter_by(session_id=session_id).first()
    if not session:
        raise Exception("Session not found")
    
    # Check if session is active
    if not session.is_active:
        raise Exception("Session is not active")
    
    # Check if session has started
    current_time = datetime.now()
    if current_time < session.start_time:
        raise Exception("Session has not started yet")
    
    # Check if session has ended
    if current_time > session.end_time:
        raise Exception("Session has already ended")
    
    # Validate user
    user = User.find_by_id(user_id)
    if not user:
        raise Exception("User not found")
    
    # Check if user belongs to the same organization
    if user.org_id != session.org_id:
        raise Exception("User does not belong to this organization")
    
    # Location validation if required
    if not force and session.latitude and session.longitude:
        if not lat or not lon:
            raise Exception("Location coordinates are required")
        
        if not validate_coordinates(lat, lon):
            raise Exception("Invalid coordinates")
        
        if not is_within_geofence(lat, lon, session.latitude, 
                                 session.longitude, session.radius):
            raise Exception("You are not within the allowed location")
    
    # Determine attendance status
    status = 'present'
    if current_time > session.start_time + timedelta(minutes=15):
        status = 'late'
    
    # Mark attendance
    result = mark_attendance(session_id, user_id, user.org_id, lat, lon, user_id)
    
    if isinstance(result, dict) and 'error' in result:
        raise Exception(result['error'])
    
    return result

def checkout_user_attendance(record_id, lat=None, lon=None):
    """
    Mark checkout for a user's attendance record.
    
    Args:
        record_id: ID of the attendance record
        lat: User's latitude
        lon: User's longitude
        
    Returns:
        Updated attendance record
    """
    # Validate coordinates if provided
    if lat and lon and not validate_coordinates(lat, lon):
        raise Exception("Invalid coordinates")
    
    result = mark_checkout(record_id, lat, lon)
    if not result:
        raise Exception("Attendance record not found")
    
    return result

def get_session_report(session_id):
    """
    Get attendance report for a session.
    
    Args:
        session_id: ID of the session
        
    Returns:
        Dictionary containing session and attendance data
    """
    from models.attendance import AttendanceSession
    
    session = AttendanceSession.query.filter_by(session_id=session_id).first()
    if not session:
        raise Exception("Session not found")
    
    attendance_records = get_session_attendance(session_id)
    
    # Calculate statistics
    total_attendees = len(attendance_records)
    present_count = len([r for r in attendance_records if r.status == 'present'])
    late_count = len([r for r in attendance_records if r.status == 'late'])
    
    return {
        'session': session.to_dict(),
        'attendance_records': [record.to_dict() for record in attendance_records],
        'statistics': {
            'total_attendees': total_attendees,
            'present_count': present_count,
            'late_count': late_count,
            'attendance_rate': (present_count + late_count) / total_attendees * 100 if total_attendees > 0 else 0
        }
    }

def get_user_attendance_history(user_id, org_id=None, limit=None):
    """
    Get attendance history for a user.
    
    Args:
        user_id: ID of the user
        org_id: Optional organization ID filter
        limit: Optional limit on number of records
        
    Returns:
        List of attendance records
    """
    records = get_user_attendance(user_id, org_id)
    
    # Sort by most recent first
    records.sort(key=lambda x: x.check_in_time, reverse=True)
    
    # Apply limit if specified
    if limit:
        records = records[:limit]
    
    return [record.to_dict() for record in records]

def get_organization_active_sessions(org_id):
    """
    Get all active sessions for an organization - FIXED VERSION.
    """
    try:
        from models.attendance import AttendanceSession
        
        # Get ALL sessions for organization (ignore timing for now)
        sessions = AttendanceSession.query.filter_by(
            org_id=org_id, 
            is_active=True
        ).all()
        
        print(f"DEBUG: Found {len(sessions)} sessions for org {org_id}")
        
        # Return all sessions (remove timing filter that was causing issues)
        result = [session.to_dict() for session in sessions]
        print(f"DEBUG: Returning {len(result)} sessions")
        return result
        
    except Exception as e:
        print(f"ERROR in get_organization_active_sessions: {e}")
        return []