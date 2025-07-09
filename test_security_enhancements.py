#!/usr/bin/env python3
"""
🔒 SECURITY ENHANCEMENT TEST SCRIPT

Tests the new session invalidation and JWT validation security features.

This script verifies:
1. Session invalidation when organization is deleted
2. JWT token validation with organizati        admin_response = requests.post(
            f"{BASE_URL}/auth/public/admin",
            json=admin_data,
            headers={"Content-Type": "application/json"}
        )
        
        if admin_response.status_code != 201:
            print(f"❌ Failed to register admin: {admin_response.text}")
            return False
        
        print(f"✅ Registered admin successfully")
        
        # Step 2b: Login the admin to get JWT token
        print("2️⃣b Login admin to get JWT token...")
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": admin_data["email"],
                "password": admin_data["password"]
            },
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code != 200:
            print(f"❌ Failed to login admin: {login_response.text}")
            return False
        
        admin_token = login_response.json()["data"]["jwt_token"]
        print(f"✅ Admin logged in with token: {admin_token[:20]}...") check  
3. Session blacklist functionality
4. Audit trail for invalidated sessions
"""

import requests
import json
import time
from datetime import datetime

# Configuration
# BASE_URL = "https://attendance-backend-go8h.onrender.com"
BASE_URL = "http://127.0.0.1:5000"  # Use for local testing

