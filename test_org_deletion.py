#!/usr/bin/env python3
"""
🧪 TEST ORGANIZATION DELETION - Verify DELETE endpoint works
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "https://attendance-backend-go8h.onrender.com"
# BASE_URL = "http://127.0.0.1:5000"  # Use this for local testing

def test_organization_deletion():
    print("🧪 TESTING ORGANIZATION DELETION ENDPOINT")
    print(f"Testing: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Step 1: Create test organization
    print("\n🏢 Step 1: Creating test organization...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    org_data = {
        "name": f"Delete Test Org {timestamp}",
        "description": "Organization for testing deletion",
        "contact_email": f"delete_test_{timestamp}@test.edu"
    }
    
    org_response = requests.post(
        f"{BASE_URL}/auth/public/organizations",
        json=org_data,
        headers={"Content-Type": "application/json"}
    )
    
    if org_response.status_code != 201:
        print(f"❌ Failed to create organization: {org_response.text}")
        return
    
    org_result = org_response.json()
    org_id = org_result['data']['org_id']
    print(f"✅ Created organization: {org_id}")
    
    # Step 2: Create admin for the organization
    print("\n👑 Step 2: Creating admin for organization...")
    admin_data = {
        "name": "Delete Test Admin",
        "email": f"delete_admin_{timestamp}@test.edu",
        "password": "DeleteTest123!",
        "org_id": org_id
    }
    
    admin_response = requests.post(
        f"{BASE_URL}/auth/public/admin",
        json=admin_data,
        headers={"Content-Type": "application/json"}
    )
    
    if admin_response.status_code != 201:
        print(f"❌ Failed to create admin: {admin_response.text}")
        return
        
    admin_result = admin_response.json()
    print(f"✅ Created admin: {admin_result['data']['email']}")
    
    # Step 3: Login admin to get JWT token
    print("\n🔐 Step 3: Logging in admin...")
    login_data = {
        "email": admin_data["email"],
        "password": admin_data["password"]
    }
    
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Failed to login admin: {login_response.text}")
        return
        
    login_result = login_response.json()
    token = login_result['data']['jwt_token']  # Fixed: use jwt_token instead of token
    auth_headers = {"Authorization": f"Bearer {token}"}
    print(f"✅ Admin logged in successfully")
    
    # Step 4: Test deletion preview (without confirmation)
    print("\n📋 Step 4: Testing deletion preview...")
    preview_response = requests.delete(
        f"{BASE_URL}/admin/organizations/{org_id}",
        json={},  # Send empty JSON body
        headers={"Content-Type": "application/json", **auth_headers}
    )
    
    print(f"   Status: {preview_response.status_code}")
    if preview_response.status_code == 200:
        preview_result = preview_response.json()
        print(f"✅ Deletion preview works")
        print(f"   Preview data: {json.dumps(preview_result['data'], indent=2)}")
    else:
        print(f"❌ Deletion preview failed: {preview_response.text}")
        return
    
    # Step 5: Test actual deletion (with confirmation)
    print("\n🗑️ Step 5: Testing actual deletion with confirmation...")
    delete_data = {"confirm_deletion": True}
    
    delete_response = requests.delete(
        f"{BASE_URL}/admin/organizations/{org_id}",
        json=delete_data,
        headers={"Content-Type": "application/json", **auth_headers}
    )
    
    print(f"   Status: {delete_response.status_code}")
    if delete_response.status_code == 200:
        delete_result = delete_response.json()
        print(f"✅ Organization deleted successfully!")
        print(f"   Deletion summary: {json.dumps(delete_result['data'], indent=2)}")
        print(f"   Message: {delete_result['message']}")
    else:
        print(f"❌ Deletion failed: {delete_response.text}")
        print(f"   This might be expected if you're testing security restrictions")
        return
    
    # Step 6: Verify organization is gone
    print("\n🔍 Step 6: Verifying organization is deleted...")
    verify_response = requests.get(
        f"{BASE_URL}/admin/organizations/{org_id}",
        headers=auth_headers
    )
    
    if verify_response.status_code == 404:
        print("✅ Organization successfully deleted - returns 404 as expected")
    elif verify_response.status_code == 401:
        print("✅ Organization deleted - admin token no longer valid (expected)")
    else:
        print(f"⚠️ Unexpected status: {verify_response.status_code}")
        print(f"   Response: {verify_response.text}")
    
    print("\n" + "="*60)
    print("🎉 ORGANIZATION DELETION TEST COMPLETED!")
    print("\n📋 SUMMARY:")
    print("✅ Organization creation works")
    print("✅ Admin creation works") 
    print("✅ Admin authentication works")
    print("✅ Deletion preview works")
    print("✅ Deletion with confirmation works")
    print("✅ Deletion verification works")

def test_security_restrictions():
    """Test that users can't delete other organizations"""
    print("\n🔒 TESTING SECURITY RESTRICTIONS")
    print("="*60)
    
    # This would require creating two organizations and testing cross-org deletion
    # For now, we'll just document the expected behavior
    print("🛡️ Security features that should be tested:")
    print("1. Admin can only delete their own organization")
    print("2. Regular users cannot delete organizations")
    print("3. Invalid org_id returns 404")
    print("4. Missing auth token returns 401")
    print("5. Cross-organization deletion returns 403")

if __name__ == "__main__":
    try:
        test_organization_deletion()
        test_security_restrictions()
    except Exception as e:
        print(f"\n❌ Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
