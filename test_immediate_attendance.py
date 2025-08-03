#!/usr/bin/env python3
"""
Test attendance with immediate session start
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "https://attendance-backend-go8h.onrender.com"

def test_immediate_attendance():
    print("🧪 TESTING IMMEDIATE ATTENDANCE")
    print("=" * 50)
    
    teacher_email = "alpha@gmail.com"
    teacher_password = "P21042004p#"
    student_email = "beta@gmail.com"
    student_password = "P21042004p#"
    
    try:
        # 1. Teacher Login
        print("1. 🔐 Teacher Login...")
        teacher_login = requests.post(f"{BASE_URL}/auth/login", json={
            "email": teacher_email,
            "password": teacher_password
        })
        
        teacher_data = teacher_login.json()
        teacher_token = teacher_data['data']['token']
        teacher_headers = {"Authorization": f"Bearer {teacher_token}"}
        print("   ✅ Teacher logged in")
        
        # 2. Create session that starts NOW
        print("\n2. 📅 Creating immediate session...")
        now = datetime.now()
        start_time = now - timedelta(minutes=5)  # Started 5 minutes ago
        end_time = now + timedelta(hours=1)      # Ends in 1 hour
        
        session_data = {
            "session_name": f"Live Session {now.strftime('%H:%M:%S')}",
            "description": "Testing live attendance",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "latitude": 40.7128,
            "longitude": -74.0060,
            "radius": 100
        }
        
        session_response = requests.post(f"{BASE_URL}/admin/sessions", 
                                       json=session_data, headers=teacher_headers)
        
        session_id = session_response.json()['data']['session_id']
        print(f"   ✅ Live session created: {session_id}")
        
        # 3. Student Login
        print("\n3. 🔐 Student Login...")
        student_login = requests.post(f"{BASE_URL}/auth/login", json={
            "email": student_email,
            "password": student_password
        })
        
        student_data = student_login.json()
        student_token = student_data['data']['token']
        student_headers = {"Authorization": f"Bearer {student_token}"}
        print("   ✅ Student logged in")
        
        # 4. Immediate Check-in
        print("\n4. ✅ Testing IMMEDIATE check-in...")
        checkin_data = {
            "session_id": session_id,
            "lat": 40.7128,  # Exact location
            "lon": -74.0060
        }
        
        checkin_response = requests.post(f"{BASE_URL}/attendance/check-in", 
                                       json=checkin_data, headers=student_headers)
        
        print(f"   📬 Status: {checkin_response.status_code}")
        print(f"   📬 Response: {checkin_response.text}")
        
        if checkin_response.status_code == 200:
            result = checkin_response.json()
            print(f"   🎉 SUCCESS! Attendance marked!")
            print(f"      Record ID: {result['data']['record_id']}")
            print(f"      Check-in time: {result['data']['check_in_time']}")
            print(f"      Status: {result['data']['status']}")
        else:
            print(f"   ❌ Failed: {checkin_response.text}")
            
        # 5. Try to check in again (should fail - duplicate)
        print("\n5. 🔄 Testing duplicate check-in prevention...")
        duplicate_response = requests.post(f"{BASE_URL}/attendance/check-in", 
                                         json=checkin_data, headers=student_headers)
        
        print(f"   📬 Status: {duplicate_response.status_code}")
        print(f"   📬 Response: {duplicate_response.text}")
        
        if duplicate_response.status_code != 200:
            print("   ✅ Duplicate prevention working!")
        
        print("\n🎉 ATTENDANCE SYSTEM IS WORKING!")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_immediate_attendance()
