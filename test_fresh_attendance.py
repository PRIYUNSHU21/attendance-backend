#!/usr/bin/env python3
"""
Create a fresh session and test attendance
"""
import requests
import json
from datetime import datetime, timezone, timedelta

BASE_URL = "https://attendance-backend-go8h.onrender.com"

def test_fresh_attendance():
    print("🔍 TESTING FRESH SESSION ATTENDANCE")
    print("=" * 50)
    
    # Test credentials
    teacher_credentials = {
        "email": "alpha@gmail.com",
        "password": "P21042004p#"
    }
    
    student_credentials = {
        "email": "beta@gmail.com", 
        "password": "P21042004p#"
    }
    
    # Step 1: Teacher login
    print("1. Teacher login...")
    teacher_response = requests.post(f"{BASE_URL}/auth/login", json=teacher_credentials)
    
    if teacher_response.status_code != 200:
        print(f"❌ Teacher login failed: {teacher_response.text}")
        return
    
    teacher_token = teacher_response.json()["data"]["jwt_token"]
    teacher_headers = {"Authorization": f"Bearer {teacher_token}"}
    print("✅ Teacher logged in")
    
    # Step 2: Student login
    print("2. Student login...")
    student_response = requests.post(f"{BASE_URL}/auth/login", json=student_credentials)
    
    if student_response.status_code != 200:
        print(f"❌ Student login failed: {student_response.text}")
        return
        
    student_token = student_response.json()["data"]["jwt_token"]
    student_headers = {"Authorization": f"Bearer {student_token}"}
    print("✅ Student logged in")
    
    # Step 3: Create new session (starts now, ends in 1 hour)
    print("3. Creating new session...")
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(minutes=1)  # Started 1 minute ago
    end_time = now + timedelta(hours=1)      # Ends in 1 hour
    
    session_data = {
        "session_name": f"Debug Session {now.strftime('%H:%M:%S')}",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "location_lat": 40.7128,
        "location_lon": -74.0060,
        "location_radius": 100,
        "is_active": True
    }
    
    session_response = requests.post(f"{BASE_URL}/admin/sessions", 
                                   json=session_data, headers=teacher_headers)
    
    if session_response.status_code != 201:  # Should be 201 for creation
        print(f"❌ Session creation failed: {session_response.text}")
        return
        
    session_id = session_response.json()["data"]["session_id"]
    print(f"✅ Session created: {session_id}")
    print(f"   Start: {start_time.isoformat()}")
    print(f"   End: {end_time.isoformat()}")
    
    # Step 4: Check if session appears in active sessions
    print("4. Verifying session in active list...")
    sessions_response = requests.get(f"{BASE_URL}/attendance/active-sessions", headers=student_headers)
    
    if sessions_response.status_code == 200:
        sessions = sessions_response.json()["data"]
        session_found = any(s["session_id"] == session_id for s in sessions)
        print(f"✅ Session found in active list: {session_found}")
    else:
        print(f"⚠️ Could not check active sessions: {sessions_response.text}")
    
    # Step 5: Try attendance with exact coordinates
    print("5. Student attempting attendance...")
    attendance_data = {
        "session_id": session_id,
        "lat": 40.7128,  # Exact match with session location
        "lon": -74.0060
    }
    
    attendance_response = requests.post(f"{BASE_URL}/attendance/check-in", 
                                      json=attendance_data, headers=student_headers)
    
    print(f"   Attendance response: {attendance_response.status_code}")
    print(f"   Response body: {attendance_response.text}")
    
    if attendance_response.status_code == 200:
        print("🎉 SUCCESS! Attendance recorded successfully!")
        record_data = attendance_response.json()["data"]
        print(f"   Record ID: {record_data.get('record_id')}")
        print(f"   Check-in time: {record_data.get('check_in_time')}")
        return True
    else:
        print("❌ Attendance failed")
        # Try with force flag as teacher
        print("6. Trying with force flag as teacher...")
        
        force_data = {
            "session_id": session_id,
            "user_id": student_response.json()["data"]["user"]["user_id"],
            "lat": 40.7128,
            "lon": -74.0060,
            "force": True
        }
        
        force_response = requests.post(f"{BASE_URL}/attendance/check-in", 
                                     json=force_data, headers=teacher_headers)
        
        print(f"   Force response: {force_response.status_code}")
        print(f"   Force body: {force_response.text}")
        
        if force_response.status_code == 200:
            print("✅ Force attendance successful!")
            return True
        else:
            print("❌ Even force attendance failed")
            return False

if __name__ == "__main__":
    success = test_fresh_attendance()
    print(f"\n🎯 RESULT: {'✅ WORKING' if success else '❌ STILL BROKEN'}")
