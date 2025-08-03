import requests
import json

BASE_URL = "http://localhost:5000/simple"

# First we need to login to get a token
def test_company_create():
    print("Testing company location setup...")
    
    # Step 1: Login to get token
    print("1. Login...")
    login_url = "http://localhost:5000/auth/login"
    login_payload = {
        "email": "admin@example.com", 
        "password": "password123"
    }
    
    try:
        login_response = requests.post(login_url, json=login_payload)
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(login_response.text)
            return
        
        token = login_response.json().get('data', {}).get('jwt_token')
        if not token:
            print("❌ No token returned from login")
            return
            
        print("Login successful!")
        
        # Step 2: Set company location
        print("2. Setting company location...")
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Use the exact payload format from the frontend
        location_payload = {
            "latitude": 22.6164736,
            "longitude": 88.3785728,
            "name": "SAHA",
            "radius": 100
        }
        
        print("Request to company/create endpoint:")
        print(json.dumps(location_payload, indent=4))
        
        response = requests.post(f"{BASE_URL}/company/create", 
                                headers=headers, 
                                json=location_payload)
        
        print(f"Response: {response.status_code}")
        print("Response Body:")
        print(json.dumps(response.json(), indent=4))
        
        if response.status_code == 200 and response.json().get('success'):
            print("✅ Company location setup successful!")
        else:
            print("❌ Company location setup failed!")
            
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        
if __name__ == "__main__":
    test_company_create()
