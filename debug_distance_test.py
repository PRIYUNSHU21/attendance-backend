#!/usr/bin/env python3
"""
Debug test to check distance calculation and organization location
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def login_user(role):
    """Login and get token"""
    credentials = {
        'admin': {'email': 'psaha21.un@gmail.com', 'password': 'P21042004p#'},
        'student': {'email': 'beta@gmail.com', 'password': 'P21042004p#'}
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=credentials[role])
        if response.status_code == 200:
            data = response.json()
            return data['data']['jwt_token']
    except Exception as e:
        print(f"Login error: {e}")
    return None

def debug_distance_calculation():
    """Debug the distance calculation and location setup"""
    print("🔍 DEBUGGING DISTANCE CALCULATION")
    print("=" * 50)
    
    admin_token = login_user('admin')
    student_token = login_user('student')
    
    if not admin_token or not student_token:
        print("❌ Cannot login")
        return
    
    # 1. First set up organization location
    print("\n1️⃣ Setting up organization location...")
    setup_payload = {
        "latitude": 22.6164736,
        "longitude": 88.3785728, 
        "name": "Test Organization",
        "radius": 100
    }
    
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(f"{BASE_URL}/simple/company/create", json=setup_payload, headers=headers)
    print(f"Organization setup status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Organization location set: {result.get('data', {}).get('location')}")
    else:
        print(f"Organization setup failed: {response.text}")
    
    # 2. Test close location (should be present)
    print("\n2️⃣ Testing close location (should be PRESENT)...")
    close_payload = {
        "latitude": 22.6165,  # Very close to org location
        "longitude": 88.3786,
        "session_id": "test-session"  # We'll use a dummy session for now
    }
    
    student_headers = {
        "Authorization": f"Bearer {student_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(f"{BASE_URL}/simple/mark-attendance", json=close_payload, headers=student_headers)
    print(f"Close location status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Status: {result.get('data', {}).get('status')}")
        print(f"Distance: {result.get('data', {}).get('distance')}m")
    else:
        print(f"Close location failed: {response.text}")
    
    # 3. Test far location (should be absent)
    print("\n3️⃣ Testing far location (should be ABSENT)...")
    far_payload = {
        "latitude": 40.7128,  # New York (very far from Kolkata)
        "longitude": -74.0060,
        "session_id": "test-session"
    }
    
    response = requests.post(f"{BASE_URL}/simple/mark-attendance", json=far_payload, headers=student_headers)
    print(f"Far location status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Status: {result.get('data', {}).get('status')}")
        print(f"Distance: {result.get('data', {}).get('distance')}m")
        
        # Calculate expected distance manually
        from math import radians, sin, cos, sqrt, atan2
        
        def calculate_distance(lat1, lon1, lat2, lon2):
            R = 6371000  # Earth's radius in meters
            dLat = radians(lat2 - lat1)
            dLon = radians(lon2 - lon1)
            a = (sin(dLat / 2) ** 2 + 
                 cos(radians(lat1)) * cos(radians(lat2)) * sin(dLon / 2) ** 2)
            distance = R * 2 * atan2(sqrt(a), sqrt(1 - a))
            return distance
        
        expected_distance = calculate_distance(22.6164736, 88.3785728, 40.7128, -74.0060)
        print(f"Expected distance: {expected_distance:.0f}m ({expected_distance/1000:.0f}km)")
        
        if result.get('data', {}).get('status') == 'absent':
            print("✅ Correctly marked as absent")
        else:
            print("⚠️ Should be marked as absent but wasn't")
    else:
        print(f"Far location failed: {response.text}")

if __name__ == "__main__":
    debug_distance_calculation()
