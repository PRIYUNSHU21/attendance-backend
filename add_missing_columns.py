#!/usr/bin/env python3
"""
Add missing columns to attendance_records table
"""

import requests

BASE_URL = "https://attendance-backend-go8h.onrender.com"

def add_missing_columns():
    print("🔧 ADDING MISSING COLUMNS TO ATTENDANCE_RECORDS")
    print("=" * 50)
    
    # Login as admin
    admin_login = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "psaha21.un@gmail.com",
        "password": "P21042004p#"
    })
    
    if admin_login.status_code != 200:
        print("❌ Admin login failed")
        return
    
    admin_token = admin_login.json()['data']['token']
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Add org_id column
    print("1. Adding org_id column...")
    org_id_response = requests.post(f"{BASE_URL}/migration/add-org-id-column", 
                                   headers=headers)
    
    if org_id_response.status_code == 200:
        print("   ✅ org_id column added successfully")
    else:
        print(f"   ⚠️ org_id column: {org_id_response.text}")
    
    # Add location_verified column  
    print("2. Adding location_verified column...")
    location_response = requests.post(f"{BASE_URL}/migration/add-location-verified-column", 
                                    headers=headers)
    
    if location_response.status_code == 200:
        print("   ✅ location_verified column added successfully")
    else:
        print(f"   ⚠️ location_verified column: {location_response.text}")
    
    # Add created_by column
    print("3. Adding created_by column...")
    created_by_response = requests.post(f"{BASE_URL}/migration/add-created-by-column", 
                                      headers=headers)
    
    if created_by_response.status_code == 200:
        print("   ✅ created_by column added successfully")
    else:
        print(f"   ⚠️ created_by column: {created_by_response.text}")
    
    print("\n🎉 MIGRATION COMPLETE!")

if __name__ == "__main__":
    add_missing_columns()
