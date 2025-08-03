#!/usr/bin/env python3
"""Quick test of login credentials"""

import requests

BASE_URL = "https://attendance-backend-go8h.onrender.com"

# Test all credentials
credentials = [
    {"name": "Admin", "email": "psaha21.un@gmail.com", "password": "P21042004p#"},
    {"name": "Teacher", "email": "alpha@gmail.com", "password": "P21042004p#"}, 
    {"name": "Student", "email": "beta@gmail.com", "password": "P21042004p#"}
]

print("🔐 TESTING ALL LOGIN CREDENTIALS")
print("=" * 40)

for cred in credentials:
    print(f"\n👤 Testing {cred['name']} login...")
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": cred['email'],
            "password": cred['password']
        })
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()['data']
            print(f"✅ SUCCESS: {data['user']['name']} ({data['user']['role']})")
        else:
            print(f"❌ FAILED: {response.text}")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

print("\n" + "=" * 40)
