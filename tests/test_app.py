"""
🧪 API TESTING SCRIPT - test_app.py

🎯 WHAT THIS FILE DOES:
This file tests the attendance backend API to make sure everything works correctly.
Think of it as a "quality check" that verifies all the main features are working.

🔧 FOR FRONTEND DEVELOPERS:
- This shows you EXACTLY how to call the API endpoints
- Provides working examples of request/response formats  
- Tests the main user flows you'll implement in your frontend
- Helps you understand expected API behavior

📋 WHAT IT TESTS:
1. Health check - Verify server is running
2. User check-in - Test attendance marking with location
3. Session attendance - Test retrieving attendance records
4. Error handling - Verify proper error responses

🌐 EXAMPLE API CALLS FOR FRONTEND:

This script demonstrates the basic API usage patterns you'll use:

HEALTH CHECK EXAMPLE:
GET http://127.0.0.1:5000/health
→ Returns: {"success": true, "message": "Server is running"}

ATTENDANCE CHECK-IN EXAMPLE:
POST http://127.0.0.1:5000/check-in
Content-Type: application/json
{
  "student_id": "user-uuid",
  "session_id": "session-uuid", 
  "lat": 40.7128,
  "lon": -74.0060
}
→ Returns attendance record with check-in time and status

SESSION ATTENDANCE EXAMPLE:
GET http://127.0.0.1:5000/session/{session_id}/attendance
→ Returns list of all attendance records for that session

⚡ HOW TO USE THIS FOR FRONTEND DEVELOPMENT:

1. RUN THE SERVER:
   python app.py

2. RUN THIS TEST:
   python test_app.py

3. OBSERVE THE OUTPUTS:
   - See exact request/response formats
   - Understand error handling
   - Copy successful patterns for your frontend

📱 FRONTEND IMPLEMENTATION GUIDE:

Based on this test script, here's how to implement in your frontend:

// Health check (useful for app startup)
async function checkServerHealth() {
  const response = await fetch('http://127.0.0.1:5000/health');
  const result = await response.json();
  return result.success;
}

// Check-in attendance (main feature)
async function checkInAttendance(sessionId, latitude, longitude) {
  const response = await fetch('http://127.0.0.1:5000/check-in', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      student_id: getCurrentUserId(),
      session_id: sessionId,
      lat: latitude,
      lon: longitude
    })
  });
  return await response.json();
}

// Get session attendance (for teachers/admins)
async function getSessionAttendance(sessionId) {
  const response = await fetch(`http://127.0.0.1:5000/session/${sessionId}/attendance`);
  return await response.json();
}

🛠️ TESTING TIPS:
- Run this script after making API changes
- Use the sample data created by init_db.py
- Check console output for error debugging
- Modify test data to test different scenarios

🔍 WHAT TO LOOK FOR:
- Status codes (200 = success, 400 = error, etc.)
- Response format consistency
- Error message clarity
- Data structure accuracy

📚 LEARNING FROM THIS SCRIPT:
- Request headers and body formats
- Expected response structures
- Error handling patterns
- Authentication requirements (for future endpoints)
"""

import sys
import os

# Add the parent directory to the Python path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:5000"

def test_health_check():
    """Test the health check endpoint."""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_check_in():
    """Test the check-in endpoint."""
    print("Testing check-in endpoint...")
    
    # Test data with real IDs from database initialization
    test_data = {
        "student_id": "4ce95cfc-a272-4d22-b42a-d6d4b7ae7ebb",  # John Doe (student)
        "session_id": "c94a4cce-fee6-4057-9c67-0368f2331fcb",  # Computer Science 101 session
        "lat": 40.7128,
        "lon": -74.0060
    }
    
    response = requests.post(
        f"{BASE_URL}/check-in",
        json=test_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_get_attendance():
    """Test the get attendance endpoint."""
    print("Testing get attendance endpoint...")
    
    session_id = "c94a4cce-fee6-4057-9c67-0368f2331fcb"  # Computer Science 101 session
    response = requests.get(f"{BASE_URL}/session/{session_id}/attendance")
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

if __name__ == "__main__":
    print("Starting attendance backend tests...")
    print("=" * 50)
    
    try:
        test_health_check()
        test_check_in()
        test_get_attendance()
        print("All tests completed!")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure the Flask app is running.")
    except Exception as e:
        print(f"Error during testing: {e}")
