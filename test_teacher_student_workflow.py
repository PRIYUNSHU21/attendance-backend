#!/usr/bin/env python3
"""
Test attendance workflow: Teacher creates session, student marks attendance
"""
import requests
from datetime import datetime, timezone, timedelta
import time

BASE_URL = "https://attendance-backend-go8h.onrender.com"

def test_attendance_workflow():
    print("👨‍🏫 TEACHER-STUDENT ATTENDANCE TEST")
    print("=" * 40)
    
    # Step 1: Login as teacher
    print("1. Teacher login...")
    teacher_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "alpha@gmail.com", 
        "password": "P21042004p#"
    })
    
    if teacher_response.status_code != 200:
        print(f"❌ Teacher login failed: {teacher_response.text}")
        return False
    
    teacher_token = teacher_response.json()["data"]["jwt_token"]
    teacher_headers = {"Authorization": f"Bearer {teacher_token}", "Content-Type": "application/json"}
    print("✅ Teacher logged in successfully")
    
    # Step 2: Create session that starts in 1 minute, lasts 1 hour
    print("\n2. Creating session (starts in 1 minute, lasts 1 hour)...")
    now_utc = datetime.now(timezone.utc)
    start_time = now_utc + timedelta(minutes=1)  # Starts in 1 minute
    end_time = start_time + timedelta(hours=1)   # Lasts 1 hour
    
    session_data = {
        "session_name": f"Teacher Session {now_utc.strftime('%H%M%S')}",
        "description": "Teacher-created session for student attendance test",
        "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
        "end_time": end_time.strftime("%Y-%m-%dT%H:%M:%S")
    }
    
    print(f"   Start time: {session_data['start_time']}")
    print(f"   End time: {session_data['end_time']}")
    
    session_response = requests.post(f"{BASE_URL}/admin/sessions", json=session_data, headers=teacher_headers)
    
    if session_response.status_code != 201:
        print(f"❌ Session creation failed: {session_response.text}")
        return False
    
    session = session_response.json()["data"]
    session_id = session['session_id']
    print(f"✅ Session created: {session['session_name']}")
    print(f"   Session ID: {session_id}")
    
    # Step 3: Login as student
    print("\n3. Student login...")
    student_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "beta@gmail.com", 
        "password": "P21042004p#"
    })
    
    if student_response.status_code != 200:
        print(f"❌ Student login failed: {student_response.text}")
        return False
    
    student_token = student_response.json()["data"]["jwt_token"]
    student_headers = {"Authorization": f"Bearer {student_token}"}
    print("✅ Student logged in successfully")
    
    # Step 4: Wait for session to start (1 minute + 10 seconds buffer)
    print("\n4. Waiting for session to start (70 seconds)...")
    print("   Session will start in:", end=" ", flush=True)
    for i in range(70, 0, -1):
        print(f"{i}s", end="..." if i > 1 else "\n", flush=True)
        time.sleep(1)
    
    print("🕐 Session should now be active!")
    
    # Step 5: Student marks attendance
    print("\n5. Student marking attendance...")
    attendance_data = {
        "session_id": session_id,
        "lat": 40.7128,
        "lon": -74.0060
    }
    
    attendance_response = requests.post(f"{BASE_URL}/attendance/check-in", 
                                      json=attendance_data, headers=student_headers)
    
    print(f"   Attendance response: {attendance_response.status_code}")
    print(f"   Response body: {attendance_response.text}")
    
    if attendance_response.status_code == 200:
        print("🎉 SUCCESS! Student attendance recorded successfully!")
        attendance_data = attendance_response.json()["data"]
        print(f"   Record ID: {attendance_data.get('record_id')}")
        print(f"   Check-in time: {attendance_data.get('check_in_time')}")
        return True
    else:
        print("❌ FAILED! Student attendance could not be recorded")
        return False

if __name__ == "__main__":
    success = test_attendance_workflow()
    print(f"\n🎯 ATTENDANCE WORKFLOW: {'✅ WORKING' if success else '❌ BROKEN'}")
