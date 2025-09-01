"""
🚀 SIMPLIFIED ATTENDANCE ROUTES - routes/simple_attendance.py

🎯 WHAT THIS FILE DOES:
Simplified attendance logic inspired by Firebase approach.
Reduces complexity while maintaining core functionality.

Key Simplifications:
1. Single attendance endpoint (no separate check-in/check-out)
2. Simple distance calculation 
3. Immediate status determination
4. Minimal database operations
5. Error-resistant design

📋 ENDPOINTS:
POST /simple/mark-attendance - Mark attendance (create or update)
GET /simple/attendance/<company_id> - Get attendance for organization
GET /simple/company/create - Create company/organization location
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from math import radians, sin, cos, sqrt, atan2
import uuid
from config.db import db
from utils.auth import token_required, get_current_user
from utils.response import success_response, error_response

simple_attendance_bp = Blueprint('simple_attendance', __name__)

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two points using Haversine formula.
    Simple and reliable distance calculation.
    
    FIXED: Ensures all inputs are converted to float to avoid Decimal/str type errors
    """
    R = 6371000  # Earth's radius in meters
    
    # Convert all inputs to float to handle Decimal/str/int types from database/frontend
    try:
        lat1 = float(lat1)
        lon1 = float(lon1)
        lat2 = float(lat2)
        lon2 = float(lon2)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid coordinate values: {e}")
    
    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)
    
    a = (sin(dLat / 2) ** 2 + 
         cos(radians(lat1)) * cos(radians(lat2)) * sin(dLon / 2) ** 2)
    
    distance = R * 2 * atan2(sqrt(a), sqrt(1 - a))
    return distance

