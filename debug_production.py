#!/usr/bin/env python3
"""
Debug production endpoints to understand the deployment
"""
import requests

def debug_production():
    base_url = "https://attendance-backend-4njr.onrender.com"
    
    endpoints_to_test = [
        "/",
        "/health", 
        "/auth/login",
        "/admin/sessions",
        "/simple/health"
    ]
    
    print("🔍 Debugging Production Endpoints...")
    
    for endpoint in endpoints_to_test:
        try:
            print(f"\n📍 Testing: {base_url}{endpoint}")
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            print(f"   Status: {response.status_code}")
            if response.status_code != 404:
                print(f"   Response: {response.text[:200]}...")
        except Exception as e:
            print(f"   Error: {e}")
    
    # Try a POST request to see if the server is responding differently
    print(f"\n📍 Testing POST to: {base_url}/auth/login")
    try:
        response = requests.post(f"{base_url}/auth/login", 
                               json={"email": "test", "password": "test"}, 
                               timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    debug_production()
