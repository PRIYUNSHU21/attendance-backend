#!/usr/bin/env python3
"""
Test what location parameters the backend actually expects
"""
import requests
import json

def test_backend_location_params():
    """Test current backend location parameter expectations"""
    
    BASE_URL = "https://attendance-backend-go8h.onrender.com"
    
    print("🔍 TESTING BACKEND LOCATION PARAMETERS")
    print("=" * 50)
    
    # Test 1: Check what the session details endpoint returns for location
    try:
        sessions_response = requests.get(f"{BASE_URL}/attendance/public-sessions", timeout=10)
        if sessions_response.status_code == 200:
            sessions = sessions_response.json()['data']
            if sessions:
                session_id = sessions[0]['session_id']
                
                # Get detailed session info
                detail_response = requests.get(f"{BASE_URL}/attendance/sessions/{session_id}", timeout=10)
                if detail_response.status_code == 200:
                    session_detail = detail_response.json()['data']
                    print("✅ Session detail structure:")
                    print(json.dumps(session_detail, indent=2))
                    
                    # Check what location fields exist
                    location_fields = [key for key in session_detail.keys() if 'location' in key.lower() or 'lat' in key.lower() or 'lon' in key.lower() or 'radius' in key.lower()]
                    if location_fields:
                        print(f"\n📍 Location-related fields found: {location_fields}")
                    else:
                        print("\n❌ No location fields found in session details")
                        
    except Exception as e:
        print(f"❌ Session test failed: {e}")
    
    # Test 2: Check if we can make a test attendance call to see expected parameters
    print(f"\n🧪 Test attendance check-in (without auth - will fail but show expected format):")
    test_payload = {
        "session_id": "test-session",
        "lat": 40.7128,
        "lon": -74.0060
    }
    
    try:
        checkin_response = requests.post(f"{BASE_URL}/attendance/check-in", 
                                       json=test_payload, timeout=10)
        print(f"Response status: {checkin_response.status_code}")
        if checkin_response.status_code in [400, 401]:
            response_data = checkin_response.json()
            print(f"Response: {json.dumps(response_data, indent=2)}")
            
            # If it's just auth error, that means parameters are probably correct
            if "token" in response_data.get('message', '').lower():
                print("✅ Parameters likely correct (auth error only)")
            elif "session" in response_data.get('message', '').lower():
                print("✅ Parameters accepted (session error)")
                
    except Exception as e:
        print(f"❌ Check-in test failed: {e}")

if __name__ == '__main__':
    test_backend_location_params()
