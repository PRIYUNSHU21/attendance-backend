#!/usr/bin/env python3
"""
🔧 BACKEND DEVELOPER: LIVE SERVER ENDPOINT VERIFICATION
Tests all endpoints on the live production server
"""

import requests
import json

def test_live_server():
    """Comprehensive test of live server endpoints"""
    base_url = "https://attendance-backend-app.onrender.com"
    
    print("🚀 LIVE SERVER ENDPOINT TESTING")
    print("=" * 50)
    
    # Test basic server health
    print("1️⃣ Server Health Check")
    try:
        response = requests.get(base_url, timeout=10)
        print(f"   Base URL Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
    
    # Test API root
    print("\n2️⃣ API Root Check")
    try:
        response = requests.get(f"{base_url}/api", timeout=10)
        print(f"   /api Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test attendance API
    print("\n3️⃣ Attendance API Check")
    try:
        response = requests.get(f"{base_url}/api/attendance", timeout=10)
        print(f"   /api/attendance Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test public sessions endpoint
    print("\n4️⃣ Public Sessions Endpoint")
    try:
        response = requests.get(f"{base_url}/api/attendance/public-sessions", timeout=10)
        print(f"   /api/attendance/public-sessions Status: {response.status_code}")
        
        if response.status_code == 200:
            sessions = response.json()
            print(f"   ✅ Found {len(sessions)} public sessions")
            if sessions:
                print(f"   📝 First session: {sessions[0].get('session_name', 'Unknown')}")
        elif response.status_code == 404:
            print("   ❌ Endpoint not found - route may not be registered")
        else:
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test other known endpoints
    print("\n5️⃣ Other Endpoint Tests")
    endpoints_to_test = [
        "/api/auth/login",
        "/api/attendance/check-in", 
        "/api/attendance/sessions",
        "/health",
        "/status"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            status_emoji = "✅" if response.status_code < 500 else "❌"
            print(f"   {status_emoji} {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint}: Connection failed")
    
    print(f"\n🎯 ANALYSIS:")
    print("   If public-sessions returns 404, the route isn't registered")
    print("   If other endpoints work, the server is live but missing our new routes")
    print("   This suggests we need to check route registration in app.py")

if __name__ == "__main__":
    test_live_server()
