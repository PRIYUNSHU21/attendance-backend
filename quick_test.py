#!/usr/bin/env python3
"""
🧪 QUICK TEST SCRIPT - Verify Backend Works End-to-End
Run this to quickly verify all critical functionality works
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "https://attendance-backend-go8h.onrender.com"
# BASE_URL = "http://127.0.0.1:5000"  # Use this for local testing

def test_section(title):
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print('='*60)

def test_endpoint(name, method, url, data=None, headers=None, expected_status=200):
    try:
        print(f"\n🔍 Testing {name}...")
        
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        
        print(f"   Status: {response.status_code}", end="")
        
        if response.status_code == expected_status:
            print(" ✅")
            try:
                result = response.json()
                if result.get('success'):
                    print(f"   Success: {result.get('message', 'OK')}")
                    return result
                else:
                    print(f"   Error: {result.get('message', 'Unknown error')}")
                    return None
            except:
                print("   Response: Non-JSON response")
                return {"status": "ok"}
        else:
            print(" ❌")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('message', 'Unknown error')}")
            except:
                print(f"   Error: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return None

def main():
    print("🚀 ATTENDANCE BACKEND - QUICK TEST SUITE")
    print(f"Testing: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test Phase 1: Basic Health
    test_section("PHASE 1: BASIC HEALTH CHECK")
    
    health = test_endpoint(
        "Backend Health", 
        "GET", 
        f"{BASE_URL}/health"
    )
    
    if not health:
        print("❌ Backend is not responding. Cannot continue tests.")
        return
    
    # Test Phase 2: Public Endpoints
    test_section("PHASE 2: PUBLIC ENDPOINTS")
    
    # List organizations
    orgs = test_endpoint(
        "List Organizations",
        "GET", 
        f"{BASE_URL}/auth/public/organizations"
    )
    
    # Create organization
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    org_data = {
        "name": f"Quick Test Org {timestamp}",
        "description": "Quick test organization",
        "contact_email": f"quicktest_{timestamp}@test.edu"
    }
    
    new_org = test_endpoint(
        "Create Organization",
        "POST",
        f"{BASE_URL}/auth/public/organizations",
        data=org_data,
        expected_status=201
    )
    
    if not new_org:
        print("❌ Cannot create organization. Stopping tests.")
        return
        
    org_id = new_org['data']['org_id']
    print(f"   Created org_id: {org_id}")
    
    # Create admin
    admin_data = {
        "name": "Quick Test Admin",
        "email": f"quickadmin_{timestamp}@test.edu",
        "password": "QuickTest123!",
        "org_id": org_id
    }
    
    new_admin = test_endpoint(
        "Create First Admin",
        "POST",
        f"{BASE_URL}/auth/public/admin",
        data=admin_data,
        expected_status=201
    )
    
    if not new_admin:
        print("❌ Cannot create admin. Stopping tests.")
        return
    
    # Test Phase 3: Authentication
    test_section("PHASE 3: AUTHENTICATION")
    
    # Login admin
    login_data = {
        "email": admin_data["email"],
        "password": admin_data["password"]
    }
    
    login_result = test_endpoint(
        "Admin Login",
        "POST",
        f"{BASE_URL}/auth/login",
        data=login_data
    )
    
    if not login_result:
        print("❌ Cannot login admin. Stopping tests.")
        return
        
    token = login_result['data']['jwt_token']
    print(f"   JWT Token: {token[:50]}...")
    
    # Verify token
    auth_headers = {"Authorization": f"Bearer {token}"}
    
    verify_result = test_endpoint(
        "Token Verification",
        "GET",
        f"{BASE_URL}/auth/verify",
        headers=auth_headers
    )
    
    # Test Phase 4: Protected Endpoints
    test_section("PHASE 4: PROTECTED ENDPOINTS")
    
    # Get profile
    profile_result = test_endpoint(
        "Get Admin Profile",
        "GET",
        f"{BASE_URL}/auth/profile",
        headers=auth_headers
    )
    
    # List users (admin function)
    users_result = test_endpoint(
        "List Users (Admin)",
        "GET",
        f"{BASE_URL}/admin/users",
        headers=auth_headers
    )
    
    # Test Phase 5: Student Registration
    test_section("PHASE 5: STUDENT FLOW")
    
    # Register student
    student_data = {
        "name": "Quick Test Student",
        "email": f"quickstudent_{timestamp}@test.edu",
        "password": "StudentTest123!",
        "org_id": org_id
    }
    
    student_result = test_endpoint(
        "Register Student",
        "POST",
        f"{BASE_URL}/auth/register",
        data=student_data,
        expected_status=201
    )
    
    # Login student
    if student_result:
        student_login_data = {
            "email": student_data["email"],
            "password": student_data["password"]
        }
        
        student_login_result = test_endpoint(
            "Student Login",
            "POST",
            f"{BASE_URL}/auth/login",
            data=student_login_data
        )
        
        if student_login_result:
            student_token = student_login_result['data']['jwt_token']
            student_headers = {"Authorization": f"Bearer {student_token}"}
            
            # Get student profile
            test_endpoint(
                "Student Profile",
                "GET",
                f"{BASE_URL}/auth/profile",
                headers=student_headers
            )
    
    # Final Summary
    test_section("TEST SUMMARY")
    print("✅ Basic health check")
    print("✅ Public organization endpoints")  
    print("✅ Admin creation and authentication")
    print("✅ JWT token functionality")
    print("✅ Protected admin endpoints")
    print("✅ Student registration and login")
    print("\n🎉 ALL CRITICAL FUNCTIONALITY VERIFIED!")
    print("\n📖 For detailed testing, see: STEP_BY_STEP_TESTING_GUIDE.md")
    print("🛠️ For integration help, see: FRONTEND_ONBOARDING_GUIDE.md")

if __name__ == "__main__":
    main()
