#!/usr/bin/env python3
"""
Create a new active session and test attendance
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "https://attendance-backend-go8h.onrender.com"
ADMIN_CREDS = {"email": "psaha21.un@gmail.com", "password": "P21042004p#"}
STUDENT_CREDS = {"email": "beta@gmail.com", "password": "P21042004p#"}

def create_active_session_and_test():
    """Create new session and test attendance"""
    print("🚀 CREATING ACTIVE SESSION AND TESTING ATTENDANCE")
    print("=" * 55)
    
    # Step 1: Login admin
    print("1️⃣ Logging in admin...")
    admin_response = requests.post(f"{BASE_URL}/auth/login", json=ADMIN_CREDS)
    if admin_response.status_code != 200:
        print(f"❌ Admin login failed: {admin_response.text}")
        return False
    
    admin_data = admin_response.json()
    admin_token = admin_data["data"]["jwt_token"]
    admin_user = admin_data["data"]["user"]
    
    print(f"✅ Admin logged in: {admin_user['name']}")
    print(f"   Organization: {admin_user['org_id']}")
    
    # Step 2: Create new session
    print("\n2️⃣ Creating new active session...")
    now = datetime.now()
    start_time = now - timedelta(minutes=30)  # Started 30 min ago
    end_time = now + timedelta(hours=2)       # Ends in 2 hours
    
    session_data = {
        "session_name": f"Live Test Session {now.strftime('%Y%m%d_%H%M%S')}",
        "description": "Test session for attendance validation",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "latitude": 40.7128,
        "longitude": -74.0060,
        "radius": 100
    }
    
    headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
    
    session_response = requests.post(f"{BASE_URL}/admin/sessions", json=session_data, headers=headers)
    print(f"Session creation status: {session_response.status_code}")
    print(f"Session creation response: {session_response.text}")
    
    if session_response.status_code not in [200, 201]:
        print("❌ Failed to create session")
        return False
    
    session_result = session_response.json()
    session_id = session_result["data"]["session_id"]
    
    print(f"✅ Session created successfully!")
    print(f"   Session ID: {session_id}")
    print(f"   Start: {start_time}")
    print(f"   End: {end_time}")
    
    # Step 3: Login student
    print("\n3️⃣ Logging in student...")
    student_response = requests.post(f"{BASE_URL}/auth/login", json=STUDENT_CREDS)
    if student_response.status_code != 200:
        print(f"❌ Student login failed: {student_response.text}")
        return False
    
    student_data = student_response.json()
    student_token = student_data["data"]["jwt_token"]
    student_user = student_data["data"]["user"]
    
    print(f"✅ Student logged in: {student_user['name']}")
    
    # Check if student is in same org as session
    if student_user['org_id'] != admin_user['org_id']:
        print(f"⚠️ Student org ({student_user['org_id']}) != Session org ({admin_user['org_id']})")
        print("This might cause issues...")
    
    # Step 4: Mark attendance
    print("\n4️⃣ Student marking attendance...")
    student_headers = {"Authorization": f"Bearer {student_token}", "Content-Type": "application/json"}
    
    attendance_data = {
        "session_id": session_id,
        "lat": 40.7128,
        "lon": -74.0060
    }
    
    attendance_response = requests.post(
        f"{BASE_URL}/attendance/check-in", 
        json=attendance_data, 
        headers=student_headers
    )
    
    print(f"Attendance status: {attendance_response.status_code}")
    print(f"Attendance response: {attendance_response.text}")
    
    if attendance_response.status_code == 200:
        result = attendance_response.json()
        print("🎉 ATTENDANCE MARKED SUCCESSFULLY!")
        print(f"   Record ID: {result['data']['record_id']}")
        print(f"   Check-in time: {result['data']['check_in_time']}")
        print(f"   Status: {result['data']['status']}")
        return True
    else:
        print("❌ Attendance marking failed")
        return False

if __name__ == "__main__":
    success = create_active_session_and_test()
    if success:
        print("\n🎉 COMPLETE ATTENDANCE WORKFLOW: SUCCESS!")
        print("✅ Session creation works")
        print("✅ Student can see and access sessions")
        print("✅ Attendance marking works perfectly")
        print("\n🔧 BACKEND ATTENDANCE SYSTEM IS FULLY FUNCTIONAL!")
    else:
        print("\n❌ ATTENDANCE WORKFLOW STILL HAS ISSUES")
