#!/usr/bin/env python3
"""
Check user organizations to understand the attendance failure
"""
import requests

BASE_URL = "https://attendance-backend-go8h.onrender.com"

def check_user_orgs():
    print("🏢 CHECKING USER ORGANIZATIONS")
    print("=" * 30)
    
    # Login as admin
    admin_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "psaha21.un@gmail.com", 
        "password": "P21042004p#"
    })
    
    admin_data = admin_response.json()["data"]
    admin_token = admin_data["jwt_token"]
    print(f"Admin user: {admin_data.get('user', {}).get('email', 'Unknown')}")
    print(f"Admin org_id: {admin_data.get('user', {}).get('org_id', 'Unknown')}")
    
    # Login as student  
    student_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "beta@gmail.com", 
        "password": "P21042004p#"
    })
    
    student_data = student_response.json()["data"]
    student_token = student_data["jwt_token"]
    print(f"Student user: {student_data.get('user', {}).get('email', 'Unknown')}")
    print(f"Student org_id: {student_data.get('user', {}).get('org_id', 'Unknown')}")
    
    # Check if they're in the same org
    admin_org = admin_data.get('user', {}).get('org_id')
    student_org = student_data.get('user', {}).get('org_id')
    
    if admin_org == student_org:
        print("✅ Users are in the same organization")
        
        # Try attendance with student token on admin's session
        headers = {"Authorization": f"Bearer {student_token}"}
        
        # Get latest session
        sessions_response = requests.get(f"{BASE_URL}/attendance/public-sessions", headers=headers)
        sessions = sessions_response.json()["data"]
        
        if sessions:
            session = sessions[-1]  # Get the most recent session
            print(f"Testing student attendance on: {session['session_name']}")
            
            attendance_data = {
                "session_id": session['session_id'],
                "lat": 40.7128,
                "lon": -74.0060
            }
            
            attendance_response = requests.post(f"{BASE_URL}/attendance/check-in", 
                                              json=attendance_data, headers=headers)
            
            print(f"Student attendance: {attendance_response.status_code}")
            print(f"Response: {attendance_response.text}")
        
    else:
        print("❌ Users are in different organizations")
        print(f"Admin org: {admin_org}")
        print(f"Student org: {student_org}")

if __name__ == "__main__":
    check_user_orgs()
