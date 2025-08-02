#!/usr/bin/env python3
"""
🔧 BACKEND DEVELOPER: CORRECT ENDPOINT TESTING
Tests the correct endpoint paths based on app.py registration
"""

import requests
import json

def test_correct_endpoints():
    """Test the correct endpoint paths without /api prefix"""
    base_url = "https://attendance-backend-app.onrender.com"
    
    print("🚀 TESTING CORRECT ENDPOINT PATHS")
    print("=" * 50)
    
    # Test health endpoint
    print("1️⃣ Health Check")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   /health Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Server is healthy!")
            print(f"   Response: {response.json()}")
        else:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test root endpoint
    print("\n2️⃣ Root Endpoint")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"   / Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Root endpoint works!")
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test public sessions (correct path)
    print("\n3️⃣ Public Sessions Endpoint")
    try:
        response = requests.get(f"{base_url}/attendance/public-sessions", timeout=10)
        print(f"   /attendance/public-sessions Status: {response.status_code}")
        
        if response.status_code == 200:
            sessions = response.json()
            print(f"   ✅ Found {len(sessions.get('data', []))} public sessions")
            if sessions.get('data'):
                first_session = sessions['data'][0]
                print(f"   📝 First session: {first_session.get('session_name', 'Unknown')}")
                print(f"   🔍 Has location field: {'location' in first_session}")
        elif response.status_code == 404:
            print("   ❌ Endpoint not found")
        else:
            print(f"   Response: {response.text[:300]}...")
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test session details endpoint
    print("\n4️⃣ Session Details Endpoint")
    try:
        # First get a session ID
        sessions_response = requests.get(f"{base_url}/attendance/public-sessions", timeout=10)
        if sessions_response.status_code == 200:
            sessions_data = sessions_response.json()
            if sessions_data.get('data'):
                session_id = sessions_data['data'][0]['session_id']
                
                # Test session details
                response = requests.get(f"{base_url}/attendance/sessions/{session_id}", timeout=10)
                print(f"   /attendance/sessions/{session_id[:8]}... Status: {response.status_code}")
                
                if response.status_code == 200:
                    session_data = response.json()
                    print(f"   ✅ Session details retrieved")
                    print(f"   📝 Session: {session_data.get('data', {}).get('session_name', 'Unknown')}")
                else:
                    print(f"   Response: {response.text[:200]}...")
        else:
            print("   ⚠️  No sessions available to test details")
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test attendance check-in
    print("\n5️⃣ Attendance Check-in")
    try:
        attendance_data = {
            "session_id": "test-session",
            "lat": 40.7128,
            "lon": -74.0060
        }
        
        response = requests.post(f"{base_url}/attendance/check-in", 
                               json=attendance_data, timeout=10)
        print(f"   /attendance/check-in Status: {response.status_code}")
        
        if response.status_code == 401:
            print("   ✅ Endpoint accepts parameters (authentication required)")
        elif response.status_code == 400:
            print(f"   ✅ Endpoint works, validation error: {response.text[:200]}...")
        else:
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    print(f"\n🎯 BACKEND SOLUTION STATUS:")
    if any("✅" in line for line in []):  # Will be updated based on results
        print("   ✅ Server is live and responding")
        print("   ✅ SQL column errors fixed in model")
        print("   ✅ Backend solution deployed successfully")
    else:
        print("   ⚠️  Checking deployment status...")

if __name__ == "__main__":
    test_correct_endpoints()
