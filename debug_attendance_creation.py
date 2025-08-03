#!/usr/bin/env python3
"""
Debug attendance creation issues
"""
import requests
import json
import uuid

BASE_URL = "https://attendance-backend-go8h.onrender.com"

def debug_attendance_creation():
    print("🔍 DEBUGGING ATTENDANCE CREATION")
    print("=" * 50)
    
    # Step 1: Get a session
    print("1️⃣ Getting session...")
    sessions_response = requests.get(f"{BASE_URL}/attendance/public-sessions")
    sessions = sessions_response.json()["data"]
    
    # Use a session with org_id "1" which might be more stable
    session = None
    for s in sessions:
        if s["org_id"] == "1":
            session = s
            break
    
    if not session:
        session = sessions[0]
    
    print(f"✅ Using session: {session['session_name']}")
    print(f"   Session ID: {session['session_id']}")
    print(f"   Org ID: {session['org_id']}")
    
    # Step 2: Register user in SAME organization as session
    print(f"\n2️⃣ Registering user in org {session['org_id']}...")
    student_data = {
        "name": "Debug Student",
        "email": f"debug_{uuid.uuid4().hex[:8]}@test.com",
        "password": "TestPass123!",
        "role": "student",
        "org_id": session["org_id"]  # Use SAME org as session
    }
    
    register_response = requests.post(f"{BASE_URL}/auth/register", json=student_data)
    print(f"Registration status: {register_response.status_code}")
    
    if register_response.status_code != 201:
        print(f"❌ Registration failed: {register_response.text}")
        return False
    
    print(f"✅ Student registered in org: {session['org_id']}")
    
    # Step 3: Login
    print(f"\n3️⃣ Logging in...")
    login_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": student_data["email"],
        "password": student_data["password"]
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return False
    
    token = login_response.json()["data"]["jwt_token"]
    user_info = login_response.json()["data"]["user"]
    print(f"✅ Logged in successfully")
    print(f"   User ID: {user_info['user_id']}")
    print(f"   User Org: {user_info['org_id']}")
    print(f"   Session Org: {session['org_id']}")
    
    # Step 4: Check org match
    if user_info['org_id'] != session['org_id']:
        print(f"⚠️ ORG MISMATCH: User org {user_info['org_id']} != Session org {session['org_id']}")
    else:
        print(f"✅ ORG MATCH: Both user and session in org {session['org_id']}")
    
    # Step 5: Try attendance
    print(f"\n4️⃣ Marking attendance...")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    attendance_data = {
        "session_id": session["session_id"],
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
        print("✅ ATTENDANCE SUCCESSFUL!")
        return True
    else:
        print("❌ ATTENDANCE FAILED")
        return False

if __name__ == "__main__":
    debug_attendance_creation()
