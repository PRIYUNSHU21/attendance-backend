#!/usr/bin/env python3
"""
Final attendance test with UTC timing
"""
import requests
from datetime import datetime, timezone, timedelta

BASE_URL = "https://attendance-backend-go8h.onrender.com"

def final_attendance_test():
    print("🎯 FINAL ATTENDANCE TEST (UTC)")
    print("=" * 35)
    
    # Login admin
    admin_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "psaha21.un@gmail.com", 
        "password": "P21042004p#"
    })
    
    admin_token = admin_response.json()["data"]["jwt_token"]
    headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
    
    # Create session with UTC timing - session started 10 minutes ago
    now_utc = datetime.now(timezone.utc)
    session_data = {
        "session_name": f"UTC TEST {now_utc.strftime('%H%M%S')}",
        "description": "UTC attendance test",
        "start_time": (now_utc - timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%S"),
        "end_time": (now_utc + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S")
    }
    
    print(f"UTC Now: {now_utc}")
    print(f"Session start (UTC): {session_data['start_time']}")
    print(f"Session end (UTC): {session_data['end_time']}")
    
    session_response = requests.post(f"{BASE_URL}/admin/sessions", json=session_data, headers=headers)
    print(f"Session creation: {session_response.status_code}")
    
    if session_response.status_code == 201:
        session = session_response.json()["data"]
        print(f"✅ Session created: {session['session_name']}")
        
        # Mark attendance
        attendance_data = {
            "session_id": session['session_id'],
            "lat": 40.7128,
            "lon": -74.0060
        }
        
        attendance_response = requests.post(f"{BASE_URL}/attendance/check-in", json=attendance_data, headers=headers)
        
        print(f"Attendance: {attendance_response.status_code}")
        print(f"Response: {attendance_response.text}")
        
        return attendance_response.status_code == 200
    else:
        print(f"Failed to create session: {session_response.text}")
        return False

if __name__ == "__main__":
    success = final_attendance_test()
    print(f"\n🎯 FINAL RESULT: {'✅ ATTENDANCE WORKS!' if success else '❌ STILL FAILING'}")
