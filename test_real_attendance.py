#!/usr/bin/env python3
"""
Test attendance flow with real existing credentials
"""
import requests
import json

BASE_URL = "https://attendance-backend-go8h.onrender.com"

# Existing credentials
ADMIN_CREDS = {"email": "psaha21.un@gmail.com", "password": "P21042004p#"}
TEACHER_CREDS = {"email": "alpha@gmail.com", "password": "P21042004p#"}
STUDENT_CREDS = {"email": "beta@gmail.com", "password": "P21042004p#"}

def login_user(credentials, role_name):
    """Login a user and return token and user info"""
    print(f"\n🔐 Logging in {role_name}...")
    
    response = requests.post(f"{BASE_URL}/auth/login", json=credentials)
    if response.status_code != 200:
        print(f"❌ {role_name} login failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None, None
    
    result = response.json()
    token = result["data"]["jwt_token"]
    user = result["data"]["user"]
    
    print(f"✅ {role_name} logged in: {user['name']}")
    print(f"   Organization: {user['org_id']}")
    print(f"   Role: {user['role']}")
    
    return token, user

def get_sessions():
    """Get available sessions"""
    print("\n📋 Getting available sessions...")
    
    response = requests.get(f"{BASE_URL}/attendance/public-sessions")
    if response.status_code != 200:
        print(f"❌ Failed to get sessions: {response.status_code}")
        return []
    
    sessions = response.json()["data"]
    print(f"✅ Found {len(sessions)} sessions")
    
    return sessions

def mark_attendance(token, session_id, user_name):
    """Mark attendance for a session"""
    print(f"\n🎯 {user_name} marking attendance for session...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    attendance_data = {
        "session_id": session_id,
        "lat": 40.7128,
        "lon": -74.0060
    }
    
    response = requests.post(
        f"{BASE_URL}/attendance/check-in", 
        json=attendance_data, 
        headers=headers
    )
    
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ ATTENDANCE MARKED SUCCESSFULLY!")
        print(f"   Record ID: {result['data']['record_id']}")
        print(f"   Check-in time: {result['data']['check_in_time']}")
        return True
    else:
        print(f"❌ Attendance marking failed")
        return False

def test_complete_flow():
    """Test complete attendance flow with existing users"""
    print("🚀 TESTING COMPLETE ATTENDANCE FLOW WITH EXISTING USERS")
    print("=" * 60)
    
    # Step 1: Get sessions
    sessions = get_sessions()
    if not sessions:
        print("❌ No sessions available")
        return False
    
    # Find a session from the same organization as our users
    student_org = "74f8a6e5-296c-4b65-9bb3-6a3c050c3584"  # SAHA organization
    saha_session = None
    
    for session in sessions:
        print(f"Session: {session['session_name']} - Org: {session['org_id']}")
        if session['org_id'] == student_org:
            saha_session = session
            break
    
    if not saha_session:
        print(f"❌ No session found for organization {student_org}")
        # Use any session for now to test
        saha_session = sessions[0]
        print(f"⚠️ Using session from different org for testing")
    
    if not saha_session:
        print("❌ No suitable session found")
        return False
    
    session_id = saha_session["session_id"]
    print(f"\n🎯 Using session: {saha_session['session_name']}")
    print(f"   Session ID: {session_id}")
    print(f"   Organization: {saha_session['org_id']}")
    
    # Step 2: Login student
    student_token, student_user = login_user(STUDENT_CREDS, "STUDENT")
    if not student_token:
        return False
    
    # Step 3: Student marks attendance
    success = mark_attendance(student_token, session_id, "STUDENT")
    
    if success:
        print("\n🎉 COMPLETE ATTENDANCE WORKFLOW: SUCCESS")
        print("✅ Student can see sessions")
        print("✅ Student can login")
        print("✅ Student can mark attendance")
        return True
    else:
        # Try with teacher credentials to debug
        print("\n🔍 Trying with teacher credentials for debugging...")
        teacher_token, teacher_user = login_user(TEACHER_CREDS, "TEACHER")
        if teacher_token:
            teacher_success = mark_attendance(teacher_token, session_id, "TEACHER")
            if teacher_success:
                print("✅ Teacher attendance works - issue might be student permissions")
            else:
                print("❌ Even teacher attendance fails - database issue")
        
        return False

if __name__ == "__main__":
    success = test_complete_flow()
    if not success:
        print("\n❌ ATTENDANCE WORKFLOW HAS ISSUES")
        print("\n🔧 NEXT STEPS:")
        print("1. Check database constraints")
        print("2. Verify organization relationships")
        print("3. Check attendance table structure")
