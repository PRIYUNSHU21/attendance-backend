#!/usr/bin/env python3
"""
Debug login response
"""

import requests
import json
from datetime import datetime

BASE_URL = "https://attendance-backend-go8h.onrender.com"

# Create test organization and admin first
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
org_data = {
    "name": f"Debug Test Org {timestamp}",
    "description": "Debug test organization",
    "contact_email": f"debugtest_{timestamp}@test.edu"
}

print("Creating organization...")
response = requests.post(f"{BASE_URL}/auth/public/organizations", json=org_data)
print(f"Org creation status: {response.status_code}")
if response.status_code == 201:
    org_result = response.json()
    org_id = org_result['data']['org_id']
    print(f"Org ID: {org_id}")
    
    # Create admin
    admin_data = {
        "name": "Debug Admin",
        "email": f"debugadmin_{timestamp}@test.edu",
        "password": "DebugTest123!",
        "org_id": org_id
    }
    
    print("Creating admin...")
    response = requests.post(f"{BASE_URL}/auth/public/admin", json=admin_data)
    print(f"Admin creation status: {response.status_code}")
    
    if response.status_code == 201:
        # Try login
        login_data = {
            "email": admin_data["email"],
            "password": admin_data["password"]
        }
        
        print("Attempting login...")
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"Login status: {response.status_code}")
        print(f"Login response: {response.text}")
    else:
        print(f"Admin creation failed: {response.text}")
else:
    print(f"Org creation failed: {response.text}")
