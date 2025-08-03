#!/usr/bin/env python3
"""
Check production database tables and create attendance_records if missing
"""
import requests

BASE_URL = "https://attendance-backend-go8h.onrender.com"

def fix_attendance_database():
    print("🔧 FIXING ATTENDANCE DATABASE")
    print("=" * 35)
    
    # Login as admin
    admin_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "psaha21.un@gmail.com", 
        "password": "P21042004p#"
    })
    
    admin_token = admin_response.json()["data"]["jwt_token"]
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Step 1: Check what tables exist
    print("1. Checking existing tables...")
    tables_response = requests.get(f"{BASE_URL}/migration/check-tables", headers=headers)
    
    if tables_response.status_code == 200:
        tables = tables_response.json()["data"]["tables"]
        print(f"   Found {len(tables)} tables:")
        for table in sorted(tables):
            print(f"   - {table}")
        
        if "attendance_records" in tables:
            print("   ✅ attendance_records table exists!")
        else:
            print("   ❌ attendance_records table MISSING!")
            
            # Step 2: Create attendance_records table
            print("\n2. Creating attendance_records table...")
            create_response = requests.post(f"{BASE_URL}/migration/create-attendance-records-table", headers=headers)
            
            if create_response.status_code == 200:
                print("   ✅ attendance_records table created successfully!")
                
                # Step 3: Test attendance now
                print("\n3. Testing attendance after table creation...")
                
                # Get latest session
                sessions_response = requests.get(f"{BASE_URL}/attendance/public-sessions", headers=headers)
                sessions = sessions_response.json()["data"]
                
                if sessions:
                    session = sessions[-1]
                    
                    # Try attendance
                    attendance_data = {
                        "session_id": session['session_id'],
                        "lat": 40.7128,
                        "lon": -74.0060
                    }
                    
                    attendance_response = requests.post(f"{BASE_URL}/attendance/check-in", 
                                                      json=attendance_data, headers=headers)
                    
                    if attendance_response.status_code == 200:
                        print("   🎉 ATTENDANCE WORKING! Database fixed!")
                        return True
                    else:
                        print(f"   ❌ Still failing: {attendance_response.text}")
                        
            else:
                print(f"   ❌ Failed to create table: {create_response.text}")
    else:
        print(f"Failed to check tables: {tables_response.text}")
    
    return False

if __name__ == "__main__":
    success = fix_attendance_database()
    print(f"\n🎯 DATABASE FIX: {'SUCCESS' if success else 'FAILED'}")
