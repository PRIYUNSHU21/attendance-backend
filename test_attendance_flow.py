#!/usr/bin/env python3
"""
Test complete attendance workflow with proper authentication
"""
import requests
import json
import uuid
from datetime import datetime

BASE_URL = "https://attendance-backend-go8h.onrender.com"

def test_complete_attendance_flow():
    print("🚀 TESTING COMPLETE ATTENDANCE FLOW")
    print("=" * 50)
    
    # Step 1: Get available sessions
    print("1️⃣ Getting available sessions...")
    sessions_response = requests.get(f"{BASE_URL}/attendance/public-sessions")
    if sessions_response.status_code != 200:
        print(f"❌ Failed to get sessions: {sessions_response.status_code}")
        return False
    
    sessions = sessions_response.json()["data"]
    if not sessions:
        print("❌ No sessions available")
        return False
    
    # Try to find a session with valid organization
    session = None
    for s in sessions:
        if s["org_id"] != "1":  # Avoid org_id "1" which seems to have issues
            session = s
            break
    
    if not session:
        session = sessions[0]  # Fallback to first session
    
    session_id = session["session_id"]
    print(f"✅ Found session: {session['session_name']} (ID: {session_id})")
    print(f"   Organization: {session['org_id']}")
    
    # Step 2: Register a new student
    print("\n2️⃣ Registering new student...")
    student_data = {
        "name": "Test Student",
        "email": f"student_{uuid.uuid4().hex[:8]}@test.com",
        "password": "TestPass123!",
        "role": "student",
        "org_id": session["org_id"]
    }
    
    register_response = requests.post(f"{BASE_URL}/auth/register", json=student_data)
    print(f"Registration status: {register_response.status_code}")
    if register_response.status_code in [200, 201]:
        print(f"✅ Student registered: {student_data['email']}")
    else:
        print(f"⚠️ Registration response: {register_response.text}")
    
    # Step 3: Login the student
    print("\n3️⃣ Logging in student...")
    login_data = {
        "email": student_data["email"],
        "password": student_data["password"]
    }
    
    login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return False
    
    login_result = login_response.json()
    print(f"Login response: {login_result}")
    
    # Handle different response formats
    if "data" in login_result and "jwt_token" in login_result["data"]:
        token = login_result["data"]["jwt_token"]
        user_id = login_result["data"]["user"]["user_id"]
    elif "data" in login_result and "token" in login_result["data"]:
        token = login_result["data"]["token"]
        user_id = login_result["data"]["user"]["user_id"]
    elif "data" in login_result and "access_token" in login_result["data"]:
        token = login_result["data"]["access_token"]
        user_id = login_result["data"]["user"]["user_id"]
    else:
        print(f"❌ Unexpected login response format: {login_result}")
        return False
        
    print(f"✅ Login successful, token: {token[:20]}...")
    
    # Step 4: Mark attendance
    print("\n4️⃣ Marking attendance...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    attendance_data = {
        "session_id": session_id,
        "lat": 40.7128,
        "lon": -74.0060
    }
    
    attendance_response = requests.post(
        f"{BASE_URL}/attendance/check-in", 
        json=attendance_data, 
        headers=headers
    )
    
    print(f"Attendance status: {attendance_response.status_code}")
    print(f"Response: {attendance_response.text}")
    
    if attendance_response.status_code == 200:
        print("✅ ATTENDANCE MARKED SUCCESSFULLY!")
        return True
    else:
        print("❌ Attendance marking failed")
        return False

if __name__ == "__main__":
    success = test_complete_attendance_flow()
    if success:
        print("\n🎉 COMPLETE ATTENDANCE WORKFLOW: SUCCESS")
    else:
        print("\n❌ COMPLETE ATTENDANCE WORKFLOW: FAILED")
