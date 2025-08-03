#!/usr/bin/env python3
"""
Debug attendance record creation
"""
import requests
import json
from datetime import datetime, timezone, timedelta

BASE_URL = "https://attendance-backend-go8h.onrender.com"

def debug_attendance():
    print("🔍 DEBUGGING ATTENDANCE RECORD CREATION")
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
    
    print(f"Teacher response: {teacher_response.json()}")
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
    
    # Step 3: Get active sessions
    print("3. Checking active sessions...")
    sessions_response = requests.get(f"{BASE_URL}/attendance/active-sessions", headers=student_headers)
    
    if sessions_response.status_code != 200:
        print(f"❌ Failed to get sessions: {sessions_response.text}")
        return
        
    sessions = sessions_response.json()["data"]
    print(f"✅ Found {len(sessions)} active sessions")
    
    if not sessions:
        print("❌ No active sessions found")
        return
        
    # Use the first active session
    session = sessions[0]
    session_id = session["session_id"]
    print(f"   Using session: {session['session_name']} (ID: {session_id})")
    
    # Step 4: Check attendance table schema
    print("4. Checking attendance records table schema...")
    schema_response = requests.get(f"{BASE_URL}/migration/check-attendance-records-schema", headers=teacher_headers)
    
    if schema_response.status_code == 200:
        schema_data = schema_response.json()["data"]
        print("✅ Schema check successful:")
        print(f"   Table exists: {schema_data.get('table_exists')}")
        print(f"   Columns: {schema_data.get('columns')}")
    else:
        print(f"⚠️ Schema check failed: {schema_response.text}")
    
    # Step 5: Try attendance with force flag
    print("5. Attempting attendance with force flag...")
    force_data = {
        "session_id": session_id,
        "lat": 40.7128,
        "lon": -74.0060,
        "force": True
    }
    
    force_response = requests.post(f"{BASE_URL}/attendance/check-in", 
                                 json=force_data, headers=teacher_headers)
    
    print(f"   Force attendance response: {force_response.status_code}")
    print(f"   Response body: {force_response.text}")
    
    if force_response.status_code == 200:
        print("✅ Force attendance successful!")
        return
    
    # Step 6: Try regular attendance
    print("6. Attempting regular attendance...")
    regular_data = {
        "session_id": session_id,
        "lat": 40.7128,
        "lon": -74.0060
    }
    
    regular_response = requests.post(f"{BASE_URL}/attendance/check-in", 
                                   json=regular_data, headers=student_headers)
    
    print(f"   Regular attendance response: {regular_response.status_code}")
    print(f"   Response body: {regular_response.text}")
    
    if regular_response.status_code == 200:
        print("✅ Regular attendance successful!")
    else:
        print("❌ Regular attendance failed")
        
        # Step 7: Check if it's a database error by examining the logs
        print("7. Checking server logs...")
        # Try to get more details from error response
        try:
            error_data = regular_response.json()
            print(f"   Error details: {json.dumps(error_data, indent=2)}")
        except:
            print(f"   Raw error response: {regular_response.text}")

if __name__ == "__main__":
    debug_attendance()
