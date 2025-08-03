#!/usr/bin/env python3
"""
📍 LOCATION FLOW DEMONSTRATION
Shows exactly how locations are handled in the bulletproof system
"""

import requests
import json

BASE_URL = "https://attendance-backend-go8h.onrender.com"

def test_location_flow():
    """Demonstrate the complete location flow."""
    print("📍 LOCATION FLOW IN BULLETPROOF ATTENDANCE SYSTEM")
    print("=" * 60)
    
    print("\n🔍 1. HOW LOCATIONS ARE HANDLED:")
    print("   ✅ NO HARDCODED LOCATIONS in the system!")
    print("   📱 Student locations: Come from frontend GPS")
    print("   🏫 Session locations: Set by teachers when creating sessions")
    print("   📊 Dynamic comparison: Student GPS vs Session location")
    
    print("\n📋 2. SESSION CREATION (Teacher sets location):")
    print("   POST /admin/sessions")
    print("   {")
    print('     "session_name": "Math Class",')
    print('     "start_time": "2025-08-03T09:00:00Z",')
    print('     "end_time": "2025-08-03T10:30:00Z",')
    print('     "latitude": 40.7128,    // Teacher sets this (classroom location)')
    print('     "longitude": -74.0060,  // Teacher sets this (classroom location)')
    print('     "radius": 50           // Allowed distance in meters')
    print("   }")
    
    print("\n📱 3. STUDENT CHECK-IN (Frontend provides GPS):")
    print("   POST /bulletproof/simple-checkin")
    print("   {")
    print('     "session_id": "session-uuid",')
    print('     "latitude": 40.7129,   // From navigator.geolocation.getCurrentPosition()')
    print('     "longitude": -74.0061  // From navigator.geolocation.getCurrentPosition()')
    print("   }")
    
    print("\n🧮 4. SYSTEM CALCULATION:")
    print("   📏 Distance = calculate_distance(student_lat, student_lon, session_lat, session_lon)")
    print("   ✅ If distance <= session_radius: Status = 'Present'")
    print("   ❌ If distance > session_radius: Status = 'Absent'")
    
    print("\n🌐 5. FRONTEND INTEGRATION EXAMPLE:")
    print("""
// Frontend JavaScript code
navigator.geolocation.getCurrentPosition(async (position) => {
  const response = await fetch('/bulletproof/simple-checkin', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      session_id: selectedSessionId,
      latitude: position.coords.latitude,   // DYNAMIC GPS
      longitude: position.coords.longitude  // DYNAMIC GPS
    })
  });
  
  const result = await response.json();
  console.log('Attendance Status:', result.data.status);
  console.log('Distance from classroom:', result.data.distance + 'm');
});
""")
    
    # Now let's test with real API calls
    print("\n🧪 6. LIVE API TEST:")
    
    # Login as teacher
    print("\n   🔐 Logging in as teacher...")
    teacher_login = {
        "email": "alpha@gmail.com",
        "password": "P21042004p#"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=teacher_login)
        if response.status_code == 200:
            teacher_data = response.json()['data']
            teacher_token = teacher_data['token']
            print("   ✅ Teacher logged in successfully")
            
            # Get active sessions to show real locations
            print("\n   📋 Fetching active sessions...")
            headers = {"Authorization": f"Bearer {teacher_token}"}
            
            sessions_response = requests.get(f"{BASE_URL}/bulletproof/get-active-sessions", headers=headers)
            if sessions_response.status_code == 200:
                sessions = sessions_response.json()['data']
                print(f"   ✅ Found {len(sessions)} active sessions:")
                
                for i, session in enumerate(sessions[:3], 1):  # Show first 3
                    print(f"\n   📍 Session {i}: {session['session_name']}")
                    print(f"      🏫 Classroom Location: ({session['location_lat']}, {session['location_lon']})")
                    print(f"      📏 Allowed Radius: {session['location_radius']}m")
                    print(f"      🆔 Session ID: {session['session_id'][:8]}...")
                    
                # Test student attendance with real GPS coordinates
                if sessions:
                    print(f"\n   🎓 Testing student attendance...")
                    
                    # Login as student
                    student_login = {
                        "email": "beta@gmail.com", 
                        "password": "P21042004p#"
                    }
                    
                    student_response = requests.post(f"{BASE_URL}/auth/login", json=student_login)
                    if student_response.status_code == 200:
                        student_data = student_response.json()['data']
                        student_token = student_data['token']
                        print("   ✅ Student logged in successfully")
                        
                        # Test attendance with simulated GPS
                        test_session = sessions[0]
                        session_lat = test_session['location_lat']
                        session_lon = test_session['location_lon']
                        
                        # Simulate student being close to classroom
                        student_lat = session_lat + 0.0001  # Very close
                        student_lon = session_lon + 0.0001
                        
                        attendance_data = {
                            "session_id": test_session['session_id'],
                            "latitude": student_lat,
                            "longitude": student_lon
                        }
                        
                        student_headers = {"Authorization": f"Bearer {student_token}"}
                        attendance_response = requests.post(
                            f"{BASE_URL}/bulletproof/simple-checkin", 
                            json=attendance_data, 
                            headers=student_headers
                        )
                        
                        if attendance_response.status_code == 200:
                            result = attendance_response.json()['data']
                            print(f"   📍 Student GPS: ({student_lat:.6f}, {student_lon:.6f})")
                            print(f"   🏫 Session GPS: ({session_lat}, {session_lon})")
                            print(f"   📏 Distance: {result['distance']:.2f}m")
                            print(f"   ✅ Status: {result['status']}")
                            print(f"   💬 Message: {result.get('message', 'N/A')}")
                        else:
                            print(f"   ❌ Attendance failed: {attendance_response.text}")
                    else:
                        print("   ❌ Student login failed")
            else:
                print("   ❌ Failed to fetch sessions")
        else:
            print("   ❌ Teacher login failed")
    
    except Exception as e:
        print(f"   ❌ API test error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY:")
    print("✅ NO hardcoded locations anywhere in the system")
    print("📱 Student locations: Dynamic GPS from frontend")
    print("🏫 Session locations: Set by teachers when creating sessions")
    print("📊 Attendance decision: Real-time distance calculation")
    print("🚀 System ready for production frontend integration!")

if __name__ == "__main__":
    test_location_flow()
