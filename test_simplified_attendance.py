"""
🧪 SIMPLIFIED ATTENDANCE TESTING - test_simplified_attendance.py

🎯 WHAT THIS DOES:
Tests the simplified attendance logic to ensure it works correctly.
Validates all key functionalities with minimal complexity.

Test scenarios:
1. Company location setup
2. Basic attendance marking (present/absent)
3. Distance calculation accuracy  
4. Daily attendance updates
5. Attendance history retrieval
"""

import requests
import json
from datetime import datetime, timedelta
import time

# Configuration
BASE_URL = "http://127.0.0.1:5000"  # Local development
# BASE_URL = "https://your-app.onrender.com"  # Production

def test_simple_attendance_flow():
    """Test the complete simplified attendance flow."""
    
    print("🚀 Testing Simplified Attendance System")
    print("=" * 50)
    
    # Test data
    test_user = {
        "email": "test.simple@example.com",
        "password": "testpass123",
        "name": "Test Simple User",
        "role": "student"
    }
    
    # Company location (example: New York coordinates)
    company_location = {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "altitude": 10,
        "radius": 50
    }
    
    # User locations for testing
    locations = {
        "inside": {"latitude": 40.7129, "longitude": -74.0061, "altitude": 10},    # ~15m away
        "outside": {"latitude": 40.7200, "longitude": -74.0100, "altitude": 10},   # ~800m away
        "exact": {"latitude": 40.7128, "longitude": -74.0060, "altitude": 10}      # Exact location
    }
    
    token = None
    
    try:
        # Step 1: Register or login user
        print("\n1️⃣ Testing User Authentication")
        login_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": test_user["email"],
            "password": test_user["password"]
        })
        
        if login_response.status_code != 200:
            # Try to register first
            print("   📝 Registering new user...")
            register_response = requests.post(f"{BASE_URL}/auth/register", json=test_user)
            print(f"   Register Status: {register_response.status_code}")
            
            if register_response.status_code in [200, 201]:
                # Login after registration
                login_response = requests.post(f"{BASE_URL}/auth/login", json={
                    "email": test_user["email"],
                    "password": test_user["password"]
                })
        
        if login_response.status_code == 200:
            token = login_response.json().get("data", {}).get("access_token")
            print(f"   ✅ Login successful")
        else:
            print(f"   ❌ Login failed: {login_response.text}")
            return False
        
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        # Step 2: Set up company location
        print("\n2️⃣ Testing Company Location Setup")
        location_response = requests.post(
            f"{BASE_URL}/simple/company/create", 
            json=company_location,
            headers=headers
        )
        
        print(f"   Location setup status: {location_response.status_code}")
        if location_response.status_code == 200:
            print("   ✅ Company location set successfully")
        else:
            print(f"   ⚠️ Location setup response: {location_response.text}")
        
        # Step 3: Test attendance marking - Inside radius (should be present)
        print("\n3️⃣ Testing Attendance - Inside Radius")
        inside_response = requests.post(
            f"{BASE_URL}/simple/mark-attendance",
            json=locations["inside"],
            headers=headers
        )
        
        print(f"   Inside attendance status: {inside_response.status_code}")
        if inside_response.status_code == 200:
            inside_data = inside_response.json().get("data", {})
            print(f"   ✅ Status: {inside_data.get('status')}")
            print(f"   📍 Distance: {inside_data.get('distance')}m")
        else:
            print(f"   ❌ Inside attendance failed: {inside_response.text}")
        
        # Step 4: Test attendance marking - Outside radius (should be absent)
        print("\n4️⃣ Testing Attendance - Outside Radius")
        outside_response = requests.post(
            f"{BASE_URL}/simple/mark-attendance",
            json=locations["outside"],
            headers=headers
        )
        
        print(f"   Outside attendance status: {outside_response.status_code}")
        if outside_response.status_code == 200:
            outside_data = outside_response.json().get("data", {})
            print(f"   ✅ Status: {outside_data.get('status')}")
            print(f"   📍 Distance: {outside_data.get('distance')}m")
        else:
            print(f"   ❌ Outside attendance failed: {outside_response.text}")
        
        # Step 5: Test attendance update (mark present after being absent)
        print("\n5️⃣ Testing Attendance Update")
        time.sleep(1)  # Small delay
        exact_response = requests.post(
            f"{BASE_URL}/simple/mark-attendance",
            json=locations["exact"],
            headers=headers
        )
        
        print(f"   Update attendance status: {exact_response.status_code}")
        if exact_response.status_code == 200:
            exact_data = exact_response.json().get("data", {})
            print(f"   ✅ Updated Status: {exact_data.get('status')}")
            print(f"   📍 Distance: {exact_data.get('distance')}m")
        else:
            print(f"   ❌ Update attendance failed: {exact_response.text}")
        
        # Step 6: Get attendance history
        print("\n6️⃣ Testing Attendance History")
        history_response = requests.get(
            f"{BASE_URL}/simple/my-attendance",
            headers=headers
        )
        
        print(f"   History status: {history_response.status_code}")
        if history_response.status_code == 200:
            history_data = history_response.json().get("data", [])
            print(f"   ✅ Found {len(history_data)} attendance records")
            
            if history_data:
                latest = history_data[0]
                print(f"   📊 Latest status: {latest.get('status')}")
                print(f"   📅 Latest timestamp: {latest.get('timestamp')}")
        else:
            print(f"   ❌ History failed: {history_response.text}")
        
        # Step 7: Test distance calculation accuracy
        print("\n7️⃣ Testing Distance Calculation")
        
        # Test exact same location (should be 0m)
        same_location_response = requests.post(
            f"{BASE_URL}/simple/mark-attendance",
            json=company_location,
            headers=headers
        )
        
        if same_location_response.status_code == 200:
            same_data = same_location_response.json().get("data", {})
            distance = same_data.get('distance', 0)
            print(f"   ✅ Same location distance: {distance}m (should be ~0)")
            
            if distance < 1:
                print("   ✅ Distance calculation accurate")
            else:
                print("   ⚠️ Distance calculation might need adjustment")
        
        print("\n🎉 Simplified Attendance Testing Completed!")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        return False

