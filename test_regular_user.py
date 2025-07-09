import requests
import json

# Test regular user registration
url = "http://127.0.0.1:5000/auth/register"
data = {
    "name": "Regular User",
    "email": "user@testorg.com",
    "password": "UserPass123!",
    "org_id": "b7d03462-7491-46a5-8600-f1cc16225ae7"
}

response = requests.post(url, headers={"Content-Type": "application/json"}, json=data)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
