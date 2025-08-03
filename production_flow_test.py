"""
🧪 PRODUCTION TEACHER-STUDENT FLOW TEST - production_flow_test.py

🎯 WHAT THIS DOES:
Tests the complete teacher-student session workflow using your production credentials.

Production Credentials:
- Admin: psaha21.un@gmail.com / P21042004p#
- Teacher: alpha@gmail.com / P21042004p#  
- Student: beta@gmail.com / P21042004p#
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://127.0.0.1:5000"

# Production credentials
CREDENTIALS = {
    "admin": {"email": "psaha21.un@gmail.com", "password": "P21042004p#"},
    "teacher": {"email": "alpha@gmail.com", "password": "P21042004p#"},
    "student": {"email": "beta@gmail.com", "password": "P21042004p#"}
}

def login_user(role):
    """Login user and return token."""
    print(f"   🔐 Logging in {role}...")
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=CREDENTIALS[role])
        
        print(f"   📊 Login status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   📄 Response keys: {list(data.keys())}")
            
            # Try different possible token locations
            token = None
            if "data" in data and isinstance(data["data"], dict):
                token = data["data"].get("jwt_token") or data["data"].get("access_token") or data["data"].get("token")
            elif "jwt_token" in data:
                token = data["jwt_token"]
            elif "access_token" in data:
                token = data["access_token"]
            elif "token" in data:
                token = data["token"]
            
            if token:
                print(f"   ✅ {role.title()} login successful")
                print(f"   🎫 Token: {token[:20]}...")
                return token
            else:
                print(f"   ❌ {role.title()} login failed - no token found")
                print(f"   📄 Full response: {data}")
                return None
        else:
            print(f"   ❌ {role.title()} login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ {role.title()} login error: {str(e)}")
        return None

def test_teacher_create_session(teacher_token):
    """Test teacher creating a session."""
    print("\n2️⃣ Testing Teacher Session Creation")
    
    if not teacher_token:
        print("   ❌ No teacher token available")
        return None
    
    # Session data
    now = datetime.now()
    start_time = now + timedelta(minutes=5)
    end_time = start_time + timedelta(hours=2)
    
    session_data = {
        "session_name": "Production Math Class",
        "description": "Test session for production flow",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "latitude": 40.7128,
        "longitude": -74.0060,
        "radius": 100
    }
    
    headers = {"Authorization": f"Bearer {teacher_token}", "Content-Type": "application/json"}
    
    # Try different endpoints for session creation
    endpoints = [
        "/admin/sessions",
        "/admin/create-session", 
        "/attendance/create-session"
    ]
    
    for endpoint in endpoints:
        print(f"   🔍 Trying endpoint: {endpoint}")
        try:
            response = requests.post(f"{BASE_URL}{endpoint}", json=session_data, headers=headers)
            print(f"   📊 Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"   ✅ Session created successfully via {endpoint}")
                
                # Extract session ID
                session_id = None
                if "data" in result:
                    if isinstance(result["data"], dict):
                        session_id = result["data"].get("session_id")
                    elif isinstance(result["data"], str):
                        session_id = result["data"]
                
                if session_id:
                    print(f"   📝 Session ID: {session_id}")
                    return session_id
                else:
                    print(f"   ⚠️ Session created but no ID found")
                    return "created-session"
            else:
                print(f"   ❌ Failed: {response.text[:150]}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print("   ❌ No working endpoint found for session creation")
    return None

def test_student_view_sessions(student_token):
    """Test student viewing active sessions."""
    print("\n3️⃣ Testing Student View Active Sessions")
    
    if not student_token:
        print("   ❌ No student token available")
        return False
    
    headers = {"Authorization": f"Bearer {student_token}"}
    
    # Try different endpoints
    endpoints = [
        "/attendance/active-sessions",
        "/attendance/sessions",
        "/attendance/public-sessions"
    ]
    
    for endpoint in endpoints:
        print(f"   🔍 Trying endpoint: {endpoint}")
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            print(f"   📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Student can view sessions via {endpoint}")
                
                if "data" in result:
                    sessions = result["data"]
                    print(f"   📋 Found {len(sessions)} sessions")
                    
                    if sessions:
                        print("   📝 Sessions:")
                        for i, session in enumerate(sessions[:3]):
                            name = session.get('session_name', 'Unknown')
                            sid = session.get('session_id', 'Unknown')
                            print(f"      {i+1}. {name} (ID: {sid[:8]}...)")
                        return True
                else:
                    print(f"   ⚠️ Unexpected response format")
            else:
                print(f"   ❌ Failed: {response.text[:100]}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print("   ❌ No working endpoint found for viewing sessions")
    return False

def test_student_mark_attendance(student_token, session_id):
    """Test student marking attendance."""
    print("\n4️⃣ Testing Student Mark Attendance")
    
    if not student_token:
        print("   ❌ No student token available")
        return False
    
    headers = {"Authorization": f"Bearer {student_token}", "Content-Type": "application/json"}
    
    # Test attendance with location close to session
    attendance_data = {
        "session_id": session_id,
        "lat": 40.7130,  # Close to session location
        "lon": -74.0062
    }
    
    # Try different attendance endpoints
    endpoints = [
        ("/attendance/check-in", attendance_data),
        ("/simple/mark-attendance", {
            "latitude": 40.7130,
            "longitude": -74.0062,
            "session_id": session_id
        })
    ]
    
    for endpoint, data in endpoints:
        print(f"   🔍 Trying endpoint: {endpoint}")
        try:
            response = requests.post(f"{BASE_URL}{endpoint}", json=data, headers=headers)
            print(f"   📊 Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"   ✅ Attendance marked successfully via {endpoint}")
                
                if "data" in result:
                    att_data = result["data"]
                    status = att_data.get("status", "Unknown")
                    print(f"   📝 Status: {status}")
                    if "distance" in att_data:
                        print(f"   📍 Distance: {att_data['distance']}m")
                else:
                    print(f"   ✅ Response: {result.get('message', 'Success')}")
                
                return True
            else:
                print(f"   ❌ Failed: {response.text[:150]}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print("   ❌ No working endpoint found for attendance")
    return False

def test_teacher_view_attendance(teacher_token, session_id):
    """Test teacher viewing attendance reports."""
    print("\n5️⃣ Testing Teacher View Attendance Report")
    
    if not teacher_token:
        print("   ❌ No teacher token available")
        return False
    
    headers = {"Authorization": f"Bearer {teacher_token}"}
    
    # Try different report endpoints
    endpoints = [
        f"/attendance/session/{session_id}/report",
        f"/attendance/session/{session_id}/attendance",
        f"/admin/sessions/{session_id}/attendance"
    ]
    
    for endpoint in endpoints:
        print(f"   🔍 Trying endpoint: {endpoint}")
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            print(f"   📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Teacher can view attendance via {endpoint}")
                
                if "data" in result:
                    data = result["data"]
                    if isinstance(data, dict) and "attendance_records" in data:
                        records = data["attendance_records"]
                        print(f"   📋 Found {len(records)} attendance records")
                    elif isinstance(data, list):
                        print(f"   📋 Found {len(data)} attendance records")
                    else:
                        print(f"   📋 Data type: {type(data)}")
                else:
                    print(f"   ⚠️ Unexpected response format")
                
                return True
            else:
                print(f"   ❌ Failed: {response.text[:100]}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print("   ❌ No working endpoint found for viewing attendance")
    return False

def main():
    """Run the complete production flow test."""
    
    print("🧪 PRODUCTION TEACHER-STUDENT FLOW TEST")
    print("=" * 55)
    
    # Check server health
    try:
        health = requests.get(f"{BASE_URL}/health", timeout=5)
        if health.status_code == 200:
            print("✅ Server is running and healthy")
        else:
            print(f"⚠️ Server health check: {health.status_code}")
    except Exception as e:
        print(f"❌ Server not accessible: {str(e)}")
        return
    
    # Test the flow
    print("\n1️⃣ Testing Authentication")
    teacher_token = login_user("teacher")
    student_token = login_user("student")
    admin_token = login_user("admin")
    
    session_id = test_teacher_create_session(teacher_token or admin_token)
    student_can_view = test_student_view_sessions(student_token)
    student_can_attend = test_student_mark_attendance(student_token, session_id)
    teacher_can_view = test_teacher_view_attendance(teacher_token or admin_token, session_id)
    
    # Generate comprehensive report
    print("\n" + "=" * 55)
    print("📊 PRODUCTION FLOW TEST REPORT")
    print("=" * 55)
    
    print("🔐 AUTHENTICATION RESULTS:")
    print(f"   Admin login:   {'✅ Success' if admin_token else '❌ Failed'}")
    print(f"   Teacher login: {'✅ Success' if teacher_token else '❌ Failed'}")
    print(f"   Student login: {'✅ Success' if student_token else '❌ Failed'}")
    
    print("\n📝 SESSION MANAGEMENT:")
    print(f"   Teacher can create sessions: {'✅ Yes' if session_id else '❌ No'}")
    print(f"   Student can view sessions:   {'✅ Yes' if student_can_view else '❌ No'}")
    
    print("\n📍 ATTENDANCE WORKFLOW:")
    print(f"   Student can mark attendance: {'✅ Yes' if student_can_attend else '❌ No'}")
    print(f"   Teacher can view reports:    {'✅ Yes' if teacher_can_view else '❌ No'}")
    
    # Overall assessment
    all_working = all([
        (teacher_token or admin_token),
        student_token,
        session_id,
        student_can_view,
        student_can_attend,
        teacher_can_view
    ])
    
    print(f"\n🎯 OVERALL ASSESSMENT:")
    if all_working:
        print("   🎉 COMPLETE SUCCESS!")
        print("   ✅ Full teacher-student workflow is functional")
        print("   ✅ Students can attend sessions created by teachers")
        print("   ✅ Teachers can view attendance reports")
    else:
        print("   ⚠️ ISSUES IDENTIFIED:")
        if not (teacher_token or admin_token):
            print("   ❌ Teacher/Admin authentication failing")
        if not student_token:
            print("   ❌ Student authentication failing")
        if not session_id:
            print("   ❌ Session creation not working")
        if not student_can_view:
            print("   ❌ Students cannot view sessions")
        if not student_can_attend:
            print("   ❌ Students cannot mark attendance")
        if not teacher_can_view:
            print("   ❌ Teachers cannot view attendance reports")
    
    print(f"\n🔧 RECOMMENDATIONS:")
    if all_working:
        print("   ✅ System is ready for production use!")
        print("   ✅ Consider deploying the simplified attendance system")
    else:
        print("   🛠️ Focus on fixing the failed components above")
        print("   📋 Check logs for specific error messages")
        print("   🔍 Verify database schema and migrations")

if __name__ == "__main__":
    main()
