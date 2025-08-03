#!/usr/bin/env python3
"""
Test script for mark-attendance endpoint with different parameter formats
"""
import requests
import json

# Test configuration
BASE_URL = "http://127.0.0.1:5000"

# Production credentials
CREDENTIALS = {
    'admin': {
        'email': 'psaha21.un@gmail.com',
        'password': 'P21042004p#'
    },
    'teacher': {
        'email': 'alpha@gmail.com', 
        'password': 'P21042004p#'
    },
    'student': {
        'email': 'beta@gmail.com',
        'password': 'P21042004p#'
    }
}

def login_user(role):
    """Login as specified role and return token"""
    print(f"🔐 Logging in as {role}...")
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=CREDENTIALS[role])
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and 'data' in data:
                token = data['data'].get('jwt_token')
                if token:
                    print(f"   ✅ {role.title()} login successful")
                    return token
        
        print(f"   ❌ {role.title()} login failed: {response.text}")
        return None
        
    except Exception as e:
        print(f"   ❌ {role.title()} login error: {str(e)}")
        return None

def create_test_session(admin_token):
    """Create a test session for attendance testing"""
    print("\n📝 Creating test session...")
    
    from datetime import datetime, timedelta
    now = datetime.now()
    start_time = now + timedelta(minutes=5)
    end_time = start_time + timedelta(hours=2)
    
    session_data = {
        "session_name": "Test Session for Attendance",
        "description": "Test session for parameter format testing",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "latitude": 22.6164736,
        "longitude": 88.3785728,
        "radius": 100
    }
    
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/admin/sessions", json=session_data, headers=headers)
        
        if response.status_code == 201:
            result = response.json()
            session_id = result.get('data', {}).get('session_id')
            if session_id:
                print(f"   ✅ Test session created: {session_id}")
                return session_id
        
        print(f"   ❌ Session creation failed: {response.text}")
        return None
        
    except Exception as e:
        print(f"   ❌ Session creation error: {str(e)}")
        return None

def test_mark_attendance_formats(student_token, session_id):
    """Test mark-attendance endpoint with different parameter formats"""
    print("\n📍 Testing Mark Attendance Parameter Formats")
    print("=" * 50)
    
    headers = {
        "Authorization": f"Bearer {student_token}",
        "Content-Type": "application/json"
    }
    
    # Test 1: Frontend format (latitude/longitude)
    print("\n🧪 Test 1: Frontend format (latitude/longitude)")
    payload1 = {
        "latitude": 22.6165,  # Close to session location
        "longitude": 88.3786,
        "session_id": session_id
    }
    
    print(f"📤 Payload: {json.dumps(payload1, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/simple/mark-attendance", json=payload1, headers=headers)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result.get('message')}")
            if 'data' in result:
                data = result['data']
                print(f"   Status: {data.get('status')}")
                print(f"   Distance: {data.get('distance')}m")
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 2: Alternative format (lat/lon) - if your backend supports it
    print("\n🧪 Test 2: Alternative format (lat/lon)")
    payload2 = {
        "lat": 22.6165,  # Close to session location
        "lon": 88.3786,
        "session_id": session_id
    }
    
    print(f"📤 Payload: {json.dumps(payload2, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/simple/mark-attendance", json=payload2, headers=headers)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result.get('message')}")
            if 'data' in result:
                data = result['data']
                print(f"   Status: {data.get('status')}")
                print(f"   Distance: {data.get('distance')}m")
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_attendance_too_far(student_token, session_id):
    """Test attendance marking when location is too far"""
    print("\n🚫 Testing Location Too Far Scenario")
    print("=" * 40)
    
    headers = {
        "Authorization": f"Bearer {student_token}",
        "Content-Type": "application/json"
    }
    
    # Use coordinates that are far from the session location
    payload = {
        "latitude": 40.7128,  # New York coordinates (far from Kolkata)
        "longitude": -74.0060,
        "session_id": session_id
    }
    
    print(f"📤 Payload (far location): {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/simple/mark-attendance", json=payload, headers=headers)
        print(f"📊 Status: {response.status_code}")
        
        result = response.json()
        if response.status_code == 200:
            # Check if it was correctly marked as absent for far location
            status = result.get('data', {}).get('status')
            distance = result.get('data', {}).get('distance')
            
            if status == 'absent':
                print(f"✅ Correctly marked as absent (distance: {distance}m)")
            else:
                print(f"⚠️ Expected 'absent' but got '{status}' (distance: {distance}m)")
        elif response.status_code == 400 and result.get('error_code') == 'LOCATION_TOO_FAR':
            print("✅ Correctly rejected attendance due to distance")
            if 'details' in result:
                details = result['details']
                print(f"   Distance: {details.get('distance')}m")
                print(f"   Max allowed: {details.get('max_allowed')}m")
        else:
            print(f"❌ Unexpected response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    print("🧪 MARK ATTENDANCE ENDPOINT TEST")
    print("=" * 50)
    
    # Check server health
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ Server is not healthy")
            return
    except:
        print("❌ Cannot connect to server")
        return
    
    print("✅ Server is healthy")
    
    # Login users
    admin_token = login_user('admin')
    student_token = login_user('student')
    
    if not admin_token or not student_token:
        print("❌ Cannot proceed without valid tokens")
        return
    
    # Create test session
    session_id = create_test_session(admin_token)
    if not session_id:
        print("❌ Cannot proceed without test session")
        return
    
    # Run tests
    test_mark_attendance_formats(student_token, session_id)
    test_attendance_too_far(student_token, session_id)
    
    print("\n" + "=" * 50)
    print("🏁 Mark attendance endpoint testing complete!")

if __name__ == "__main__":
    main()