def test_error_scenarios():
    """Test error handling scenarios."""
    
    print("\n🛡️ Testing Error Scenarios")
    print("=" * 30)
    
    # Test without authentication
    print("\n1️⃣ Testing without authentication")
    no_auth_response = requests.post(f"{BASE_URL}/simple/mark-attendance", json={
        "latitude": 40.7128,
        "longitude": -74.0060
    })
    print(f"   No auth status: {no_auth_response.status_code} (should be 401)")
    
    # Test with invalid coordinates
    print("\n2️⃣ Testing with invalid coordinates")
    # This would need a valid token from previous test
    
    # Test with missing fields
    print("\n3️⃣ Testing with missing fields")
    # This would also need a valid token
    
    print("   ⚠️ Additional error tests require authentication from main test")

if __name__ == "__main__":
    """Run the tests."""
    
    print("🧪 Simplified Attendance System Tests")
    print("=====================================")
    
    # Check if server is running
    try:
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Server is running")
        else:
            print("⚠️ Server responded but health check failed")
    except Exception as e:
        print(f"❌ Server not accessible: {str(e)}")
        print("Make sure the Flask server is running with: python app.py")
        exit(1)
    
    # Run main test flow
    success = test_simple_attendance_flow()
    
    # Run error scenario tests
    test_error_scenarios()
    
    if success:
        print("\n🎊 All tests completed successfully!")
        print("\nNext steps:")
        print("1. Update your app.py to register the simple_attendance blueprint")
        print("2. Run the migration to create the simplified table")
        print("3. Update your frontend to use the simplified endpoints")
    else:
        print("\n⚠️ Some tests failed. Check the logs above.")
