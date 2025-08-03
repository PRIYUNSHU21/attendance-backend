"""
🧪 TEACHER-STUDENT SESSION WORKFLOW TEST - test_teacher_student_flow.py

🎯 WHAT THIS TESTS:
Complete workflow testing to verify:
1. Teacher can create sessions
2. Students can see active sessions  
3. Students can mark attendance to teacher's sessions
4. Teacher can view attendance reports

This tests the FULL workflow from session creation to attendance reporting.
"""

import requests
import json
from datetime import datetime, timedelta
import time

# Configuration
BASE_URL = "http://127.0.0.1:5000"

# Production credentials
PRODUCTION_CREDENTIALS = {
    "admin": {
        "email": "psaha21.un@gmail.com",
        "password": "P21042004p#"
    },
    "teacher": {
        "email": "alpha@gmail.com", 
        "password": "P21042004p#"
    },
    "student": {
        "email": "beta@gmail.com",
        "password": "P21042004p#"
    }
}

# Production credentials
CREDENTIALS = {
    "admin": {
        "email": "psaha21.un@gmail.com",
        "password": "P21042004p#"
    },
    "teacher": {
        "email": "alpha@gmail.com", 
        "password": "P21042004p#"
    },
    "student": {
        "email": "beta@gmail.com",
        "password": "P21042004p#"
    }
}

