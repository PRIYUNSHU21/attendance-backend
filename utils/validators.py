"""
🔍 VALIDATION UTILITIES - utils/validators.py

🎯 WHAT THIS FILE DOES:
Provides validation functions for input data validation.
Simple validation logic to ensure data integrity.
"""

import re

def validate_attendance_data(data):
    """
    Validate attendance data.
    
    Args:
        data: Dictionary containing attendance data
        
    Returns:
        Dictionary with validation result
    """
    if not data:
        return {
            'is_valid': False,
            'errors': ['No data provided']
        }
    
    errors = []
    
    # Basic validation - just check if it's a dictionary
    if not isinstance(data, dict):
        errors.append('Data must be a valid JSON object')
    
    if errors:
        return {
            'is_valid': False,
            'errors': errors
        }
    
    return {
        'is_valid': True,
        'errors': []
    }

def validate_user_data(data):
    """
    Validate user data for registration/update.
    
    Args:
        data: Dictionary containing user data
        
    Returns:
        Dictionary with validation result
    """
    if not data:
        return {
            'is_valid': False,
            'errors': ['No data provided']
        }
    
    errors = []
    
    # Check email format
    email = data.get('email', '')
    if email:
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            errors.append('Invalid email format')
    
    # Check password length
    password = data.get('password', '')
    if password and len(password) < 6:
        errors.append('Password must be at least 6 characters long')
    
    # Check name
    name = data.get('name', '')
    if name and len(name.strip()) < 2:
        errors.append('Name must be at least 2 characters long')
    
    if errors:
        return {
            'is_valid': False,
            'errors': errors
        }
    
    return {
        'is_valid': True,
        'errors': []
    }

def validate_attendance_session_data(data):
    """
    Validate attendance session data.
    
    Args:
        data: Dictionary containing session data
        
    Returns:
        Dictionary with validation result
    """
    if not data:
        return {
            'is_valid': False,
            'errors': ['No data provided']
        }
    
    errors = []
    
    # Check session name
    session_name = data.get('session_name', '')
    if not session_name or len(session_name.strip()) < 3:
        errors.append('Session name must be at least 3 characters long')
    
    # Check dates if provided
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    
    if start_time and end_time:
        try:
            from datetime import datetime
            start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            
            if start >= end:
                errors.append('Start time must be before end time')
        except ValueError:
            errors.append('Invalid date format')
    
    if errors:
        return {
            'is_valid': False,
            'errors': errors
        }
    
    return {
        'is_valid': True,
        'errors': []
    }

def validate_pagination_params(data):
    """
    Validate pagination parameters.
    
    Args:
        data: Dictionary containing pagination data
        
    Returns:
        Dictionary with validation result
    """
    if not data:
        return {
            'is_valid': True,
            'errors': []
        }
    
    errors = []
    
    # Check page number
    page = data.get('page')
    if page is not None:
        try:
            page_num = int(page)
            if page_num < 1:
                errors.append('Page number must be positive')
        except (ValueError, TypeError):
            errors.append('Page must be a valid number')
    
    # Check limit
    limit = data.get('limit')
    if limit is not None:
        try:
            limit_num = int(limit)
            if limit_num < 1 or limit_num > 100:
                errors.append('Limit must be between 1 and 100')
        except (ValueError, TypeError):
            errors.append('Limit must be a valid number')
    
    if errors:
        return {
            'is_valid': False,
            'errors': errors
        }
    
    return {
        'is_valid': True,
        'errors': []
    }

def validate_coordinates(lat, lon):
    """
    Validate GPS coordinates.
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        Boolean indicating if coordinates are valid
    """
    try:
        lat = float(lat)
        lon = float(lon)
        
        # Check if coordinates are within valid ranges
        if -90 <= lat <= 90 and -180 <= lon <= 180:
            return True
        
        return False
    except (TypeError, ValueError):
        return False

def validate_required_fields(data, required_fields):
    """
    Validate that required fields are present in data.
    
    Args:
        data: Dictionary to validate
        required_fields: List of required field names
        
    Returns:
        Dictionary with validation result
    """
    if not data:
        return {
            'is_valid': False,
            'errors': ['No data provided']
        }
    
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None:
            missing_fields.append(field)
    
    if missing_fields:
        return {
            'is_valid': False,
            'errors': [f'Missing required fields: {", ".join(missing_fields)}']
        }
    
    return {
        'is_valid': True,
        'errors': []
    }
