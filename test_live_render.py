import requests
import json
import datetime

# Test the live Render backend
BASE_URL = "https://attendance-backend-go8h.onrender.com"

print("🧪 TESTING LIVE RENDER BACKEND")
print("=" * 60)

# Test 1: Health check
print("\n🔍 Testing Health Check")
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"✅ Status: {response.status_code}")
    print(f"✅ Response: {response.json()}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Public endpoints
print("\n🏢 Testing Public Organizations Endpoint")
try:
    response = requests.get(f"{BASE_URL}/auth/public/organizations")
    print(f"✅ Status: {response.status_code}")
    data = response.json()
    print(f"✅ Organizations available: {len(data.get('data', []))}")
    print(f"✅ Response: {data}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Create test organization
print("\n🏗️ Testing Organization Creation")
org_data = {
    "name": f"Test Organization {datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
    "description": "A test organization for live testing",
    "contact_email": "test@livetest.com"
}

try:
    response = requests.post(
        f"{BASE_URL}/auth/public/organizations",
        headers={"Content-Type": "application/json"},
        json=org_data
    )
    print(f"✅ Status: {response.status_code}")
    org_result = response.json()
    print(f"✅ Organization created: {org_result}")
    
    if response.status_code == 201:
        org_id = org_result['data']['org_id']
        print(f"✅ New org_id: {org_id}")
        
        # Test 4: Create admin for the organization
        print("\n👑 Testing Admin Creation")
        admin_data = {
            "name": "Test Admin",
            "email": f"admin_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}@livetest.com",
            "password": "AdminPass123!",
            "org_id": org_id
        }
        
        admin_response = requests.post(
            f"{BASE_URL}/auth/public/admin",
            headers={"Content-Type": "application/json"},
            json=admin_data
        )
        print(f"✅ Status: {admin_response.status_code}")
        admin_result = admin_response.json()
        print(f"✅ Admin created: {admin_result}")
        
        if admin_response.status_code == 201:
            # Test 5: Login with new admin
            print("\n🔐 Testing Admin Login")
            login_data = {
                "email": admin_data["email"],
                "password": admin_data["password"]
            }
            
            login_response = requests.post(
                f"{BASE_URL}/auth/login",
                headers={"Content-Type": "application/json"},
                json=login_data
            )
            print(f"✅ Status: {login_response.status_code}")
            login_result = login_response.json()
            print(f"✅ Login successful: {login_result.get('success', False)}")
            
            if login_response.status_code == 200:
                token = login_result['data']['token']
                user_org_id = login_result['data']['user']['org_id']
                print(f"✅ JWT Token received (length: {len(token)})")
                print(f"✅ User org_id in response: {user_org_id}")
                
                # Test 6: Test admin endpoints with organization filtering
                print("\n🔒 Testing Admin Endpoints (Organization Filtering)")
                headers = {"Authorization": f"Bearer {token}"}
                
                # Test users endpoint
                users_response = requests.get(f"{BASE_URL}/admin/users", headers=headers)
                print(f"✅ Admin users endpoint status: {users_response.status_code}")
                if users_response.status_code == 200:
                    users_data = users_response.json()
                    print(f"✅ Users returned: {len(users_data.get('data', []))}")
                    # Verify all users belong to the same organization
                    users = users_data.get('data', [])
                    if users:
                        user_orgs = set(user.get('org_id') for user in users)
                        print(f"✅ Organization isolation test: {len(user_orgs)} unique org_ids")
                        if len(user_orgs) == 1 and list(user_orgs)[0] == user_org_id:
                            print("✅ ✅ ORGANIZATION ISOLATION WORKING CORRECTLY!")
                        else:
                            print("❌ ❌ ORGANIZATION ISOLATION FAILED!")
                    else:
                        print("✅ No users yet (expected for new organization)")
                
    else:
        print(f"❌ Organization creation failed: {org_result}")
        
except Exception as e:
    print(f"❌ Error during live testing: {e}")

print("\n" + "=" * 60)
print("🎉 LIVE TESTING COMPLETED")