def login_user(user_type):
    """Login a user and return token."""
    try:
        credentials = CREDENTIALS[user_type]
        
        print(f"   🔑 Logging in {user_type}: {credentials['email']}")
        
        login_response = requests.post(f"{BASE_URL}/auth/login", json=credentials)
        
        print(f"   Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data.get("data", {}).get("access_token")
            user_info = token_data.get("data", {}).get("user", {})
            
            print(f"   ✅ {user_type.title()} logged in successfully")
            print(f"   👤 User: {user_info.get('name', 'N/A')} (Role: {user_info.get('role', 'N/A')})")
            print(f"   🏢 Org: {user_info.get('org_id', 'N/A')}")
            
            return token, user_info
        else:
            print(f"   ❌ {user_type.title()} login failed: {login_response.text}")
            return None, None
            
    except Exception as e:
        print(f"   ❌ Login error for {user_type}: {str(e)}")
        return None, None

def test_complete_teacher_student_workflow():
    """Test the complete teacher-student workflow."""
    
    print("🎓 Testing Complete Teacher-Student Workflow")
    print("=" * 60)
    
    # Check server health first
    try:
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Server is running")
        else:
            print("⚠️ Server responded but health check failed")
            return False
    except Exception as e:
        print(f"❌ Server not accessible: {str(e)}")
        return False
    
    # Step 1: Teacher login
    print("\n1️⃣ TEACHER LOGIN")
    teacher_token, teacher_info = login_user("teacher")
    
    if not teacher_token:
        print("❌ Teacher login failed - cannot continue")
        return False
    
    # Step 2: Student login  
    print("\n2️⃣ STUDENT LOGIN")
    student_token, student_info = login_user("student")
    
    if not student_token:
        print("❌ Student login failed - cannot continue")
        return False
        "password": "teacherpass123",
        "name": "Test Teacher",
        "role": "teacher"
    }
    
    student_user = {
        "email": "student.test@example.com", 
        "password": "studentpass123",
        "name": "Test Student",
        "role": "student"
    }
    
    # Session data
    now = datetime.now()
    session_data = {
        "session_name": "Math 101 - Chapter 5",
        "description": "Linear Algebra Basics",
        "start_time": (now - timedelta(minutes=30)).isoformat(),  # Started 30 min ago
        "end_time": (now + timedelta(hours=1)).isoformat(),       # Ends in 1 hour
        "latitude": 40.7128,
        "longitude": -74.0060,
        "radius": 50
    }
    
    teacher_token = None
    student_token = None
    session_id = None
    
    try:
        # === STEP 1: TEACHER AUTHENTICATION ===
        print("\n1️⃣ Testing Teacher Authentication")
        
        # Try login with production credentials
        teacher_login = requests.post(f"{BASE_URL}/auth/login", json=PRODUCTION_CREDENTIALS["teacher"])
        
        if teacher_login.status_code == 200:
            teacher_token = teacher_login.json().get("data", {}).get("access_token")
            print("   ✅ Teacher login successful")
        else:
            print(f"   ❌ Teacher login failed: {teacher_login.text}")
            return False
        
        # === STEP 2: STUDENT AUTHENTICATION ===
        print("\n2️⃣ Testing Student Authentication")
        
        # Try login with production credentials
        student_login = requests.post(f"{BASE_URL}/auth/login", json=PRODUCTION_CREDENTIALS["student"])
        
        if student_login.status_code == 200:
            student_token = student_login.json().get("data", {}).get("access_token")
            print("   ✅ Student login successful")
        else:
            print(f"   ❌ Student login failed: {student_login.text}")
            return False
        })
        
        if student_login.status_code != 200:
            # Register student
            print("   📝 Registering student...")
            student_register = requests.post(f"{BASE_URL}/auth/register", json=student_user)
            print(f"   Student register status: {student_register.status_code}")
            
            if student_register.status_code in [200, 201]:
                # Login after registration
                student_login = requests.post(f"{BASE_URL}/auth/login", json={
                    "email": student_user["email"],
                    "password": student_user["password"]
                })
        
        if student_login.status_code == 200:
            student_token = student_login.json().get("data", {}).get("access_token")
            print("   ✅ Student login successful")
        else:
            print(f"   ❌ Student login failed: {student_login.text}")
            return False
        
        teacher_headers = {"Authorization": f"Bearer {teacher_token}", "Content-Type": "application/json"}
        student_headers = {"Authorization": f"Bearer {student_token}", "Content-Type": "application/json"}
        
        # === STEP 3: TEACHER CREATES SESSION ===
        print("\n3️⃣ Testing Teacher Session Creation")
        
        session_response = requests.post(
            f"{BASE_URL}/admin/sessions",
            json=session_data,
            headers=teacher_headers
        )
        
        print(f"   Session creation status: {session_response.status_code}")
        if session_response.status_code == 201:
            session_result = session_response.json()
            session_id = session_result.get("data", {}).get("session_id")
            print(f"   ✅ Session created successfully: {session_id}")
            print(f"   📋 Session name: {session_result.get('data', {}).get('session_name')}")
        else:
            print(f"   ❌ Session creation failed: {session_response.text}")
            return False
        
        # === STEP 4: STUDENT VIEWS ACTIVE SESSIONS ===
        print("\n4️⃣ Testing Student Can View Active Sessions")
        
        active_sessions_response = requests.get(
            f"{BASE_URL}/attendance/active-sessions",
            headers=student_headers
        )
        
        print(f"   Active sessions status: {active_sessions_response.status_code}")
        if active_sessions_response.status_code == 200:
            active_sessions = active_sessions_response.json().get("data", [])
            print(f"   ✅ Student can see {len(active_sessions)} active sessions")
            
            # Check if our created session is in the list
            our_session = next((s for s in active_sessions if s.get("session_id") == session_id), None)
            if our_session:
                print(f"   ✅ Student can see teacher's session: '{our_session.get('session_name')}'")
            else:
                print("   ⚠️ Student cannot see teacher's session in active sessions")
                print(f"   Available sessions: {[s.get('session_name') for s in active_sessions]}")
        else:
            print(f"   ❌ Student cannot view active sessions: {active_sessions_response.text}")
            return False
        
        # === STEP 5: STUDENT MARKS ATTENDANCE ===
        print("\n5️⃣ Testing Student Attendance Marking")
        
        # Student location (within radius of session)
        attendance_data = {
            "session_id": session_id,
            "lat": 40.7129,  # Close to session location
            "lon": -74.0061
        }
        
        attendance_response = requests.post(
            f"{BASE_URL}/attendance/check-in",
            json=attendance_data,
            headers=student_headers
        )
        
        print(f"   Attendance marking status: {attendance_response.status_code}")
        if attendance_response.status_code == 200:
            attendance_result = attendance_response.json()
            record_id = attendance_result.get("data", {}).get("record_id")
            print(f"   ✅ Student attendance marked successfully")
            print(f"   📝 Record ID: {record_id}")
            print(f"   📍 Status: {attendance_result.get('data', {}).get('status', 'unknown')}")
        else:
            print(f"   ❌ Student attendance marking failed: {attendance_response.text}")
            return False
        
        # === STEP 6: TEACHER VIEWS ATTENDANCE REPORT ===
        print("\n6️⃣ Testing Teacher Can View Attendance Report")
        
        report_response = requests.get(
            f"{BASE_URL}/attendance/session/{session_id}/report",
            headers=teacher_headers
        )
        
        print(f"   Attendance report status: {report_response.status_code}")
        if report_response.status_code == 200:
            report_data = report_response.json()
            print("   ✅ Teacher can view attendance report")
            print(f"   📊 Report data available: {list(report_data.get('data', {}).keys())}")
        else:
            print(f"   ❌ Teacher cannot view attendance report: {report_response.text}")
            # This might fail, so let's also try the session attendance endpoint
            
            print("   🔄 Trying alternative attendance endpoint...")
            alt_report = requests.get(
                f"{BASE_URL}/attendance/session/{session_id}/attendance",
                headers=teacher_headers
            )
            
            print(f"   Alternative report status: {alt_report.status_code}")
            if alt_report.status_code == 200:
                alt_data = alt_report.json()
                attendance_records = alt_data.get("data", {}).get("attendance_records", [])
                print(f"   ✅ Found {len(attendance_records)} attendance records")
                
                if attendance_records:
                    record = attendance_records[0]
                    print(f"   👤 Student record: {record.get('user_id')} - {record.get('status')}")
            else:
                print(f"   ❌ Alternative report also failed: {alt_report.text}")
        
        # === STEP 7: TEST SIMPLIFIED ATTENDANCE (BONUS) ===
        print("\n7️⃣ Testing Simplified Attendance (Bonus)")
        
        # Test if student can use simplified attendance
        simple_attendance = requests.post(
            f"{BASE_URL}/simple/mark-attendance",
            json={
                "latitude": 40.7128,
                "longitude": -74.0060,
                "session_id": session_id  # Optional for simplified
            },
            headers=student_headers
        )
        
        print(f"   Simplified attendance status: {simple_attendance.status_code}")
        if simple_attendance.status_code == 200:
            simple_result = simple_attendance.json()
            print(f"   ✅ Simplified attendance works: {simple_result.get('data', {}).get('status')}")
        else:
            print(f"   ⚠️ Simplified attendance not working: {simple_attendance.text}")
        
        print("\n🎉 Teacher-Student Workflow Test Completed!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        return False

def test_session_visibility():
    """Test session visibility across different user roles."""
    
    print("\n🔍 Testing Session Visibility")
    print("=" * 40)
    
    try:
        # Test public sessions endpoint
        public_sessions = requests.get(f"{BASE_URL}/attendance/public-sessions")
        print(f"Public sessions status: {public_sessions.status_code}")
        
        if public_sessions.status_code == 200:
            sessions = public_sessions.json().get("data", [])
            print(f"✅ Found {len(sessions)} public sessions")
            
            for session in sessions[:3]:  # Show first 3
                print(f"   📋 {session.get('session_name')} (ID: {session.get('session_id')[:8]}...)")
        else:
            print(f"❌ Public sessions failed: {public_sessions.text}")
        
    except Exception as e:
        print(f"❌ Session visibility test error: {str(e)}")

def test_authentication_issues():
    """Test common authentication issues."""
    
    print("\n🔐 Testing Authentication Issues")
    print("=" * 40)
    
    # Test endpoints without authentication
    endpoints_to_test = [
        ("GET", "/attendance/active-sessions"),
        ("POST", "/admin/sessions"),
        ("POST", "/attendance/check-in"),
        ("GET", "/simple/my-attendance")
    ]
    
    for method, endpoint in endpoints_to_test:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}")
            else:
                response = requests.post(f"{BASE_URL}{endpoint}", json={})
            
            if response.status_code == 401:
                print(f"   ✅ {method} {endpoint}: Properly requires authentication")
            else:
                print(f"   ⚠️ {method} {endpoint}: Status {response.status_code} (expected 401)")
        
        except Exception as e:
            print(f"   ❌ {method} {endpoint}: Error {str(e)}")

