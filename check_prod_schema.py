#!/usr/bin/env python3
"""
Check production attendance_records table schema
"""

import requests

BASE_URL = "https://attendance-backend-go8h.onrender.com"

def check_attendance_records_schema():
    print("🔍 CHECKING PRODUCTION ATTENDANCE_RECORDS SCHEMA")
    print("=" * 50)
    
    # Login as admin to access migration endpoints
    admin_login = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "psaha21.un@gmail.com",
        "password": "P21042004p#"
    })
    
    if admin_login.status_code != 200:
        print("❌ Admin login failed")
        return
    
    admin_token = admin_login.json()['data']['token']
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Check attendance_records schema
    schema_response = requests.get(f"{BASE_URL}/migration/check-attendance-records-schema", 
                                 headers=headers)
    
    if schema_response.status_code == 200:
        schema_data = schema_response.json()
        print("✅ Current attendance_records schema:")
        for col in schema_data['data']['columns']:
            print(f"   📋 {col['name']}: {col['type']} ({'nullable' if col['nullable'] == 'YES' else 'not null'})")
    else:
        print(f"❌ Schema check failed: {schema_response.text}")

if __name__ == "__main__":
    check_attendance_records_schema()
