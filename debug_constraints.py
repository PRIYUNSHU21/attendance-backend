#!/usr/bin/env python3
"""
Diagnose attendance database constraints
"""
import requests
import json

BASE_URL = "https://attendance-backend-go8h.onrender.com"
STUDENT_CREDS = {"email": "beta@gmail.com", "password": "P21042004p#"}

def check_database_constraints():
    """Check if all required records exist for attendance"""
    print("🔍 DIAGNOSING DATABASE CONSTRAINTS")
    print("=" * 50)
    
    # Login student
    print("1️⃣ Logging in student...")
    login_response = requests.post(f"{BASE_URL}/auth/login", json=STUDENT_CREDS)
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    login_data = login_response.json()
    token = login_data["data"]["jwt_token"]
    user = login_data["data"]["user"]
    
    print(f"✅ Student logged in:")
    print(f"   User ID: {user['user_id']}")
    print(f"   Org ID: {user['org_id']}")
    print(f"   Role: {user['role']}")
    
    # Get sessions
    print("\n2️⃣ Getting sessions...")
    sessions_response = requests.get(f"{BASE_URL}/attendance/public-sessions")
    if sessions_response.status_code != 200:
        print(f"❌ Failed to get sessions: {sessions_response.text}")
        return
    
    sessions = sessions_response.json()["data"]
    
    # Find matching session
    user_org = user['org_id']
    matching_session = None
    for session in sessions:
        if session['org_id'] == user_org:
            matching_session = session
            break
    
    if not matching_session:
        print(f"❌ No session found for org {user_org}")
        return
    
    print(f"✅ Found matching session:")
    print(f"   Session ID: {matching_session['session_id']}")
    print(f"   Session Name: {matching_session['session_name']}")
    print(f"   Org ID: {matching_session['org_id']}")
    
    # Try to create attendance record manually via API to see detailed error
    print("\n3️⃣ Testing attendance creation...")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    attendance_data = {
        "session_id": matching_session['session_id'],
        "lat": 40.7128,
        "lon": -74.0060
    }
    
    print(f"Sending data: {attendance_data}")
    
    response = requests.post(f"{BASE_URL}/attendance/check-in", json=attendance_data, headers=headers)
    print(f"Response status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Test if we can get session details
    print(f"\n4️⃣ Testing session details...")
    session_response = requests.get(f"{BASE_URL}/attendance/sessions/{matching_session['session_id']}")
    print(f"Session details status: {session_response.status_code}")
    print(f"Session details: {session_response.text}")

if __name__ == "__main__":
    check_database_constraints()
