#!/usr/bin/env python3
"""
Test script to verify organization endpoint authentication fix
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_organization_endpoints():
    print("🧪 Testing Organization Endpoint Authentication Fix")
    print("=" * 60)
    
    # Step 1: Login as admin to get token
    print("1. 🔑 Admin Login...")
    login_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "admin@testuni.edu",
        "password": "admin123"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return
    
    login_data = login_response.json()
    print(f"Login response: {login_data}")
    
    token = login_data["data"]["jwt_token"]
    print(f"✅ Login successful, token obtained")
    
    # Headers with authorization
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Step 2: Test GET /admin/organizations (should work)
    print("\n2. 📋 Testing GET /admin/organizations...")
    get_response = requests.get(f"{BASE_URL}/admin/organizations", headers=headers)
    print(f"Status: {get_response.status_code}")
    if get_response.status_code == 200:
        print("✅ GET organizations works correctly")
    else:
        print(f"❌ GET failed: {get_response.text}")
    
    # Step 3: Test POST /admin/organizations (the fixed endpoint)
    print("\n3. 🏢 Testing POST /admin/organizations (FIXED ENDPOINT)...")
    org_data = {
        "name": "Test Organization",
        "description": "Test organization created by fix verification",
        "address": "123 Test Street",
        "contact_email": "test@testorg.com",
        "contact_phone": "+1234567890"
    }
    
    post_response = requests.post(f"{BASE_URL}/admin/organizations", 
                                  headers=headers, 
                                  json=org_data)
    
    print(f"Status: {post_response.status_code}")
    if post_response.status_code == 201:
        print("✅ POST organizations now works correctly!")
        print(f"Created organization: {post_response.json()['data']['name']}")
    elif post_response.status_code == 401:
        print("❌ Still getting authentication error - fix didn't work")
    else:
        print(f"❌ POST failed with: {post_response.text}")
    
    # Step 4: Test without token (should fail)
    print("\n4. 🔒 Testing POST without token (should fail)...")
    no_auth_response = requests.post(f"{BASE_URL}/admin/organizations", 
                                     json=org_data)
    
    if no_auth_response.status_code == 401:
        print("✅ Correctly blocks requests without authentication")
    else:
        print(f"❌ Security issue: {no_auth_response.status_code}")
    
    print("\n" + "=" * 60)
    print("🎯 Organization endpoint authentication test complete!")

if __name__ == "__main__":
    test_organization_endpoints()
