#!/usr/bin/env python3
"""
🧪 BACKEND FLAW INVESTIGATION - test_regular_user.py

This script investigates backend issues discovered by the frontend team:
1. Session visibility problems for students
2. Session timing validation issues
3. Organization filtering problems
"""

import requests
import json
from datetime import datetime, timedelta
import uuid

# Configuration
# BASE_URL = "https://attendance-backend-go8h.onrender.com"
BASE_URL = "http://127.0.0.1:5000"  # Test against LOCAL backend with fixes

HEADERS = {"Content-Type": "application/json"}

def log_test(step, message, data=None):
    """Log test results with formatting"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {step}: {message}")
    if data:
        print(f"    Data: {json.dumps(data, indent=2)}")

def test_backend_flaw():
    """Test the backend flaw discovered by frontend team"""
    
    print("🔍 INVESTIGATING BACKEND FLAW DISCOVERED BY FRONTEND TEAM")
    print("=" * 70)
    
    # Step 1: Create test organization
    print("\n🏢 Step 1: Creating test organization...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    org_data = {
        "name": f"Backend Test Org {timestamp}",
        "description": "Testing backend flaw",
        "contact_email": f"backendtest_{timestamp}@test.edu"
    }
    
    try:
        org_response = requests.post(f"{BASE_URL}/auth/public/organizations", json=org_data, headers=HEADERS)
        if org_response.status_code != 201:
            log_test("❌ ORG CREATE", f"Failed: {org_response.status_code}", org_response.text)
            return False
        
        org_result = org_response.json()
        org_id = org_result['data']['org_id']
        log_test("✅ ORG CREATE", f"Success - Org ID: {org_id}")
        
    except Exception as e:
        log_test("❌ ORG CREATE", f"Exception: {str(e)}")
        return False
    
    # Step 2: Create admin user
    print("\n👨‍💼 Step 2: Creating admin user...")
    admin_data = {
        "name": "Test Admin",
        "email": f"admin_{timestamp}@test.edu",
        "password": "P21042004p#",
        "org_id": org_id
    }
    
    try:
        admin_response = requests.post(f"{BASE_URL}/auth/public/admin", json=admin_data, headers=HEADERS)
        if admin_response.status_code != 201:
            log_test("❌ ADMIN CREATE", f"Failed: {admin_response.status_code}", admin_response.text)
            return False
        
        log_test("✅ ADMIN CREATE", "Success")
        
    except Exception as e:
        log_test("❌ ADMIN CREATE", f"Exception: {str(e)}")
        return False
    
    # Step 3: Login admin to get token
    print("\n🔑 Step 3: Admin login...")
    try:
        login_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": admin_data["email"],
            "password": admin_data["password"]
        }, headers=HEADERS)
        
        if login_response.status_code != 200:
            log_test("❌ ADMIN LOGIN", f"Failed: {login_response.status_code}", login_response.text)
            return False
        
        admin_token = login_response.json()["data"]["jwt_token"]
        admin_headers = {**HEADERS, "Authorization": f"Bearer {admin_token}"}
        log_test("✅ ADMIN LOGIN", f"Success - Token: {admin_token[:20]}...")
        
    except Exception as e:
        log_test("❌ ADMIN LOGIN", f"Exception: {str(e)}")
        return False
    
    # Step 4: Create student user
    print("\n👨‍🎓 Step 4: Creating student user...")
    student_data = {
        "name": "Test Student",
        "email": f"student_{timestamp}@test.edu",
        "password": "P21042004p#",
        "org_id": org_id
    }
    
    try:
        student_response = requests.post(f"{BASE_URL}/auth/register", json=student_data, headers=admin_headers)
        if student_response.status_code != 201:
            log_test("❌ STUDENT CREATE", f"Failed: {student_response.status_code}", student_response.text)
            return False
        
        log_test("✅ STUDENT CREATE", "Success")
        
    except Exception as e:
        log_test("❌ STUDENT CREATE", f"Exception: {str(e)}")
        return False
    
    # Step 5: Login student to get token
    print("\n🔑 Step 5: Student login...")
    try:
        student_login_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": student_data["email"],
            "password": student_data["password"]
        }, headers=HEADERS)
        
        if student_login_response.status_code != 200:
            log_test("❌ STUDENT LOGIN", f"Failed: {student_login_response.status_code}", student_login_response.text)
            return False
        
        student_token = student_login_response.json()["data"]["jwt_token"]
        student_headers = {**HEADERS, "Authorization": f"Bearer {student_token}"}
        log_test("✅ STUDENT LOGIN", f"Success - Token: {student_token[:20]}...")
        
    except Exception as e:
        log_test("❌ STUDENT LOGIN", f"Exception: {str(e)}")
        return False
    
    # Step 6: Admin creates attendance session
    print("\n📅 Step 6: Admin creating attendance session...")
    now = datetime.now()
    start_time = (now - timedelta(minutes=5)).isoformat()   # Started 5 minutes ago
    end_time = (now + timedelta(hours=2)).isoformat()      # Ends in 2 hours
    
    session_data = {
        "session_name": f"Backend Test Session {timestamp}",
        "description": "Testing backend session visibility",
        "start_time": start_time,
        "end_time": end_time,
        "location": "Test Room 101",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "radius": 100,
        "is_active": True
    }
    
    try:
        session_response = requests.post(f"{BASE_URL}/admin/sessions", json=session_data, headers=admin_headers)
        if session_response.status_code != 201:
            log_test("❌ SESSION CREATE", f"Failed: {session_response.status_code}", session_response.text)
            return False
        
        session_result = session_response.json()
        session_id = session_result['data']['session_id']
        log_test("✅ SESSION CREATE", f"Success - Session ID: {session_id}")
        log_test("📊 SESSION DETAILS", f"Start: {start_time}, End: {end_time}")
        
    except Exception as e:
        log_test("❌ SESSION CREATE", f"Exception: {str(e)}")
        return False
    
    # Step 7: Test CRITICAL FLAW - Student checks for active sessions
    print("\n🚨 Step 7: TESTING CRITICAL FLAW - Student checking active sessions...")
    try:
        student_sessions_response = requests.get(f"{BASE_URL}/attendance/active-sessions", headers=student_headers)
        if student_sessions_response.status_code != 200:
            log_test("❌ STUDENT SESSIONS", f"Failed: {student_sessions_response.status_code}", student_sessions_response.text)
            return False
        
        student_sessions = student_sessions_response.json()
        log_test("🔍 STUDENT SESSIONS", f"Found {len(student_sessions.get('data', []))} sessions")
        
        if len(student_sessions.get('data', [])) == 0:
            log_test("🚨 CRITICAL FLAW", "Student cannot see admin's session in same organization!")
            log_test("🔍 FLAW DETAILS", f"Admin created session in org {org_id}, student in same org sees nothing")
        else:
            log_test("✅ SESSION VISIBILITY", "Student can see sessions correctly")
        
    except Exception as e:
        log_test("❌ STUDENT SESSIONS", f"Exception: {str(e)}")
        return False
    
    # Step 8: Test admin's view for comparison
    print("\n👨‍💼 Step 8: Admin checking active sessions for comparison...")
    try:
        admin_sessions_response = requests.get(f"{BASE_URL}/attendance/active-sessions", headers=admin_headers)
        if admin_sessions_response.status_code != 200:
            log_test("❌ ADMIN SESSIONS", f"Failed: {admin_sessions_response.status_code}", admin_sessions_response.text)
            return False
        
        admin_sessions = admin_sessions_response.json()
        log_test("👨‍💼 ADMIN SESSIONS", f"Found {len(admin_sessions.get('data', []))} sessions")
        
        if len(admin_sessions.get('data', [])) > 0:
            session_info = admin_sessions['data'][0]
            log_test("📊 ADMIN SESSION INFO", f"Session: {session_info.get('session_name', 'Unknown')}")
            log_test("📊 SESSION ORG", f"Org ID: {session_info.get('org_id', 'Unknown')}")
        
    except Exception as e:
        log_test("❌ ADMIN SESSIONS", f"Exception: {str(e)}")
        return False
    
    # Step 9: Test session timing flaw - Try to check in
    print("\n⏰ Step 9: Testing session timing flaw...")
    if len(student_sessions.get('data', [])) > 0:
        try:
            checkin_data = {
                "latitude": 40.7128,
                "longitude": -74.0060
            }
            
            checkin_response = requests.post(
                f"{BASE_URL}/attendance/checkin/{session_id}", 
                json=checkin_data, 
                headers=student_headers
            )
            
            log_test("⏰ CHECKIN RESULT", f"Status: {checkin_response.status_code}")
            if checkin_response.status_code != 200:
                log_test("🚨 TIMING FLAW", f"Checkin failed: {checkin_response.text}")
            else:
                log_test("✅ TIMING OK", "Session timing works correctly")
                
        except Exception as e:
            log_test("❌ CHECKIN TEST", f"Exception: {str(e)}")
    else:
        log_test("⚠️ CHECKIN SKIP", "Cannot test timing - student sees no sessions")
    
    print("\n" + "=" * 70)
    print("🎯 BACKEND FLAW INVESTIGATION COMPLETE")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    test_backend_flaw()
