#!/usr/bin/env python3
"""
🔍 DEBUG TEST - Check what's in the API responses
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def test_admin_registration():
    """Test admin registration endpoint."""
    print("🔍 Testing admin registration...")
    
    try:
        # Create test organization
        org_data = {
            "name": f"Debug Test Org {int(time.time())}",
            "description": "Debug test organization",
            "contact_email": "debug@test.com"
        }
        
        org_response = requests.post(
            f"{BASE_URL}/auth/public/organizations",
            json=org_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Org creation status: {org_response.status_code}")
        print(f"Org response: {org_response.text}")
        
        if org_response.status_code != 201:
            return False
        
        org_id = org_response.json()["data"]["org_id"]
        
        # Register admin
        admin_data = {
            "name": "Debug Admin",
            "email": f"debug_admin_{int(time.time())}@test.com",
            "password": "DebugPassword123!",
            "org_id": org_id
        }
        
        admin_response = requests.post(
            f"{BASE_URL}/auth/public/admin",
            json=admin_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Admin registration status: {admin_response.status_code}")
        print(f"Admin response: {admin_response.text}")
        
        if admin_response.status_code == 201:
            data = admin_response.json()["data"]
            print(f"Keys in response: {list(data.keys())}")
            return True
        
        return False
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_admin_registration()
