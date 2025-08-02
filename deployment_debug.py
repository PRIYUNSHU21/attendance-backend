#!/usr/bin/env python3
"""
🔧 BACKEND DEVELOPER: DEPLOYMENT VERIFICATION
Check if the server is actually responding and what routes are available
"""

import requests
import json

def check_deployment_status():
    """Check the actual deployment status"""
    base_url = "https://attendance-backend-app.onrender.com"
    
    print("🔍 DEPLOYMENT STATUS CHECK")
    print("=" * 50)
    
    # Test 1: Basic connectivity
    print("1️⃣ Basic Server Connectivity")
    try:
        response = requests.get(base_url, timeout=15)
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        if response.text:
            print(f"   Response: {response.text[:500]}...")
    except requests.exceptions.Timeout:
        print("   ❌ Server timeout - deployment may be sleeping")
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
    
    # Test 2: Try different potential endpoints
    print(f"\n2️⃣ Testing Various Endpoints")
    endpoints = [
        "/",
        "/health", 
        "/api",
        "/api/health",
        "/attendance/public-sessions",
        "/api/attendance/public-sessions",
        "/auth/login",
        "/api/auth/login"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            status_emoji = "✅" if response.status_code < 500 else "❌"
            print(f"   {status_emoji} {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"      Response: {json.dumps(data, indent=8)[:200]}...")
                except:
                    print(f"      Response: {response.text[:100]}...")
        except Exception as e:
            print(f"   ❌ {endpoint}: {str(e)[:50]}...")
    
    # Test 3: Check if it's a routing issue
    print(f"\n3️⃣ Diagnosing Routing Issues")
    
    # The server might be expecting different paths
    # Let's check the actual app.py to see route registration
    print("   Based on app.py analysis:")
    print("   - Routes should be at /health, /attendance/*, /auth/*")
    print("   - NOT /api/attendance/* (no API prefix in app.py)")
    print("   - If all return 404, the server deployment has issues")
    
    # Test 4: Check if server is in sleep mode
    print(f"\n4️⃣ Render Sleep Mode Check")
    print("   Render free tier puts apps to sleep after 15 minutes")
    print("   First request after sleep takes 30+ seconds to wake up")
    print("   Trying wake-up request...")
    
    try:
        # Long timeout for potential wake-up
        response = requests.get(f"{base_url}/health", timeout=60)
        print(f"   Wake-up attempt result: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Server is now awake!")
            return True
        else:
            print(f"   ❌ Server still not responding properly")
            return False
    except Exception as e:
        print(f"   ❌ Wake-up failed: {e}")
        return False

def test_with_correct_base_url():
    """Test with potentially different base URL"""
    print(f"\n5️⃣ Testing Alternative URLs")
    
    # The repo name suggests it might be deployed differently
    alternative_urls = [
        "https://attendance-backend-app.onrender.com",
        "https://attendance-backend.onrender.com", 
        "https://priyunshu21-attendance-backend.onrender.com",
        "https://attendance-backend-go8h.onrender.com"  # From previous tests
    ]
    
    for url in alternative_urls:
        print(f"\n   Testing: {url}")
        try:
            response = requests.get(f"{url}/health", timeout=15)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   ✅ FOUND WORKING URL: {url}")
                
                # Test a few endpoints on this working URL
                test_endpoints = ["/attendance/public-sessions", "/auth/login"]
                for endpoint in test_endpoints:
                    try:
                        resp = requests.get(f"{url}{endpoint}", timeout=10)
                        print(f"      {endpoint}: {resp.status_code}")
                    except:
                        print(f"      {endpoint}: Failed")
                        
                return url
        except Exception as e:
            print(f"   ❌ Failed: {str(e)[:50]}")
    
    return None

if __name__ == "__main__":
    print("🚀 BACKEND DEVELOPER - DEPLOYMENT DIAGNOSIS")
    print("=" * 60)
    
    working = check_deployment_status()
    if not working:
        working_url = test_with_correct_base_url()
        if working_url:
            print(f"\n✅ SOLUTION: Use {working_url} as base URL")
        else:
            print("\n❌ No working deployment found")
            print("   Deployment may need to be restarted or fixed")
    else:
        print("\n✅ Deployment is working correctly")
