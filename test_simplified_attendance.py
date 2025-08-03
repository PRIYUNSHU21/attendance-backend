"""
🧪 TEST SIMPLIFIED ATTENDANCE SYSTEM
Test the new simplified system based on friend's working patterns
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "https://attendance-backend-go8h.onrender.com"
# BASE_URL = "http://127.0.0.1:5000"  # For local testing

def test_simplified_attendance():
    """Test the simplified attendance system that mimics friend's approach."""
    
    print("🧪 TESTING SIMPLIFIED ATTENDANCE SYSTEM")
    print("=" * 50)
    
    # Test credentials - TEACHER AND STUDENT
    teacher_email = "alpha@gmail.com"
    teacher_password = "P21042004p#"
    
    student_email = "beta@gmail.com"
    student_password = "P21042004p#"
    
    try:
        # 1. TEACHER LOGIN FIRST
        print("1. 🔐 Testing Teacher Login...")
        login_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": teacher_email,
            "password": teacher_password
        })
        
        if login_response.status_code != 200:
            print(f"   ❌ Login failed: {login_response.text}")
            return
        
        login_data = login_response.json()
        teacher_token = login_data['data']['token']
        teacher_user_id = login_data['data']['user']['user_id']
        org_id = login_data['data']['user']['org_id']
        
        print(f"   ✅ Teacher login successful! User ID: {teacher_user_id}")
        
        teacher_headers = {"Authorization": f"Bearer {teacher_token}"}
        
        # 2. CREATE A SIMPLE SESSION (using admin route)
        print("\n2. 📅 Creating test session...")
        now = datetime.now()
        start_time = now + timedelta(minutes=1)
        end_time = start_time + timedelta(hours=1)
        
        session_data = {
            "session_name": f"Simple Test Session {now.strftime('%H:%M:%S')}",
            "description": "Testing simplified attendance",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "latitude": 40.7128,
            "longitude": -74.0060,
            "radius": 100
        }
        
        session_response = requests.post(f"{BASE_URL}/admin/sessions", 
                                       json=session_data, headers=teacher_headers)
        
        if session_response.status_code != 201:
            print(f"   ❌ Session creation failed: {session_response.text}")
            return
        
        session_id = session_response.json()['data']['session_id']
        print(f"   ✅ Session created! ID: {session_id}")
        
        # 3. STUDENT LOGIN
        print("\n3. 🔐 Student Login...")
        student_login_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": student_email,
            "password": student_password
        })
        
        if student_login_response.status_code != 200:
            print(f"   ❌ Student login failed: {student_login_response.text}")
            return
        
        student_data = student_login_response.json()
        student_token = student_data['data']['token']
        student_user_id = student_data['data']['user']['user_id']
        student_headers = {"Authorization": f"Bearer {student_token}"}
        
        print(f"   ✅ Student login successful! User ID: {student_user_id}")
        
        # 4. TEST SIMPLIFIED CHECK-IN
        print("\n4. ✅ Testing simplified check-in...")
        checkin_data = {
            "session_id": session_id,
            "lat": 40.7128,  # Within geofence
            "lon": -74.0060
        }
        
        checkin_response = requests.post(f"{BASE_URL}/attendance/check-in", 
                                       json=checkin_data, headers=student_headers)
        
        print(f"   📡 Request: POST {BASE_URL}/attendance/check-in")
        print(f"   📨 Data: {json.dumps(checkin_data, indent=2)}")
        print(f"   📬 Status: {checkin_response.status_code}")
        print(f"   📬 Response: {checkin_response.text}")
        
        if checkin_response.status_code == 200:
            checkin_result = checkin_response.json()
            print(f"   ✅ Check-in successful!")
            print(f"      Response: {checkin_result}")
        else:
            print(f"   ❌ Check-in failed: {checkin_response.text}")
        
        print("\n🎉 ATTENDANCE TEST COMPLETE!")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")

if __name__ == "__main__":
    test_simplified_attendance()
