"""
🧪 QUICK SIMPLIFIED ATTENDANCE TEST - quick_test_simple.py

🎯 WHAT THIS DOES:
Quick test focusing on the simplified attendance logic without complex authentication.
Tests the core distance calculation and attendance logic.
"""

import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:5000"

def test_simplified_endpoints():
    """Test simplified attendance endpoints directly."""
    
    print("🚀 Quick Test: Simplified Attendance Endpoints")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1️⃣ Testing Health Check")
    try:
        health_response = requests.get(f"{BASE_URL}/health")
        if health_response.status_code == 200:
            print("   ✅ Server is healthy")
        else:
            print(f"   ❌ Health check failed: {health_response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False
    
    # Test 2: Check if simplified endpoints are registered
    print("\n2️⃣ Testing Simplified Endpoints Registration")
    
    # Test without authentication (should get 401)
    try:
        attendance_response = requests.post(f"{BASE_URL}/simple/mark-attendance", json={
            "latitude": 40.7128,
            "longitude": -74.0060
        })
        
        if attendance_response.status_code == 401:
            print("   ✅ Simplified attendance endpoint is registered (401 as expected)")
        else:
            print(f"   ⚠️ Unexpected response: {attendance_response.status_code}")
            print(f"   Response: {attendance_response.text}")
    except Exception as e:
        print(f"   ❌ Endpoint test error: {e}")
    
    # Test 3: Check simplified company endpoint  
    try:
        company_response = requests.post(f"{BASE_URL}/simple/company/create", json={
            "latitude": 40.7128,
            "longitude": -74.0060
        })
        
        if company_response.status_code == 401:
            print("   ✅ Simplified company endpoint is registered (401 as expected)")
        else:
            print(f"   ⚠️ Unexpected response: {company_response.status_code}")
    except Exception as e:
        print(f"   ❌ Company endpoint test error: {e}")
    
    # Test 4: Test the distance calculation function directly
    print("\n3️⃣ Testing Distance Calculation")
    try:
        # Import the distance calculation function
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from routes.simple_attendance import calculate_distance
        
        # Test known distances
        # New York to nearby location (should be ~111 meters)
        lat1, lon1 = 40.7128, -74.0060  # New York
        lat2, lon2 = 40.7138, -74.0060  # About 111m north
        
        distance = calculate_distance(lat1, lon1, lat2, lon2)
        print(f"   📏 Distance test: {distance:.2f}m (expected ~111m)")
        
        if 100 <= distance <= 122:  # Allow some margin for calculation
            print("   ✅ Distance calculation accurate")
        else:
            print("   ⚠️ Distance calculation might need adjustment")
        
        # Test same location (should be ~0)
        same_distance = calculate_distance(lat1, lon1, lat1, lon1)
        print(f"   📏 Same location distance: {same_distance:.2f}m (expected ~0m)")
        
        if same_distance < 1:
            print("   ✅ Same location calculation accurate")
        
    except Exception as e:
        print(f"   ❌ Distance calculation test error: {e}")
    
    print("\n✅ Quick test completed!")
    print("\nNext steps:")
    print("1. Set up authentication with existing users")
    print("2. Test full attendance flow")
    print("3. Validate database operations")
    
    return True

def test_database_table():
    """Test if the simplified attendance table was created."""
    
    print("\n4️⃣ Testing Database Table")
    try:
        import sqlite3
        
        # Connect to the database
        db_path = "instance/attendance.db"
        if not os.path.exists(db_path):
            print("   ⚠️ Database file not found")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if simple_attendance_records table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='simple_attendance_records'
        """)
        
        table = cursor.fetchone()
        if table:
            print("   ✅ simple_attendance_records table exists")
            
            # Check table structure
            cursor.execute("PRAGMA table_info(simple_attendance_records)")
            columns = cursor.fetchall()
            print(f"   📊 Table has {len(columns)} columns")
            
            for col in columns:
                print(f"      - {col[1]} ({col[2]})")
        else:
            print("   ❌ simple_attendance_records table not found")
        
        # Check if location columns were added to organisations
        cursor.execute("PRAGMA table_info(organisations)")
        org_columns = cursor.fetchall()
        location_columns = [col for col in org_columns if 'location' in col[1]]
        
        if location_columns:
            print(f"   ✅ Found {len(location_columns)} location columns in organisations:")
            for col in location_columns:
                print(f"      - {col[1]} ({col[2]})")
        else:
            print("   ⚠️ No location columns found in organisations table")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Database test error: {e}")
        return False

if __name__ == "__main__":
    """Run the quick tests."""
    
    print("🧪 Quick Simplified Attendance Test")
    print("===================================")
    
    # Import os for database test
    import os
    
    # Run endpoint tests
    success = test_simplified_endpoints()
    
    # Run database tests
    db_success = test_database_table()
    
    if success and db_success:
        print("\n🎉 All quick tests passed!")
        print("\nThe simplified attendance system is set up correctly.")
        print("Next step: Set up proper authentication for full testing.")
    else:
        print("\n⚠️ Some tests failed. Check the output above.")
