#!/usr/bin/env python3
"""
Test script to verify that both admin and teacher can set up organization locations
"""

import requests
import json

# Base URL for the API
BASE_URL = "https://attendance-backend-go8h.onrender.com"

# Test credentials
ADMIN_CREDENTIALS = {
    "email": "psaha21.un@gmail.com",
    "password": "P21042004p#"
}

TEACHER_CREDENTIALS = {
    "email": "alpha@gmail.com", 
    "password": "P21042004p#"
}

STUDENT_CREDENTIALS = {
    "email": "beta@gmail.com",
    "password": "P21042004p#"
}

def login_user(credentials, role_name):
    """Login and get JWT token"""
    print(f"\n🔐 Logging in {role_name}...")
    response = requests.post(f"{BASE_URL}/auth/login", json=credentials)
    
    if response.status_code == 200:
        data = response.json()
        token = data['data']['jwt_token']
        print(f"✅ {role_name} login successful")
        return token
    else:
        print(f"❌ {role_name} login failed: {response.text}")
        return None

def test_company_location(token, role_name):
    """Test the company location endpoint"""
    print(f"\n📍 Testing company location setup for {role_name}...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Frontend payload format (using exact format from frontend)
    payload = {
        "latitude": 22.6164736,
        "longitude": 88.3785728,
        "name": f"Test School - {role_name}",
        "radius": 100
    }
    
    response = requests.post(f"{BASE_URL}/simple/company/create", json=payload, headers=headers)
    
    print(f"📊 Status Code: {response.status_code}")
    print(f"📄 Response: {response.text}")
    
    if response.status_code == 200:
        print(f"✅ {role_name} can create/update company location")
        return True
    elif response.status_code == 403:
        print(f"❌ {role_name} access denied (expected for students)")
        return False
    else:
        print(f"⚠️ Unexpected response for {role_name}")
        return False

def main():
    print("🧪 TESTING COMPANY LOCATION ACCESS CONTROL")
    print("="*50)
    
    # Test Admin Access
    admin_token = login_user(ADMIN_CREDENTIALS, "Admin")
    if admin_token:
        test_company_location(admin_token, "Admin")
    
    # Test Teacher Access
    teacher_token = login_user(TEACHER_CREDENTIALS, "Teacher")
    if teacher_token:
        test_company_location(teacher_token, "Teacher")
    
    # Test Student Access (should fail)
    student_token = login_user(STUDENT_CREDENTIALS, "Student")
    if student_token:
        test_company_location(student_token, "Student")
    
    print("\n" + "="*50)
    print("🎯 TEST SUMMARY")
    print("Expected Results:")
    print("✅ Admin should have access")
    print("✅ Teacher should have access") 
    print("❌ Student should be denied access")

if __name__ == "__main__":
    main()
