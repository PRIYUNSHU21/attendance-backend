# services/geo_service.py
"""
Geo service module for location-based operations.
This module provides functions for distance calculations and geofence validation.
"""

import math
from typing import Tuple

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth.
    Uses the Haversine formula to calculate distance in meters.
    
    Args:
        lat1, lon1: Latitude and longitude of first point
        lat2, lon2: Latitude and longitude of second point
        
    Returns:
        Distance in meters
    """
    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of Earth in meters
    earth_radius = 6371000
    
    # Calculate the distance
    distance = earth_radius * c
    return distance

def is_within_geofence(user_lat: float, user_lon: float, 
                      center_lat: float, center_lon: float, 
                      radius: float) -> bool:
    """
    Check if a user's location is within a geofence.
    
    Args:
        user_lat, user_lon: User's current latitude and longitude
        center_lat, center_lon: Center of the geofence
        radius: Radius of the geofence in meters
        
    Returns:
        True if user is within the geofence, False otherwise
    """
    distance = calculate_distance(user_lat, user_lon, center_lat, center_lon)
    return distance <= radius

def validate_coordinates(lat: float, lon: float) -> bool:
    """
    Validate latitude and longitude coordinates.
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
        
    Returns:
        True if coordinates are valid, False otherwise
    """
    return (-90 <= lat <= 90) and (-180 <= lon <= 180)

def get_location_accuracy_status(accuracy: float) -> str:
    """
    Get location accuracy status based on accuracy value.
    
    Args:
        accuracy: GPS accuracy in meters
        
    Returns:
        Status string (high, medium, low)
    """
    if accuracy <= 5:
        return "high"
    elif accuracy <= 20:
        return "medium"
    else:
        return "low"

def format_coordinates(lat: float, lon: float, precision: int = 6) -> Tuple[str, str]:
    """
    Format coordinates to specified precision.
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
        precision: Number of decimal places
        
    Returns:
        Tuple of formatted latitude and longitude strings
    """
    lat_str = f"{lat:.{precision}f}"
    lon_str = f"{lon:.{precision}f}"
    return lat_str, lon_str