"""
🐛 Test Production Database Login
This script will test login against the actual production API
"""
import requests
import json

# Test with production API
PRODUCTION_URL = "https://attendance-backend-go8h.onrender.com"

print("🌐 Testing production API login...")
print(f"URL: {PRODUCTION_URL}")

# Test admin login
try:
    response = requests.post(f"{PRODUCTION_URL}/auth/login", 
        json={
            "email": "psaha21.un@gmail.com",
            "password": "P21042004p#"
        },
        timeout=30
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Login successful!")
        data = response.json()
        print(f"User: {data.get('user', {}).get('name', 'Unknown')}")
        print(f"Role: {data.get('user', {}).get('role', 'Unknown')}")
        print(f"Token: {data.get('token', 'None')[:50]}...")
    else:
        print("❌ Login failed")
        print(f"Response: {response.text}")
        
except requests.exceptions.RequestException as e:
    print(f"❌ Request failed: {e}")

# Test the actual health check
try:
    print("\n🏥 Testing health check...")
    response = requests.get(f"{PRODUCTION_URL}/health", timeout=10)
    print(f"Health Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Health Response: {response.json()}")
    else:
        print(f"Health Error: {response.text}")
except Exception as e:
    print(f"❌ Health check failed: {e}")
