#!/usr/bin/env python3
"""
Test production schema via API
"""
import requests
import time

BASE_URL = "https://attendance-backend-go8h.onrender.com"
ADMIN_CREDS = {"email": "psaha21.un@gmail.com", "password": "P21042004p#"}

def test_migration_endpoint():
    print("🔧 TESTING MIGRATION ENDPOINT")
    print("=" * 40)
    
    # Wait for deployment
    print("⏳ Waiting for deployment...")
    time.sleep(20)
    
    # Login admin
    print("1️⃣ Logging in admin...")
    login_response = requests.post(f"{BASE_URL}/auth/login", json=ADMIN_CREDS)
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    token = login_response.json()["data"]["jwt_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Admin logged in")
    
    # Check schema
    print("\n2️⃣ Checking schema...")
    response = requests.get(f"{BASE_URL}/migration/check-schema", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    test_migration_endpoint()
