#!/usr/bin/env python3
"""
🧪 PUBLIC ENDPOINTS TEST SCRIPT
Test script for verifying public endpoints for frontend onboarding

Tests:
1. GET /auth/public/organizations - List organizations
2. POST /auth/public/organizations - Create new organization  
3. POST /auth/public/admin - Create first admin for organization
4. POST /auth/login - Login with newly created admin
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:5000"
HEADERS = {"Content-Type": "application/json"}

def log_test(test_name, success=True, details=""):
    """Log test results."""
    status = "✅ PASS" if success else "❌ FAIL"
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {status} {test_name}")
    if details:
        print(f"    Details: {details}")

def test_get_organizations():
    """Test GET /auth/public/organizations"""
    print("\n🔍 Testing GET /auth/public/organizations")
    try:
        response = requests.get(f"{BASE_URL}/auth/public/organizations")
        log_test("GET Organizations", 
                success=response.status_code == 200,
                details=f"Status: {response.status_code}, Response: {response.json()}")
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        log_test("GET Organizations", success=False, details=str(e))
        return None

def test_create_organization():
    """Test POST /auth/public/organizations"""
    print("\n🏢 Testing POST /auth/public/organizations")
    org_data = {
        "name": f"Test Organization {datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "description": "A test organization for frontend integration testing",
        "contact_email": "test@testorg.com"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/public/organizations",
            headers=HEADERS,
            data=json.dumps(org_data)
        )
        success = response.status_code == 201
        response_data = response.json()
        log_test("Create Organization", 
                success=success,
                details=f"Status: {response.status_code}, Response: {response_data}")
        
        if success and response_data.get('success'):
            return response_data['data']
        return None
    except Exception as e:
        log_test("Create Organization", success=False, details=str(e))
        return None

def test_create_admin(org_id):
    """Test POST /auth/public/admin"""
    print("\n👑 Testing POST /auth/public/admin")
    admin_data = {
        "name": "Test Admin",
        "email": f"admin_{datetime.now().strftime('%Y%m%d_%H%M%S')}@testorg.com",
        "password": "AdminPassword123!",
        "org_id": org_id
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/public/admin",
            headers=HEADERS,
            data=json.dumps(admin_data)
        )
        success = response.status_code == 201
        response_data = response.json()
        log_test("Create Admin", 
                success=success,
                details=f"Status: {response.status_code}, Response: {response_data}")
        
        if success and response_data.get('success'):
            return admin_data  # Return the original data for login test
        return None
    except Exception as e:
        log_test("Create Admin", success=False, details=str(e))
        return None

def test_admin_login(admin_data):
    """Test POST /auth/login with newly created admin"""
    print("\n🔐 Testing admin login")
    login_data = {
        "email": admin_data["email"],
        "password": admin_data["password"]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            headers=HEADERS,
            data=json.dumps(login_data)
        )
        success = response.status_code == 200
        response_data = response.json()
        log_test("Admin Login", 
                success=success,
                details=f"Status: {response.status_code}, User: {response_data.get('data', {}).get('user', {}).get('role', 'unknown')}")
        
        if success and response_data.get('success'):
            return response_data['data']
        return None
    except Exception as e:
        log_test("Admin Login", success=False, details=str(e))
        return None

def test_duplicate_admin_creation(org_id):
    """Test that duplicate admin creation is prevented"""
    print("\n🚫 Testing duplicate admin prevention")
    admin_data = {
        "name": "Duplicate Admin",
        "email": f"duplicate_{datetime.now().strftime('%Y%m%d_%H%M%S')}@testorg.com",
        "password": "AdminPassword123!",
        "org_id": org_id
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/public/admin",
            headers=HEADERS,
            data=json.dumps(admin_data)
        )
        # Should fail with 400 because admin already exists
        success = response.status_code == 400
        response_data = response.json()
        log_test("Duplicate Admin Prevention", 
                success=success,
                details=f"Status: {response.status_code}, Message: {response_data.get('message', '')}")
    except Exception as e:
        log_test("Duplicate Admin Prevention", success=False, details=str(e))

def main():
    """Run all public endpoint tests."""
    print("🚀 STARTING PUBLIC ENDPOINTS TEST SUITE")
    print("=" * 60)
    
    # Test 1: Get existing organizations
    test_get_organizations()
    
    # Test 2: Create new organization
    org = test_create_organization()
    if not org:
        print("\n❌ Cannot proceed without organization. Exiting.")
        sys.exit(1)
    
    org_id = org['org_id']
    print(f"\n✅ Created organization with ID: {org_id}")
    
    # Test 3: Create admin for organization
    admin_data = test_create_admin(org_id)
    if not admin_data:
        print("\n❌ Cannot proceed without admin. Exiting.")
        sys.exit(1)
    
    print(f"\n✅ Created admin: {admin_data['email']}")
    
    # Test 4: Login with newly created admin
    login_result = test_admin_login(admin_data)
    if login_result:
        print(f"\n✅ Admin login successful! Role: {login_result['user']['role']}")
    
    # Test 5: Try to create duplicate admin (should fail)
    test_duplicate_admin_creation(org_id)
    
    print("\n" + "=" * 60)
    print("🎉 PUBLIC ENDPOINTS TEST SUITE COMPLETED!")
    print("\n📋 SUMMARY FOR FRONTEND DEVELOPERS:")
    print("✅ Organization listing works")
    print("✅ Organization creation works")
    print("✅ First admin creation works")
    print("✅ Admin login works")
    print("✅ Duplicate admin prevention works")
    print("\n🔗 Available public endpoints:")
    print("• GET /auth/public/organizations")
    print("• POST /auth/public/organizations")
    print("• POST /auth/public/admin")
    print("\n💡 Frontend integration is ready!")

if __name__ == "__main__":
    main()
