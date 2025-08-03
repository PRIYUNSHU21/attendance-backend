"""
📍 GEOLOCATION SERVICE - services/geo_service.py

🎯 WHAT THIS FILE DOES:
Provides geolocation utilities for attendance verification.
Handles distance calculations and geofencing logic.
"""

import math

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees).
    
    Args:
        lat1, lon1: Latitude and longitude of first point
        lat2, lon2: Latitude and longitude of second point
        
    Returns:
        Distance in meters
        
    FIXED: Ensures all inputs are converted to float to avoid Decimal/str type errors
    """
    # Convert all inputs to float to handle Decimal/str/int types from database/frontend
    try:
        lat1 = float(lat1)
        lon1 = float(lon1)
        lat2 = float(lat2)
        lon2 = float(lon2)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid coordinate values: {e}")
    
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in meters
    r = 6371000
    
    return c * r

def is_within_geofence(user_lat, user_lon, center_lat, center_lon, radius_meters):
    """
    Check if a user's location is within a geofenced area.
    
    Args:
        user_lat, user_lon: User's current coordinates
        center_lat, center_lon: Center coordinates of geofence
        radius_meters: Radius of geofence in meters
        
    Returns:
        Boolean indicating if user is within geofence
    """
    distance = haversine_distance(user_lat, user_lon, center_lat, center_lon)
    return distance <= radius_meters

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

def calculate_distance_simple(lat1, lon1, lat2, lon2):
    """
    Simple distance calculation (alias for haversine_distance).
    
    Args:
        lat1, lon1: First point coordinates
        lat2, lon2: Second point coordinates
        
    Returns:
        Distance in meters
    """
    return haversine_distance(lat1, lon1, lat2, lon2)