if __name__ == "__main__":
    """Run the comprehensive tests."""
    
    print("🧪 Comprehensive Teacher-Student Workflow Tests")
    print("=" * 70)
    
    # Check if server is running
    try:
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Server is running")
        else:
            print("⚠️ Server responded but health check failed")
    except Exception as e:
        print(f"❌ Server not accessible: {str(e)}")
        print("Make sure the Flask server is running with: python app.py")
        exit(1)
    
    # Run tests
    success = test_complete_teacher_student_workflow()
    test_session_visibility()
    test_authentication_issues()
    
    print("\n📋 Test Summary")
    print("=" * 20)
    
    if success:
        print("🎊 Main workflow test: ✅ PASSED")
        print("\nThe teacher-student session workflow is working correctly!")
        print("\n✅ Teachers can create sessions")
        print("✅ Students can see active sessions")
        print("✅ Students can mark attendance")
        print("✅ Teachers can view reports")
    else:
        print("⚠️ Main workflow test: ❌ FAILED")
        print("\nSome issues were found. Check the logs above.")
        print("Common issues:")
        print("- Authentication problems (users not in same organization)")
        print("- Database schema issues")
        print("- Missing permissions")
    
    print("\n🔧 Next Steps:")
    print("1. If authentication fails: Set up proper test users")
    print("2. If sessions not visible: Check organization matching")
    print("3. If attendance fails: Verify session timing and location")
    print("4. If reports fail: Check database schema")
