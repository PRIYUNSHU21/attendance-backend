#!/usr/bin/env python3
"""
Test session creation locally to ensure it works
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

import requests
import json
from datetime import datetime, timedelta

def test_session_creation():
    base_url = "http://localhost:5000"
    
    # Login as teacher first
    login_data = {
        "email": "alpha@gmail.com",
        "password": "P21042004p#"
    }
    
    print("🔐 Logging in as teacher...")
    response = requests.post(f"{base_url}/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        return
    
    auth_data = response.json()
    print(f"Auth response: {auth_data}")
    token = auth_data.get('data', {}).get('jwt_token')
    print(f"✅ Login successful! Token: {token[:20]}..." if token else "No token received")
    
    # Create session with location data
    start_time = datetime.now().replace(minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=2)
    
    session_data = {
        "session_name": "Test Session with Location",
        "description": "Testing session creation with location",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "latitude": 28.6139,  # New Delhi
        "longitude": 77.2090,
        "radius": 100
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("📍 Creating session with location data...")
    response = requests.post(f"{base_url}/admin/sessions", 
                           json=session_data, headers=headers)
    
    if response.status_code == 201:
        session_result = response.json()
        print(f"✅ Session created successfully!")
        print(f"Response: {session_result}")
        session_data_response = session_result.get('data', session_result)
        if 'session_id' in session_data_response:
            print(f"Session ID: {session_data_response['session_id']}")
            print(f"Session Name: {session_data_response['session_name']}")
            print(f"Location: {session_data_response.get('latitude', 'None')}, {session_data_response.get('longitude', 'None')}")
    else:
        print(f"❌ Session creation failed: {response.status_code}")
        print(response.text)
    
    # Also test without location data
    session_data_no_location = {
        "session_name": "Test Session without Location",
        "description": "Testing session creation without location",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    }
    
    print("\n🏫 Creating session without location data...")
    response = requests.post(f"{base_url}/admin/sessions", 
                           json=session_data_no_location, headers=headers)
    
    if response.status_code == 201:
        session_result = response.json()
        print(f"✅ Session created successfully!")
        print(f"Response: {session_result}")
        session_data_response = session_result.get('data', session_result)
        if 'session_id' in session_data_response:
            print(f"Session ID: {session_data_response['session_id']}")
            print(f"Session Name: {session_data_response['session_name']}")
            print(f"Location: {session_data_response.get('latitude', 'None')}, {session_data_response.get('longitude', 'None')}")
    else:
        print(f"❌ Session creation failed: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_session_creation()