@simple_attendance_bp.route('/company/create', methods=['POST'])
@token_required
def create_company_location():
    """
    Create or update company/organization location.
    Simplified version of organization location setup.
    Admin and Teacher access allowed.
    """
    try:
        current_user = get_current_user()
        
        # Check if user is admin or teacher
        if current_user.get('role') not in ['admin', 'teacher']:
            return error_response("Admin or Teacher access required", 403)
        # First, run the migration to ensure columns exist
        from migrations.add_location_columns import run_migration
        run_migration()
        
        data = request.get_json()
        current_user = get_current_user()
        
        # Validate required fields
        org_id = current_user.get('org_id')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        altitude = data.get('altitude', 0)
        radius = data.get('radius', 100)  # Default 100 meters to match frontend expectation
        
        # Fallback for different parameter naming conventions
        if latitude is None and 'location_lat' in data:
            latitude = data.get('location_lat')
        if longitude is None and 'location_lon' in data:
            longitude = data.get('location_lon')
            
        if not org_id or latitude is None or longitude is None:
            return error_response("Missing organization or location details", 400)
        
        # Get organization name for the response
        org_query = "SELECT name FROM organisations WHERE org_id = :org_id"
        org_result = db.session.execute(db.text(org_query), {'org_id': org_id}).fetchone()
        org_name = org_result[0] if org_result else "Organization"
        
        # Update organization with location
        update_query = """
        UPDATE organisations 
        SET location_lat = :lat, location_lon = :lon, location_radius = :radius, updated_at = :now
        WHERE org_id = :org_id
        """
        
        db.session.execute(db.text(update_query), {
            'lat': latitude,
            'lon': longitude,
            'radius': radius,
            'now': datetime.utcnow(),
            'org_id': org_id
        })
        db.session.commit()
        
        # Format response to match frontend expectation
        return success_response(
            data={
                'name': data.get('name', org_name),
                'location': {
                    'latitude': latitude,
                    'longitude': longitude,
                    'radius': radius
                }
            },
            message="Company location updated successfully"
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error updating company location: {str(e)}", 500)

@simple_attendance_bp.route('/mark-attendance', methods=['POST'])
@token_required
def mark_simple_attendance():
    """
    Simplified attendance marking - single endpoint for all attendance operations.
    Inspired by Firebase approach but using SQL database.
    """
    try:
        data = request.get_json()
        current_user = get_current_user()
        
        # Extract data
        user_id = current_user.get('user_id')
        org_id = current_user.get('org_id') 
        
        # Handle both session_id and session_code parameters for compatibility
        session_id = data.get('session_id')  # New format
        if session_id is None:
            session_id = data.get('session_code')  # Legacy/frontend format
        
        # Handle both parameter formats (latitude/longitude and lat/lon)
        lat = data.get('latitude')
        if lat is None:
            lat = data.get('lat')
            
        lon = data.get('longitude')
        if lon is None:
            lon = data.get('lon')
            
        alt = data.get('altitude', 0)
        
        # CRITICAL FIX: Convert coordinates to float and validate
        try:
            lat = float(lat) if lat is not None else None
            lon = float(lon) if lon is not None else None
            
            # Validate coordinate ranges
            if lat is not None and not (-90 <= lat <= 90):
                return error_response("Latitude must be between -90 and 90", 400)
            if lon is not None and not (-180 <= lon <= 180):
                return error_response("Longitude must be between -180 and 180", 400)
                
        except (ValueError, TypeError):
            return error_response("Invalid coordinate format - must be numeric", 400)
        
        if not user_id or not org_id or lat is None or lon is None:
            # Create detailed validation errors for better frontend debugging
            validation_errors = {}
            if session_id is None:
                validation_errors['session_id'] = ['Missing required parameter']
            if lat is None:
                validation_errors['latitude'] = ['Missing required parameter']
            if lon is None:
                validation_errors['longitude'] = ['Missing required parameter']
                
            return error_response(f"Invalid keys in input: {validation_errors}", 422, "Unprocessable Entity")
        
        # Get organization location
        org_query = """
        SELECT location_lat, location_lon, location_radius, name 
        FROM organisations 
        WHERE org_id = :org_id
        """
        org_result = db.session.execute(db.text(org_query), {'org_id': org_id}).fetchone()
        
        if not org_result:
            return error_response("Organization not found", 404)
        
        target_lat, target_lon, radius, org_name = org_result
        
        if target_lat is None or target_lon is None:
            return error_response("Organization location not set", 400)
            
        # CRITICAL FIX: Convert database coordinates to float to match frontend coordinates
        try:
            target_lat = float(target_lat)
            target_lon = float(target_lon)
            radius = float(radius) if radius is not None else 50.0
        except (ValueError, TypeError):
            return error_response("Invalid organization location data", 500)
        
        # Calculate distance
        distance = calculate_distance(lat, lon, target_lat, target_lon)
        
        # Determine status - simple logic
        status = "present" if distance <= (radius or 50) else "absent"
        
        # Response data structure
        response_data = {
            'record_id': None,  # Will be set below
            'user_id': user_id,
            'status': status,
            'distance_from_session': round(distance, 2),  # Frontend expects this name
            'check_in_time': None,  # Will be set below
            'organization': org_name
        }
        
        # Get current date for daily attendance
        today = datetime.utcnow().date()
        now = datetime.utcnow()
        
        # Check if attendance already exists for today
        existing_query = """
        SELECT record_id, status, check_in_time, absent_timestamps 
        FROM simple_attendance_records 
        WHERE user_id = :user_id AND org_id = :org_id AND DATE(check_in_time) = :today
        """
        
        existing = db.session.execute(db.text(existing_query), {
            'user_id': user_id,
            'org_id': org_id,
            'today': today
        }).fetchone()
        
        if existing:
            # Update existing record
            record_id = existing[0]
            response_data['record_id'] = record_id
            response_data['check_in_time'] = existing[2].isoformat() if existing[2] else None
            
            update_data = {
                'latitude': lat,
                'longitude': lon,
                'altitude': alt,
                'status': status,
                'last_updated': now,
                'record_id': record_id
            }
            
            update_query = """
            UPDATE simple_attendance_records 
            SET latitude = :latitude, longitude = :longitude, altitude = :altitude,
                status = :status, last_updated = :last_updated
            WHERE record_id = :record_id
            """
            
            # If absent, add to absent timestamps
            if status == "absent":
                # Parse existing absent timestamps (stored as JSON or comma-separated)
                existing_absents = existing[3] or ""
                if existing_absents:
                    existing_absents += f",{now.isoformat()}"
                else:
                    existing_absents = now.isoformat()
                
                update_query = """
                UPDATE simple_attendance_records 
                SET latitude = :latitude, longitude = :longitude, altitude = :altitude,
                    status = :status, last_updated = :last_updated, absent_timestamps = :absent_timestamps
                WHERE record_id = :record_id
                """
                update_data['absent_timestamps'] = existing_absents
            
            db.session.execute(db.text(update_query), update_data)
            
        else:
            # Create new record
            record_id = str(uuid.uuid4())
            response_data['record_id'] = record_id
            response_data['check_in_time'] = now.isoformat()
            
            insert_query = """
            INSERT INTO simple_attendance_records 
            (record_id, user_id, org_id, session_id, latitude, longitude, altitude, 
             status, check_in_time, last_updated, absent_timestamps)
            VALUES (:record_id, :user_id, :org_id, :session_id, :latitude, :longitude, 
                    :altitude, :status, :check_in_time, :last_updated, :absent_timestamps)
            """
            
            db.session.execute(db.text(insert_query), {
                'record_id': record_id,
                'user_id': user_id,
                'org_id': org_id,
                'session_id': session_id,
                'latitude': lat,
                'longitude': lon,
                'altitude': alt,
                'status': status,
                'check_in_time': now,
                'last_updated': now,
                'absent_timestamps': now.isoformat() if status == "absent" else None
            })
        
        db.session.commit()
        
        return success_response(
            data=response_data,
            message=f"Attendance recorded - {status}"
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f"Error recording attendance: {str(e)}", 500)

@simple_attendance_bp.route('/attendance/<org_id>', methods=['GET'])
@token_required
def get_organization_attendance(org_id):
    """
    Get attendance records for an organization.
    Simplified version similar to Firebase collection query.
    """
    try:
        current_user = get_current_user()
        
        # Check if user has access to this organization
        if current_user.get('role') not in ['admin', 'teacher'] and current_user.get('org_id') != org_id:
            return error_response("Access denied", 403)
        
        # Query attendance records
        query = """
        SELECT r.record_id, r.user_id, r.status, r.check_in_time, r.last_updated, 
               r.absent_timestamps, u.name as user_name
        FROM simple_attendance_records r
        JOIN users u ON r.user_id = u.user_id
        WHERE r.org_id = :org_id
        ORDER BY r.check_in_time DESC
        LIMIT 100
        """
        
        records = db.session.execute(db.text(query), {'org_id': org_id}).fetchall()
        
        attendance_list = []
        for record in records:
            # Format absent timestamps
            absent_timestamps = []
            if record[5]:  # absent_timestamps
                # Handle both comma-separated and JSON formats
                timestamps = record[5].split(',') if ',' in record[5] else [record[5]]
                absent_timestamps = [ts.strip() for ts in timestamps if ts.strip()]
            
            attendance_list.append({
                'record_id': record[0],
                'user_id': record[1],
                'user_name': record[6],
                'status': record[2],
                'timestamp': record[3].isoformat() if record[3] else None,
                'last_updated': record[4].isoformat() if record[4] else None,
                'absent_timestamps': absent_timestamps
            })
        
        return success_response(
            data=attendance_list,
            message=f"Found {len(attendance_list)} attendance records"
        )
        
    except Exception as e:
        return error_response(f"Error fetching attendance: {str(e)}", 500)

@simple_attendance_bp.route('/my-attendance', methods=['GET'])
@token_required
def get_my_simple_attendance():
    """Get current user's attendance history."""
    try:
        current_user = get_current_user()
        user_id = current_user.get('user_id')
        
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        days = request.args.get('days', 30, type=int)
        
        # Calculate date range
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = """
        SELECT record_id, status, check_in_time, last_updated, absent_timestamps,
               latitude, longitude
        FROM simple_attendance_records
        WHERE user_id = :user_id AND check_in_time >= :start_date
        ORDER BY check_in_time DESC
        LIMIT :limit
        """
        
        records = db.session.execute(db.text(query), {
            'user_id': user_id,
            'start_date': start_date,
            'limit': limit
        }).fetchall()
        
        attendance_history = []
        for record in records:
            attendance_history.append({
                'record_id': record[0],
                'status': record[1],
                'timestamp': record[2].isoformat() if record[2] else None,
                'last_updated': record[3].isoformat() if record[3] else None,
                'absent_count': len(record[4].split(',')) if record[4] else 0,
                'location': {
                    'latitude': record[5],
                    'longitude': record[6]
                } if record[5] and record[6] else None
            })
        
        return success_response(
            data=attendance_history,
            message=f"Found {len(attendance_history)} attendance records"
        )
        
    except Exception as e:
        return error_response(f"Error fetching attendance history: {str(e)}", 500)
