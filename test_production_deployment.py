#!/usr/bin/env python3
"""
Test production deployment - verify session creation works after migration
"""
import requests
import json
from datetime import datetime, timedelta

def test_production_session_creation():
    """Test session creation on production after database migration."""
    
    # Production URL
    base_url = "https://attendance-backend-go8h.onrender.com"
    
    print("🌐 Testing Production Deployment...")
    print(f"Base URL: {base_url}")
    
    # First test health endpoint
    print("\n1️⃣ Testing Health Endpoint...")
    try:
        health_response = requests.get(f"{base_url}/health", timeout=30)
        if health_response.status_code == 200:
            print("✅ Health check passed - Server is running")
            print(f"Response: {health_response.json()}")
        else:
            print(f"❌ Health check failed: {health_response.status_code}")
            print(health_response.text)
            return
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return
    
    # Login as teacher
    print("\n2️⃣ Testing Teacher Login...")
    login_data = {
        "email": "alpha@gmail.com", 
        "password": "P21042004p#"
    }
    
    try:
        login_response = requests.post(f"{base_url}/auth/login", json=login_data, timeout=30)
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(login_response.text)
            return
        
        auth_data = login_response.json()
        token = auth_data.get('data', {}).get('jwt_token')
        if not token:
            print("❌ No JWT token received")
            print(f"Response: {auth_data}")
            return
            
        print("✅ Login successful")
        print(f"Token: {token[:20]}...")
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Test session creation WITH location data
    print("\n3️⃣ Testing Session Creation WITH Location Data...")
    
    start_time = datetime.now().replace(minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=2)
    
    session_data_with_location = {
        "session_name": "Production Test Session WITH Location",
        "description": "Testing after database migration - with location",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "latitude": 28.6139,  # New Delhi
        "longitude": 77.2090,
        "radius": 100
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        session_response = requests.post(
            f"{base_url}/admin/sessions", 
            json=session_data_with_location, 
            headers=headers,
            timeout=30
        )
        
        if session_response.status_code == 201:
            result = session_response.json()
            print("✅ Session with location created successfully!")
            session_data = result.get('data', {})
            print(f"   Session ID: {session_data.get('session_id')}")
            print(f"   Session Name: {session_data.get('session_name')}")
            print(f"   Location: {session_data.get('latitude')}, {session_data.get('longitude')}")
            print(f"   Radius: {session_data.get('radius')} meters")
        else:
            print(f"❌ Session creation WITH location failed: {session_response.status_code}")
            print(session_response.text)
            print("🔍 This means the database migration might not have worked")
            return
            
    except Exception as e:
        print(f"❌ Session creation error: {e}")
        return
    
    # Test session creation WITHOUT location data
    print("\n4️⃣ Testing Session Creation WITHOUT Location Data...")
    
    session_data_no_location = {
        "session_name": "Production Test Session WITHOUT Location",
        "description": "Testing after database migration - no location",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    }
    
    try:
        session_response = requests.post(
            f"{base_url}/admin/sessions", 
            json=session_data_no_location, 
            headers=headers,
            timeout=30
        )
        
        if session_response.status_code == 201:
            result = session_response.json()
            print("✅ Session without location created successfully!")
            session_data = result.get('data', {})
            print(f"   Session ID: {session_data.get('session_id')}")
            print(f"   Session Name: {session_data.get('session_name')}")
            print(f"   Location: {session_data.get('latitude', 'None')}, {session_data.get('longitude', 'None')}")
            print(f"   Radius: {session_data.get('radius')} meters")
        else:
            print(f"❌ Session creation WITHOUT location failed: {session_response.status_code}")
            print(session_response.text)
            return
            
    except Exception as e:
        print(f"❌ Session creation error: {e}")
        return
    
    print("\n🎉 ALL TESTS PASSED!")
    print("✅ Database migration successful")
    print("✅ Session creation working on production")
    print("✅ Both with and without location data")
    print("\n🚀 Your attendance backend is fully operational!")

if __name__ == "__main__":
    test_production_session_creation()
