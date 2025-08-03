#!/usr/bin/env python3
"""
Test script for company location endpoint with production credentials
"""
import requests
import json

# Test configuration
BASE_URL = "http://127.0.0.1:5000"

# Production credentials
CREDENTIALS = {
    'admin': {
        'email': 'psaha21.un@gmail.com',
        'password': 'P21042004p#'
    },
    'teacher': {
        'email': 'alpha@gmail.com', 
        'password': 'P21042004p#'
    },
    'student': {
        'email': 'beta@gmail.com',
        'password': 'P21042004p#'
    }
}

def login_user(role):
    """Login as specified role and return token"""
    print(f"🔐 Logging in as {role}...")
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=CREDENTIALS[role])
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and 'data' in data:
                token = data['data'].get('jwt_token')
                if token:
                    print(f"   ✅ {role.title()} login successful")
                    return token
        
        print(f"   ❌ {role.title()} login failed: {response.text}")
        return None
        
    except Exception as e:
        print(f"   ❌ {role.title()} login error: {str(e)}")
        return None

def test_company_location_endpoint():
    """Test the company location endpoint with frontend payload format"""
    print("\n🏢 Testing Company Location Endpoint")
    print("=" * 50)
    
    # Test with admin credentials
    admin_token = login_user('admin')
    if not admin_token:
        print("❌ Cannot test without admin token")
        return
    
    # Test payload (exactly what frontend sends)
    payload = {
        "latitude": 22.6164736,
        "longitude": 88.3785728,
        "name": "SAHA",
        "radius": 100
    }
    
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n📤 Sending payload to /simple/company/create:")
    print(json.dumps(payload, indent=2))
    
    try:
        response = requests.post(f"{BASE_URL}/simple/company/create", json=payload, headers=headers)
        
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"📄 Response Content:")
        
        try:
            response_data = response.json()
            print(json.dumps(response_data, indent=2))
            
            if response.status_code == 200 and response_data.get('success'):
                print("\n✅ Company location endpoint is working correctly!")
                
                # Verify response structure
                data = response_data.get('data', {})
                if 'name' in data and 'location' in data:
                    location = data['location']
                    if all(key in location for key in ['latitude', 'longitude', 'radius']):
                        print("✅ Response structure is correct")
                    else:
                        print("⚠️ Response structure missing expected location fields")
                else:
                    print("⚠️ Response structure missing expected data fields")
            else:
                print(f"\n❌ Company location endpoint failed!")
                
        except json.JSONDecodeError:
            print(f"Raw response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")

def test_non_admin_access():
    """Test that non-admin users cannot access the endpoint"""
    print("\n🔒 Testing Non-Admin Access Control")
    print("=" * 40)
    
    # Test with teacher credentials
    teacher_token = login_user('teacher')
    if teacher_token:
        headers = {
            "Authorization": f"Bearer {teacher_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "latitude": 22.6164736,
            "longitude": 88.3785728,
            "name": "SAHA",
            "radius": 100
        }
        
        try:
            response = requests.post(f"{BASE_URL}/simple/company/create", json=payload, headers=headers)
            print(f"📊 Teacher access response: {response.status_code}")
            
            if response.status_code == 403:
                print("✅ Access control working - teachers cannot access endpoint")
            else:
                print("⚠️ Access control issue - teachers should not have access")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Teacher access test failed: {str(e)}")

def test_health_check():
    """Test if server is running"""
    print("🏥 Testing Server Health")
    print("=" * 25)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Server is running and healthy")
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 COMPANY LOCATION ENDPOINT TEST")
    print("=" * 50)
    
    # Check if server is running
    if not test_health_check():
        print("\n❌ Please start the Flask server first")
        exit(1)
    
    # Run tests
    test_company_location_endpoint()
    test_non_admin_access()
    
    print("\n" + "=" * 50)
    print("🏁 Company location endpoint testing complete!")
