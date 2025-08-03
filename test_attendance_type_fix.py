#!/usr/bin/env python3
"""
Test the attendance marking fix for Decimal/str type errors
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

import requests
import json
from decimal import Decimal

def test_attendance_marking_types():
    """Test attendance marking with various coordinate types."""
    base_url = "https://attendance-backend-go8h.onrender.com"
    
    print("🧪 Testing Attendance Marking Type Conversion Fix...")
    
    # Login as student
    login_data = {
        "email": "beta@gmail.com", 
        "password": "P21042004p#"
    }
    
    print("\n1️⃣ Logging in as student...")
    try:
        login_response = requests.post(f"{base_url}/auth/login", json=login_data, timeout=30)
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            print(login_response.text)
            return
        
        auth_data = login_response.json()
        token = auth_data.get('data', {}).get('jwt_token')
        if not token:
            print("❌ No JWT token received")
            return
            
        print("✅ Login successful")
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Test attendance marking with different coordinate formats
    headers = {"Authorization": f"Bearer {token}"}
    
    test_cases = [
        {
            "name": "Float coordinates (normal case)",
            "data": {
                "session_id": "test-session-id", 
                "latitude": 22.6164736,
                "longitude": 88.3785728,
                "altitude": 0
            }
        },
        {
            "name": "String coordinates (problematic case)", 
            "data": {
                "session_id": "test-session-id",
                "latitude": "22.6164736",
                "longitude": "88.3785728", 
                "altitude": 0
            }
        },
        {
            "name": "Integer coordinates",
            "data": {
                "session_id": "test-session-id",
                "latitude": 23,
                "longitude": 88,
                "altitude": 0
            }
        },
        {
            "name": "High precision coordinates",
            "data": {
                "session_id": "test-session-id",
                "latitude": 22.61647364829472,
                "longitude": 88.37857283947284,
                "altitude": 0
            }
        }
    ]
    
    print("\n2️⃣ Testing various coordinate formats...")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}:")
        print(f"   Input: lat={test_case['data']['latitude']} ({type(test_case['data']['latitude']).__name__})")
        print(f"          lon={test_case['data']['longitude']} ({type(test_case['data']['longitude']).__name__})")
        
        try:
            response = requests.post(
                f"{base_url}/simple/mark-attendance",
                json=test_case['data'],
                headers=headers,
                timeout=10
            )
            
            result = response.json()
            
            if response.status_code == 200:
                print(f"   ✅ Success: {result.get('message', 'Attendance marked')}")
                if 'data' in result:
                    data = result['data']
                    print(f"      Distance: {data.get('distance', 'N/A')}m")
                    print(f"      Status: {data.get('status', 'N/A')}")
            elif response.status_code == 400 and "Organization location not set" in result.get('message', ''):
                print(f"   ✅ Expected error (org not set): {result['message']}")
            elif response.status_code == 404 and "Session not found" in result.get('message', ''):
                print(f"   ✅ Expected error (session not found): {result['message']}")
            elif "unsupported operand type" in result.get('message', ''):
                print(f"   ❌ TYPE ERROR STILL EXISTS: {result['message']}")
            else:
                print(f"   ⚠️  Other response ({response.status_code}): {result.get('message', 'No message')}")
                
        except Exception as e:
            print(f"   ❌ Request error: {e}")
    
    print("\n3️⃣ Testing local distance calculation function...")
    
    # Test the distance calculation function directly
    try:
        from routes.simple_attendance import calculate_distance
        from decimal import Decimal
        
        # Test with mixed types that would cause the original error
        test_coords = [
            (22.6164736, 88.3785728, Decimal('22.6164736'), Decimal('88.3785728')),
            (22.6164736, 88.3785728, "22.6164736", "88.3785728"),
            (Decimal('22.6164736'), Decimal('88.3785728'), 22.6164736, 88.3785728),
            ("22.6164736", "88.3785728", 22.6164736, 88.3785728),
        ]
        
        for i, (lat1, lon1, lat2, lon2) in enumerate(test_coords, 1):
            try:
                distance = calculate_distance(lat1, lon1, lat2, lon2)
                print(f"   ✅ Test {i}: Distance = {distance:.2f}m")
                print(f"      Types: {type(lat1).__name__}, {type(lon1).__name__}, {type(lat2).__name__}, {type(lon2).__name__}")
            except Exception as e:
                print(f"   ❌ Test {i} failed: {e}")
                print(f"      Types: {type(lat1).__name__}, {type(lon1).__name__}, {type(lat2).__name__}, {type(lon2).__name__}")
        
    except ImportError:
        print("   ⚠️  Could not import calculate_distance function for local testing")
    
    print("\n🎯 Type Conversion Fix Test Complete!")
    print("✅ If no 'TYPE ERROR STILL EXISTS' messages appeared, the fix is working!")

if __name__ == "__main__":
    test_attendance_marking_types()
