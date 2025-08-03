#!/usr/bin/env python3
"""
Check production database schema for attendance_records table
"""
import requests

BASE_URL = "https://attendance-backend-go8h.onrender.com"

def check_attendance_schema():
    print("🔍 CHECKING ATTENDANCE RECORDS SCHEMA")
    print("=" * 40)
    
    # Use the migration endpoint to check schema
    admin_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "psaha21.un@gmail.com", 
        "password": "P21042004p#"
    })
    
    admin_token = admin_response.json()["data"]["jwt_token"]
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Check if we have migration endpoints
    schema_response = requests.get(f"{BASE_URL}/migration/check-schema", headers=headers)
    
    print(f"Schema check: {schema_response.status_code}")
    print(f"Response: {schema_response.text}")

if __name__ == "__main__":
    check_attendance_schema()
