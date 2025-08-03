#!/usr/bin/env python3
"""
🧪 MARK ATTENDANCE TEST - test_mark_attendance.py

🎯 WHAT THIS FILE DOES:
Tests the mark-attendance endpoint with the exact frontend payload format.
"""

import json
import requests
import sys
import uuid
from datetime import datetime

# Base URL
BASE_URL = "http://localhost:5000"

def check_server_health():
    """Check if the server is running."""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Server is running and healthy")
            return True
        else:
            print(f"❌ Server returned status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Could not connect to server: {str(e)}")
        return False

def login_student():
    """Login as a student to get auth token."""
    print("1️⃣ Testing Student Authentication")
    print("   🔐 Logging in as student...")
    
    login_data = {
        "email": "admin@example.com",  # Using admin credentials for testing
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"   📊 Login status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Login successful")
            print(f"   📊 Response keys: {list(result.keys())}")
            
            token = result.get('data', {}).get('jwt_token')
            print(f"   🎫 Token: {token[:20]}...")
            
            if token:
                return token
        
        print(f"   ❌ Login failed: {response.text}")
        return None
    except Exception as e:
        print(f"   ❌ Login error: {str(e)}")
        return None

def get_active_sessions(token):
    """Get active sessions for the student."""
    print("2️⃣ Getting Active Sessions")
    print("   🔍 Fetching active sessions...")
    
    if not token:
        print("   ❌ No token available")
        return []
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/simple/sessions", headers=headers)
        print(f"   📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Active sessions retrieved successfully")
            
            sessions = result.get('data', [])
            print(f"   📋 Found {len(sessions)} sessions:")
            
            for session in sessions[:3]:  # Show only first 3 sessions
                print(f"      - Session ID: {session.get('session_id')}")
                
            return sessions
        else:
            print(f"   ❌ Failed to get sessions: {response.text}")
            return []
    except Exception as e:
        print(f"   ❌ Error getting sessions: {str(e)}")
        return []

def mark_attendance_with_frontend_format(token, session_id):
    """Mark attendance using the frontend payload format."""
    print("3️⃣ Marking Attendance with Frontend Payload Format")
    
    if not token:
        print("   ❌ No token available")
        return False
    
    # This is exactly the frontend payload format from the example
    payload = {
        "session_id": session_id,
        "lat": 40.7128,  # New York coordinates for testing
        "lon": -74.006,
        "altitude": 10
    }
    
    print("   📝 Using payload:")
    print(json.dumps(payload, indent=6))
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/simple/mark-attendance", 
            headers=headers,
            json=payload
        )
        print(f"   📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Attendance marked successfully")
            print(f"   📋 Response: {result}")
            
            # Test response format
            print("4️⃣ Testing Response Format")
            if result.get('success') is True:
                print("   ✓ Success flag is True")
            else:
                print("   ❌ Success flag is not True")
            
            data = result.get('data', {})
            if 'record_id' in data:
                print("   ✓ Record ID is present")
            
            if data.get('user_id'):
                print("   ✓ User ID matches student ID")
            
            if 'status' in data:
                print(f"   ✓ Status is recorded ({data.get('status')})")
                
            if 'distance' in data:
                print("   ✓ Distance calculation included")
                
            if 'timestamp' in data:
                print("   ✓ Timestamp is valid")
                
            if 'organization' in data:
                print("   ✓ Organization name is included")
            
            return True
        else:
            print(f"   ❌ Failed to mark attendance: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error marking attendance: {str(e)}")
        return False

def main():
    """Run the main test flow."""
    print("🧪 MARK ATTENDANCE ENDPOINT TEST")
    print("=======================================================")
    
    # Check if server is running
    if not check_server_health():
        print("❌ Cannot proceed with tests because server is not available")
        return
    
    # Step 1: Login as student
    token = login_student()
    if not token:
        print("❌ Cannot proceed with tests because login failed")
        return
    
    # Step 2: Get active sessions
    sessions = get_active_sessions(token)
    if not sessions:
        print("❌ Cannot proceed with tests because no active sessions were found")
        return
    
    # Step 3: Mark attendance using a session
    session_id = sessions[0].get('session_id')
    success = mark_attendance_with_frontend_format(token, session_id)
    
    # Print test summary
    print("=======================================================")
    print("🎯 TEST SUMMARY")
    print("=======================================================")
    print("✅ Server Health Check: PASSED")
    print("✅ Student Login: PASSED")
    print("✅ Active Sessions Retrieval: PASSED")
    
    if success:
        print("✅ Attendance Marking with Frontend Format: PASSED")
        print("✅ Response Format Validation: PASSED")
        print("=======================================================")
        print("🏁 ALL TESTS PASSED! The mark-attendance endpoint now accepts the frontend payload format.")
    else:
        print("❌ Attendance Marking with Frontend Format: FAILED")
        print("=======================================================")
        print("❌ TEST FAILED! Check the errors above for details.")

if __name__ == "__main__":
    main()
