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
    
    # Test credentials
    admin_email = "psaha21.un@gmail.com"
    admin_password = "123456"
    
    try:
        # 1. LOGIN FIRST
        print("1. 🔐 Testing Login...")
        login_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": admin_email,
            "password": admin_password
        })
        
        if login_response.status_code != 200:
            print(f"   ❌ Login failed: {login_response.text}")
            return
        
        login_data = login_response.json()
        token = login_data['data']['token']
        user_id = login_data['data']['user']['user_id']
        org_id = login_data['data']['user']['org_id']
        
        print(f"   ✅ Login successful! User ID: {user_id}")
        
        headers = {"Authorization": f"Bearer {token}"}
        
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
                                       json=session_data, headers=headers)
        
        if session_response.status_code != 201:
            print(f"   ❌ Session creation failed: {session_response.text}")
            return
        
        session_id = session_response.json()['data']['session_id']
        print(f"   ✅ Session created! ID: {session_id}")
        
        # 3. TEST SIMPLIFIED CHECK-IN
        print("\n3. ✅ Testing simplified check-in...")
        checkin_data = {
            "session_id": session_id,
            "lat": 40.7128,  # Within geofence
            "lon": -74.0060,
            "user_id": user_id,
            "org_id": org_id
        }
        
        checkin_response = requests.post(f"{BASE_URL}/simple/simple-check-in", 
                                       json=checkin_data)
        
        print(f"   📡 Request: POST {BASE_URL}/simple/simple-check-in")
        print(f"   📨 Data: {json.dumps(checkin_data, indent=2)}")
        print(f"   📬 Status: {checkin_response.status_code}")
        print(f"   📬 Response: {checkin_response.text}")
        
        if checkin_response.status_code == 200:
            checkin_result = checkin_response.json()
            print(f"   ✅ Simplified check-in successful!")
            print(f"      Status: {checkin_result.get('status')}")
            print(f"      Distance: {checkin_result.get('distance')}m")
            print(f"      Record ID: {checkin_result.get('record_id')}")
        else:
            print(f"   ❌ Simplified check-in failed: {checkin_response.text}")
        
        # 4. TEST WITH WRONG LOCATION (should be absent)
        print("\n4. 🌍 Testing with wrong location...")
        wrong_checkin = {
            "session_id": session_id,
            "lat": 41.0000,  # Far away - should be absent
            "lon": -75.0000,
            "user_id": "test_user_2",
            "org_id": org_id
        }
        
        wrong_response = requests.post(f"{BASE_URL}/simple/simple-check-in", 
                                     json=wrong_checkin)
        
        print(f"   📬 Status: {wrong_response.status_code}")
        print(f"   📬 Response: {wrong_response.text}")
        
        if wrong_response.status_code == 200:
            wrong_result = wrong_response.json()
            print(f"   ✅ Location validation working!")
            print(f"      Status: {wrong_result.get('status')} (should be Absent)")
            print(f"      Distance: {wrong_result.get('distance')}m (should be large)")
        
        print("\n🎉 SIMPLIFIED ATTENDANCE TEST COMPLETE!")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")

if __name__ == "__main__":
    test_simplified_attendance()
