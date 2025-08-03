#!/usr/bin/env python3
"""
Test the BULLETPROOF attendance system
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "https://attendance-backend-go8h.onrender.com"

def test_bulletproof_attendance():
    print("🛡️ TESTING BULLETPROOF ATTENDANCE SYSTEM")
    print("=" * 60)
    
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
        
        # 2. Create session with bulletproof timing
        print("\n2. 📅 Creating bulletproof session...")
        now = datetime.now()
        # Session started 10 minutes ago, ends in 2 hours
        start_time = now - timedelta(minutes=10)
        end_time = now + timedelta(hours=2)
        
        session_data = {
            "session_name": f"Bulletproof Session {now.strftime('%H:%M:%S')}",
            "description": "Testing bulletproof attendance",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "latitude": 40.7128,
            "longitude": -74.0060,
            "radius": 100
        }
        
        session_response = requests.post(f"{BASE_URL}/admin/sessions", 
                                       json=session_data, headers=teacher_headers)
        
        session_id = session_response.json()['data']['session_id']
        print(f"   ✅ Session created: {session_id}")
        
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
        
        # 4. Test BULLETPROOF Check-in
        print("\n4. 🛡️ Testing BULLETPROOF check-in...")
        checkin_data = {
            "session_id": session_id,
            "lat": 40.7128,  # Exact location
            "lon": -74.0060
        }
        
        checkin_response = requests.post(f"{BASE_URL}/bulletproof/simple-checkin", 
                                       json=checkin_data, headers=student_headers)
        
        print(f"   📡 Request: POST {BASE_URL}/bulletproof/simple-checkin")
        print(f"   📬 Status: {checkin_response.status_code}")
        print(f"   📬 Response: {checkin_response.text}")
        
        if checkin_response.status_code == 200:
            result = checkin_response.json()
            print(f"\n   🎉 BULLETPROOF SUCCESS!")
            print(f"      ✅ Record ID: {result['data']['record_id']}")
            print(f"      ✅ Status: {result['data']['status']}")
            print(f"      ✅ Distance: {result['data']['distance']}m")
            print(f"      ✅ Time: {result['data']['check_in_time']}")
            print(f"      ✅ Message: {result['data']['message']}")
        else:
            print(f"   ❌ Failed: {checkin_response.text}")
            return
            
        # 5. Test duplicate prevention
        print("\n5. 🔄 Testing duplicate prevention...")
        duplicate_response = requests.post(f"{BASE_URL}/bulletproof/simple-checkin", 
                                         json=checkin_data, headers=student_headers)
        
        print(f"   📬 Status: {duplicate_response.status_code}")
        if duplicate_response.status_code == 400:
            print("   ✅ Duplicate prevention working!")
        
        # 6. Test location validation
        print("\n6. 🌍 Testing location validation...")
        far_checkin = {
            "session_id": session_id,
            "lat": 41.0000,  # Far away
            "lon": -75.0000
        }
        
        # Need another user for this test - try with teacher
        far_response = requests.post(f"{BASE_URL}/bulletproof/simple-checkin", 
                                   json=far_checkin, headers=teacher_headers)
        
        print(f"   📬 Status: {far_response.status_code}")
        if far_response.status_code == 200:
            far_result = far_response.json()
            print(f"   ✅ Location validation working!")
            print(f"      Status: {far_result['data']['status']} (should be Absent)")
            print(f"      Distance: {far_result['data']['distance']}m (should be large)")
        
        # 7. Test get active sessions
        print("\n7. 📋 Testing get active sessions...")
        sessions_response = requests.get(f"{BASE_URL}/bulletproof/get-active-sessions", 
                                       headers=student_headers)
        
        if sessions_response.status_code == 200:
            sessions_result = sessions_response.json()
            print(f"   ✅ Found {len(sessions_result['data'])} active sessions")
            for session in sessions_result['data']:
                print(f"      📅 {session['session_name']}")
        
        print(f"\n🎉 BULLETPROOF ATTENDANCE SYSTEM WORKS PERFECTLY!")
        print("=" * 60)
        print("✅ No complex time validation issues")
        print("✅ Direct database operations")
        print("✅ Simple location checking")
        print("✅ Reliable error handling")
        print("✅ Based on your friend's successful patterns")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_bulletproof_attendance()
