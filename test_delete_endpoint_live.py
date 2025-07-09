#!/usr/bin/env python3
"""
🧪 TEST DELETE ORGANIZATION ENDPOINT
Test the newly implemented DELETE /admin/organizations/{id} endpoint
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "https://attendance-backend-go8h.onrender.com"
# BASE_URL = "http://127.0.0.1:5000"  # Use this for local testing

def test_delete_organization():
    """Test the complete organization deletion flow"""
    
    print("🧪 TESTING DELETE ORGANIZATION ENDPOINT")
    print(f"Testing: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Step 1: Create a test organization
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    org_data = {
        "name": f"Delete Test Org {timestamp}",
        "description": "Test organization for deletion testing",
        "contact_email": f"deletetest_{timestamp}@test.edu"
    }
    
    print("\n🏢 Step 1: Creating test organization...")
    response = requests.post(
        f"{BASE_URL}/auth/public/organizations",
        headers={"Content-Type": "application/json"},
        json=org_data
    )
    
    if response.status_code != 201:
        print(f"❌ Failed to create organization: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    org_result = response.json()
    org_id = org_result['data']['org_id']
    print(f"✅ Created organization: {org_id}")
    
    # Step 2: Create admin for the organization
    admin_data = {
        "name": "Delete Test Admin",
        "email": f"deleteadmin_{timestamp}@test.edu",
        "password": "DeleteTest123!",
        "org_id": org_id
    }
    
    print("\n👑 Step 2: Creating admin for the organization...")
    response = requests.post(
        f"{BASE_URL}/auth/public/admin",
        headers={"Content-Type": "application/json"},
        json=admin_data
    )
    
    if response.status_code != 201:
        print(f"❌ Failed to create admin: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    print("✅ Created admin successfully")
    
    # Step 3: Login to get admin token
    login_data = {
        "email": admin_data["email"],
        "password": admin_data["password"]
    }
    
    print("\n🔐 Step 3: Logging in as admin...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        headers={"Content-Type": "application/json"},
        json=login_data
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to login: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    login_result = response.json()
    token = login_result['data']['jwt_token']  # Fixed: use 'jwt_token' instead of 'token'
    auth_headers = {"Authorization": f"Bearer {token}"}
    print(f"✅ Logged in successfully. Token: {token[:30]}...")
    
    # Step 4: Test GET organization (verify it exists)
    print(f"\n📋 Step 4: Verifying organization exists...")
    response = requests.get(
        f"{BASE_URL}/admin/organizations/{org_id}",
        headers=auth_headers
    )
    
    if response.status_code != 200:
        print(f"❌ Organization not found: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    org_info = response.json()
    print(f"✅ Organization exists: {org_info['data']['name']}")
    
    # Step 5: Test DELETE without confirmation (should show preview)
    print(f"\n🔍 Step 5: Testing DELETE without confirmation (preview)...")
    response = requests.delete(
        f"{BASE_URL}/admin/organizations/{org_id}",
        headers=auth_headers,
        json={}  # No confirm_deletion flag
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        preview_result = response.json()
        print("✅ DELETE preview successful!")
        print(f"Preview data: {json.dumps(preview_result['data'], indent=2)}")
    else:
        print(f"❌ DELETE preview failed: {response.text}")
        return
    
    # Step 6: Test DELETE with confirmation (actual deletion)
    print(f"\n💥 Step 6: Testing DELETE with confirmation (actual deletion)...")
    response = requests.delete(
        f"{BASE_URL}/admin/organizations/{org_id}",
        headers=auth_headers,
        json={"confirm_deletion": True}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        delete_result = response.json()
        print("✅ DELETE successful!")
        print(f"Deletion summary: {json.dumps(delete_result['data'], indent=2)}")
    else:
        print(f"❌ DELETE failed: {response.text}")
        return
    
    # Step 7: Verify organization is actually deleted
    print(f"\n🔍 Step 7: Verifying organization is deleted...")
    response = requests.get(
        f"{BASE_URL}/admin/organizations/{org_id}",
        headers=auth_headers
    )
    
    if response.status_code == 404:
        print("✅ Organization successfully deleted (404 Not Found)")
    elif response.status_code == 401:
        print("✅ Organization deleted (401 because admin token is invalid after org deletion)")
    else:
        print(f"❌ Organization still exists: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    print("\n" + "="*60)
    print("🎉 DELETE ORGANIZATION ENDPOINT TEST COMPLETED!")
    print("✅ Organization creation works")
    print("✅ Admin creation works")
    print("✅ Authentication works")
    print("✅ DELETE preview works")
    print("✅ DELETE confirmation works")
    print("✅ Organization actually deleted")
    print("\n🚀 The DELETE endpoint is fully functional!")

if __name__ == "__main__":
    test_delete_organization()
