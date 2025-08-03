#!/usr/bin/env python3
"""
Check if attendance records exist in production database
"""
import requests

BASE_URL = "https://attendance-backend-go8h.onrender.com"

def check_existing_attendance():
    print("📊 CHECKING EXISTING ATTENDANCE RECORDS")
    print("=" * 40)
    
    # Login as admin
    admin_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "psaha21.un@gmail.com", 
        "password": "P21042004p#"
    })
    
    admin_token = admin_response.json()["data"]["jwt_token"]
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Try to get attendance reports or records
    # Check if there are any endpoints to view attendance
    
    # Get sessions first
    sessions_response = requests.get(f"{BASE_URL}/attendance/public-sessions", headers=headers)
    sessions = sessions_response.json()["data"]
    
    if sessions:
        session = sessions[0]
        session_id = session['session_id']
        
        # Try to get session report (this might work even if we can't create records)
        report_response = requests.get(f"{BASE_URL}/admin/sessions/{session_id}/report", headers=headers)
        print(f"Session report: {report_response.status_code}")
        print(f"Response: {report_response.text}")
        
        # Try alternative attendance endpoints
        attendance_response = requests.get(f"{BASE_URL}/attendance/sessions/{session_id}", headers=headers)
        print(f"Session attendance: {attendance_response.status_code}")
        print(f"Response: {attendance_response.text}")

if __name__ == "__main__":
    check_existing_attendance()
