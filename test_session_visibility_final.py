#!/usr/bin/env python3
"""
🔍 FINAL SESSION VISIBILITY TEST

This test verifies that our backend fixes resolve the issue where
students couldn't see sessions created by admins in the same organization.
"""

import requests
import json
from datetime import datetime, timedelta

# Your production API URL
BASE_URL = "https://attendance-backend-3l6a.onrender.com"

def test_session_visibility():
    """Test complete session visibility workflow."""
    
    print("🎯 TESTING SESSION VISIBILITY FIX...")
    print("="*50)
    
    # Test data
    test_org_name = f"Test Org {datetime.now().strftime('%Y%m%d_%H%M%S')}"
    admin_email = f"admin_{datetime.now().strftime('%Y%m%d_%H%M%S')}@test.com"
    student_email = f"student_{datetime.now().strftime('%Y%m%d_%H%M%S')}@test.com"
    
    try:
        # Step 1: Create test organization
        print("1️⃣ Creating test organization...")
        org_data = {
            "org_name": test_org_name,
            "org_description": "Test organization for session visibility"
        }
        
        org_response = requests.post(f"{BASE_URL}/public/organizations", json=org_data)
        if org_response.status_code != 201:
            print(f"❌ Failed to create organization: {org_response.text}")
            return False
            
        org_data_response = org_response.json()
        org_id = org_data_response['data']['org_id']
        print(f"✅ Organization created: {org_id}")
        
        # Step 2: Create admin user
        print("2️⃣ Creating admin user...")
        admin_data = {
            "name": "Test Admin",
            "email": admin_email,
            "password": "testpassword123",
            "role": "admin",
            "org_id": org_id
        }
        
        admin_response = requests.post(f"{BASE_URL}/public/register", json=admin_data)
        if admin_response.status_code != 201:
            print(f"❌ Failed to create admin: {admin_response.text}")
            return False
        print("✅ Admin user created")
        
        # Step 3: Create student user
        print("3️⃣ Creating student user...")
        student_data = {
            "name": "Test Student",
            "email": student_email,
            "password": "testpassword123",
            "role": "student",
            "org_id": org_id
        }
        
        student_response = requests.post(f"{BASE_URL}/public/register", json=student_data)
        if student_response.status_code != 201:
            print(f"❌ Failed to create student: {student_response.text}")
            return False
        print("✅ Student user created")
        
        # Step 4: Login as admin
        print("4️⃣ Logging in as admin...")
        admin_login = requests.post(f"{BASE_URL}/public/login", json={
            "email": admin_email,
            "password": "testpassword123"
        })
        
        if admin_login.status_code != 200:
            print(f"❌ Admin login failed: {admin_login.text}")
            return False
            
        admin_token = admin_login.json()['data']['token']
        print("✅ Admin logged in successfully")
        
        # Step 5: Login as student
        print("5️⃣ Logging in as student...")
        student_login = requests.post(f"{BASE_URL}/public/login", json={
            "email": student_email,
            "password": "testpassword123"
        })
        
        if student_login.status_code != 200:
            print(f"❌ Student login failed: {student_login.text}")
            return False
            
        student_token = student_login.json()['data']['token']
        print("✅ Student logged in successfully")
        
        # Step 6: Admin creates a session
        print("6️⃣ Admin creating attendance session...")
        now = datetime.now()
        start_time = now + timedelta(minutes=5)
        end_time = now + timedelta(hours=2)
        
        session_data = {
            "session_name": "Test Math Class",
            "description": "Testing session visibility",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "location": "Room 101",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "radius": 100
        }
        
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        session_response = requests.post(f"{BASE_URL}/admin/attendance-sessions", 
                                       json=session_data, headers=admin_headers)
        
        if session_response.status_code != 201:
            print(f"❌ Failed to create session: {session_response.text}")
            return False
            
        session_id = session_response.json()['data']['session_id']
        print(f"✅ Session created by admin: {session_id}")
        
        # Step 7: Student tries to see active sessions
        print("7️⃣ Student checking for active sessions...")
        student_headers = {"Authorization": f"Bearer {student_token}"}
        student_sessions_response = requests.get(f"{BASE_URL}/attendance/active-sessions", 
                                                headers=student_headers)
        
        if student_sessions_response.status_code != 200:
            print(f"❌ Student failed to get sessions: {student_sessions_response.text}")
            return False
            
        student_sessions = student_sessions_response.json()['data']
        print(f"✅ Student retrieved {len(student_sessions)} sessions")
        
        # Step 8: Verify the session is visible
        session_found = False
        for session in student_sessions:
            if session['session_id'] == session_id:
                session_found = True
                print(f"✅ SESSION VISIBILITY CONFIRMED!")
                print(f"   Session Name: {session['session_name']}")
                print(f"   Session ID: {session['session_id']}")
                print(f"   Created by admin, visible to student!")
                break
        
        if not session_found:
            print(f"❌ SESSION NOT VISIBLE TO STUDENT!")
            print(f"   Expected session ID: {session_id}")
            print(f"   Student sessions: {json.dumps(student_sessions, indent=2)}")
            return False
        
        print("\n🎉 SUCCESS! The backend fix works!")
        print("✅ Students can now see sessions created by admins")
        print("✅ Session visibility issue has been resolved")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_session_visibility()
    if success:
        print("\n🎯 RESULT: BACKEND FIX SUCCESSFUL!")
    else:
        print("\n💥 RESULT: BACKEND STILL HAS ISSUES!")