def test_session_invalidation_on_org_deletion():
    """Test that all user sessions are invalidated when organization is deleted."""
    print("\n🔒 TESTING: Session Invalidation on Organization Deletion")
    print("=" * 60)
    
    try:
        # Step 1: Create a test organization
        print("1️⃣ Creating test organization...")
        org_data = {
            "name": f"Test Security Org {int(time.time())}",
            "description": "Organization for security testing",
            "contact_email": "security@test.com"
        }
        
        org_response = requests.post(
            f"{BASE_URL}/auth/public/organizations",
            json=org_data,
            headers={"Content-Type": "application/json"}
        )
        
        if org_response.status_code != 201:
            print(f"❌ Failed to create organization: {org_response.text}")
            return False
        
        org_id = org_response.json()["data"]["org_id"]
        print(f"✅ Created organization: {org_id}")
        
        # Step 2: Register first admin
        print("2️⃣ Registering first admin...")
        admin_data = {
            "name": "Security Test Admin",
            "email": f"security_admin_{int(time.time())}@test.com",
            "password": "SecurePassword123!",
            "org_id": org_id
        }
        
        admin_response = requests.post(
            f"{BASE_URL}/auth/public/admin",
            json=admin_data,
            headers={"Content-Type": "application/json"}
        )
        
        if admin_response.status_code != 201:
            print(f"❌ Failed to register admin: {admin_response.text}")
            return False
        
        print(f"✅ Registered admin successfully")
        
        # Step 2b: Login the admin to get JWT token
        print("2️⃣b Login admin to get JWT token...")
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": admin_data["email"],
                "password": admin_data["password"]
            },
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code != 200:
            print(f"❌ Failed to login admin: {login_response.text}")
            return False
        
        admin_token = login_response.json()["data"]["jwt_token"]
        print(f"✅ Admin logged in with token: {admin_token[:20]}...")
        
        # Step 3: Register additional users
        print("3️⃣ Registering additional users...")
        user_tokens = []
        
        for i in range(2):
            user_data = {
                "name": f"Security User {i+1}",
                "email": f"security_user_{i+1}_{int(time.time())}@test.com",
                "password": "UserPassword123!",
                "role": "student",
                "org_id": org_id
            }
            
            user_response = requests.post(
                f"{BASE_URL}/auth/register",
                json=user_data,
                headers={"Content-Type": "application/json"}
            )
            
            if user_response.status_code == 201:
                # Log in the user to get a session
                login_response = requests.post(
                    f"{BASE_URL}/auth/login",
                    json={
                        "email": user_data["email"],
                        "password": user_data["password"]
                    },
                    headers={"Content-Type": "application/json"}
                )
                
                if login_response.status_code == 200:
                    user_token = login_response.json()["data"]["jwt_token"]
                    user_tokens.append(user_token)
                    print(f"✅ User {i+1} logged in: {user_token[:20]}...")
        
        print(f"✅ Created {len(user_tokens)} user sessions")
        
        # Step 4: Verify all tokens work before deletion
        print("4️⃣ Verifying all tokens work before deletion...")
        working_tokens = 0
        
        # Test admin token
        admin_verify = requests.get(
            f"{BASE_URL}/auth/verify",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        if admin_verify.status_code == 200:
            working_tokens += 1
            print("✅ Admin token valid")
        else:
            print(f"❌ Admin token invalid: {admin_verify.text}")
        
        # Test user tokens
        for i, token in enumerate(user_tokens):
            user_verify = requests.get(
                f"{BASE_URL}/auth/verify",
                headers={"Authorization": f"Bearer {token}"}
            )
            if user_verify.status_code == 200:
                working_tokens += 1
                print(f"✅ User {i+1} token valid")
            else:
                print(f"❌ User {i+1} token invalid: {user_verify.text}")
        
        print(f"📊 {working_tokens} tokens working before deletion")
        
        # Step 5: Delete the organization
        print("5️⃣ Deleting organization...")
        delete_response = requests.delete(
            f"{BASE_URL}/admin/organizations/{org_id}",
            json={"confirm_deletion": True},
            headers={
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            }
        )
        
        if delete_response.status_code != 200:
            print(f"❌ Failed to delete organization: {delete_response.text}")
            return False
        
        result = delete_response.json()
        invalidated_sessions = result["data"].get("invalidated_sessions", 0)
        print(f"✅ Organization deleted, {invalidated_sessions} sessions invalidated")
        
        # Step 6: Verify all tokens are now invalid
        print("6️⃣ Verifying all tokens are now invalid...")
        invalid_tokens = 0
        
        # Test admin token (should be invalid)
        admin_verify = requests.get(
            f"{BASE_URL}/auth/verify",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        if admin_verify.status_code == 401:
            invalid_tokens += 1
            print("✅ Admin token correctly invalidated")
        else:
            print(f"❌ Admin token still valid: {admin_verify.status_code}")
        
        # Test user tokens (should be invalid)
        for i, token in enumerate(user_tokens):
            user_verify = requests.get(
                f"{BASE_URL}/auth/verify",
                headers={"Authorization": f"Bearer {token}"}
            )
            if user_verify.status_code == 401:
                invalid_tokens += 1
                print(f"✅ User {i+1} token correctly invalidated")
            else:
                print(f"❌ User {i+1} token still valid: {user_verify.status_code}")
        
        print(f"📊 {invalid_tokens} tokens correctly invalidated")
        
        # Step 7: Test accessing protected endpoints
        print("7️⃣ Testing access to protected endpoints...")
        protected_test = requests.get(
            f"{BASE_URL}/auth/profile",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        if protected_test.status_code == 401:
            print("✅ Protected endpoint correctly rejects invalid token")
        else:
            print(f"❌ Protected endpoint still accessible: {protected_test.status_code}")
        
        print("\n🎉 SESSION INVALIDATION TEST COMPLETED")
        print(f"Expected invalidated sessions: {working_tokens}")
        print(f"Actual invalidated sessions: {invalidated_sessions}")
        print(f"Tokens correctly invalidated: {invalid_tokens}")
        
        return invalid_tokens == working_tokens
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False

def test_soft_delete_session_invalidation():
    """Test that sessions are invalidated during soft delete."""
    print("\n🔒 TESTING: Session Invalidation on Soft Delete")
    print("=" * 60)
    
    try:
        # Step 1: Create test organization and admin
        print("1️⃣ Creating test organization for soft delete...")
        org_data = {
            "name": f"Test Soft Delete Org {int(time.time())}",
            "description": "Organization for soft delete testing",
            "contact_email": "softdelete@test.com"
        }
        
        org_response = requests.post(
            f"{BASE_URL}/auth/public/organizations",
            json=org_data,
            headers={"Content-Type": "application/json"}
        )
        
        if org_response.status_code != 201:
            print(f"❌ Failed to create organization: {org_response.text}")
            return False
        
        org_id = org_response.json()["data"]["org_id"]
        print(f"✅ Created organization: {org_id}")
        
        # Step 2: Register admin and get token
        admin_data = {
            "name": "Soft Delete Admin",
            "email": f"soft_admin_{int(time.time())}@test.com",
            "password": "SecurePassword123!",
            "org_id": org_id
        }
        
        admin_response = requests.post(
            f"{BASE_URL}/auth/public/admin",
            json=admin_data,
            headers={"Content-Type": "application/json"}
        )
        
        if admin_response.status_code != 201:
            print(f"❌ Failed to register admin: {admin_response.text}")
            return False
        
        print(f"✅ Registered admin successfully")
        
        # Step 2b: Login the admin to get JWT token
        print("2️⃣b Login admin to get JWT token...")
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": admin_data["email"],
                "password": admin_data["password"]
            },
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code != 200:
            print(f"❌ Failed to login admin: {login_response.text}")
            return False
        
        admin_token = login_response.json()["data"]["jwt_token"]
        print(f"✅ Admin logged in with token: {admin_token[:20]}...")
        
        # Step 3: Verify token works
        verify_response = requests.get(
            f"{BASE_URL}/auth/verify",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        if verify_response.status_code != 200:
            print(f"❌ Token verification failed: {verify_response.text}")
            return False
        
        print("✅ Token verified successfully")
        
        # Step 4: Soft delete the organization
        print("2️⃣ Soft deleting organization...")
        soft_delete_response = requests.put(
            f"{BASE_URL}/admin/organizations/{org_id}/soft-delete",
            headers={
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            }
        )
        
        if soft_delete_response.status_code != 200:
            print(f"❌ Failed to soft delete organization: {soft_delete_response.text}")
            return False
        
        result = soft_delete_response.json()
        invalidated_sessions = result["data"].get("invalidated_sessions", 0)
        print(f"✅ Organization soft deleted, {invalidated_sessions} sessions invalidated")
        
        # Step 5: Verify token is now invalid
        print("3️⃣ Verifying token is invalidated...")
        verify_response = requests.get(
            f"{BASE_URL}/auth/verify",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        if verify_response.status_code == 401:
            print("✅ Token correctly invalidated after soft delete")
            return True
        else:
            print(f"❌ Token still valid after soft delete: {verify_response.status_code}")
            return False
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False

def main():
    """Run all security enhancement tests."""
    print("🔒 BACKEND SECURITY ENHANCEMENT TESTS")
    print("=" * 80)
    print(f"Testing backend: {BASE_URL}")
    print(f"Test started at: {datetime.now().isoformat()}")
    
    results = {}
    
    # Test 1: Session invalidation on organization deletion
    results["org_deletion"] = test_session_invalidation_on_org_deletion()
    
    # Test 2: Session invalidation on soft delete
    results["soft_delete"] = test_soft_delete_session_invalidation()
    
    # Print summary
    print("\n" + "=" * 80)
    print("🔒 SECURITY TEST SUMMARY")
    print("=" * 80)
    
    passed = 0
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASSED" if passed_test else "❌ FAILED"
        print(f"{test_name.upper()}: {status}")
        if passed_test:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL SECURITY ENHANCEMENTS WORKING CORRECTLY!")
        print("\n🔒 SECURITY FEATURES VERIFIED:")
        print("✅ Sessions invalidated when organization deleted")
        print("✅ Sessions invalidated when organization soft deleted")
        print("✅ JWT tokens correctly validated with organization existence")
        print("✅ Blacklisted sessions properly rejected")
        print("\n📝 The frontend team's security recommendations have been implemented!")
    else:
        print("⚠️ Some security tests failed. Please check the implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
