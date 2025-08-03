"""
🎯 COMPLETE ATTENDANCE FLOW TEST
This will test the entire flow:
1. Teacher login
2. Teacher creates session
3. Student login  
4. Student sees session
5. Student marks attendance
"""
import sys
sys.path.append('.')

import requests
import json
from datetime import datetime

# Test URLs
LOCAL_URL = "http://127.0.0.1:5000"
PRODUCTION_URL = "https://attendance-backend-go8h.onrender.com"

def test_complete_flow(base_url):
    print(f"🌐 Testing complete flow on: {base_url}")
    
    # Step 1: Teacher Login
    print("\n👨‍🏫 STEP 1: Teacher Login")
    teacher_response = requests.post(f"{base_url}/auth/login", json={
        "email": "alpha@gmail.com",
        "password": "P21042004p#"
    })
    
    if teacher_response.status_code != 200:
        print(f"❌ Teacher login failed: {teacher_response.status_code}")
        print(f"Error: {teacher_response.text}")
        return False
    
    teacher_data = teacher_response.json()
    teacher_token = teacher_data.get('token')
    print(f"✅ Teacher login successful! Token: {teacher_token[:20]}...")
    
    # Step 2: Teacher Creates Session
    print("\n📝 STEP 2: Teacher Creates Session")
    session_response = requests.post(f"{base_url}/admin/create-attendance-session", 
        json={
            "subject": "Mathematics Test Session",
            "location": "Room 101",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "duration_minutes": 60
        },
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    
    if session_response.status_code != 200:
        print(f"❌ Session creation failed: {session_response.status_code}")
        print(f"Error: {session_response.text}")
        return False
    
    session_data = session_response.json()
    session_id = session_data.get('session_id')
    print(f"✅ Session created! ID: {session_id}")
    
    # Step 3: Student Login
    print("\n👨‍🎓 STEP 3: Student Login")
    student_response = requests.post(f"{base_url}/auth/login", json={
        "email": "beta@gmail.com", 
        "password": "P21042004p#"
    })
    
    if student_response.status_code != 200:
        print(f"❌ Student login failed: {student_response.status_code}")
        print(f"Error: {student_response.text}")
        return False
    
    student_data = student_response.json()
    student_token = student_data.get('token')
    print(f"✅ Student login successful! Token: {student_token[:20]}...")
    
    # Step 4: Student Sees Sessions
    print("\n👀 STEP 4: Student Views Available Sessions")
    sessions_response = requests.get(f"{base_url}/attendance/active-sessions",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    
    if sessions_response.status_code != 200:
        print(f"❌ Failed to get sessions: {sessions_response.status_code}")
        print(f"Error: {sessions_response.text}")
        return False
    
    sessions_data = sessions_response.json()
    available_sessions = sessions_data.get('sessions', [])
    print(f"✅ Student can see {len(available_sessions)} sessions")
    
    if not available_sessions:
        print("❌ No sessions available for student")
        return False
    
    # Step 5: Student Marks Attendance
    print("\n✋ STEP 5: Student Marks Attendance")
    attendance_response = requests.post(f"{base_url}/attendance/simple-checkin",
        json={
            "session_id": session_id,
            "latitude": 28.6140,  # Close to session location
            "longitude": 77.2091
        },
        headers={"Authorization": f"Bearer {student_token}"}
    )
    
    if attendance_response.status_code != 200:
        print(f"❌ Attendance marking failed: {attendance_response.status_code}")
        print(f"Error: {attendance_response.text}")
        return False
    
    attendance_data = attendance_response.json()
    print(f"✅ Attendance marked successfully!")
    print(f"   Record ID: {attendance_data.get('record_id')}")
    print(f"   Status: {attendance_data.get('status')}")
    
    print("\n🎉 COMPLETE FLOW SUCCESS! All steps working.")
    return True

if __name__ == "__main__":
    print("🧪 TESTING COMPLETE ATTENDANCE FLOW")
    print("=" * 50)
    
    # Test locally first
    print("\n🏠 Testing LOCAL server...")
    try:
        local_success = test_complete_flow(LOCAL_URL)
    except Exception as e:
        print(f"❌ Local test failed: {e}")
        local_success = False
    
    # Test production
    print("\n🌍 Testing PRODUCTION server...")
    try:
        prod_success = test_complete_flow(PRODUCTION_URL)
    except Exception as e:
        print(f"❌ Production test failed: {e}")
        prod_success = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 FINAL RESULTS:")
    print(f"Local Server: {'✅ WORKING' if local_success else '❌ FAILED'}")
    print(f"Production: {'✅ WORKING' if prod_success else '❌ FAILED'}")
    
    if prod_success:
        print("\n🚀 PRODUCTION IS READY!")
        print("✅ Teachers can login and create sessions")
        print("✅ Students can login and see sessions") 
        print("✅ Students can mark attendance")
        print("✅ Complete attendance system working!")
    else:
        print("\n⚠️  PRODUCTION NEEDS FIXING")
