#!/usr/bin/env python3
"""
Test live server session visibility
"""
import requests
import json
from datetime import datetime, timedelta

# Live server URL
BASE_URL = "https://attendance-backend-go8h.onrender.com"

def test_live_server_session_visibility():
    """Test if students can see admin-created sessions on live server"""
    
    print("🌐 TESTING LIVE SERVER SESSION VISIBILITY")
    print("=" * 50)
    
    # Test 1: Check server health
    try:
        health_response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"✅ Server health: {health_response.status_code} - {health_response.text}")
    except Exception as e:
        print(f"❌ Server health check failed: {e}")
        return
    
    # Test 2: Get all active sessions (public endpoint)
    try:
        sessions_response = requests.get(f"{BASE_URL}/attendance/public-sessions", timeout=10)
        print(f"\n📊 Public sessions endpoint: {sessions_response.status_code}")
        
        if sessions_response.status_code == 200:
            sessions_data = sessions_response.json()
            print(f"Response: {json.dumps(sessions_data, indent=2)}")
            
            if 'data' in sessions_data:
                sessions = sessions_data['data']
                print(f"📈 Found {len(sessions)} active sessions")
                
                if sessions:
                    print("\n🎯 Session details:")
                    for i, session in enumerate(sessions[:3], 1):  # Show first 3 sessions
                        print(f"  {i}. {session.get('session_name', 'Unnamed')} - Org: {session.get('org_id', 'Unknown')}")
                        print(f"     Created by: {session.get('created_by', 'Unknown')}")
                        print(f"     Active: {session.get('is_active', 'Unknown')}")
                else:
                    print("✅ No active sessions found - this means admin sessions aren't visible to students!")
            else:
                print(f"❌ Unexpected response format: {sessions_data}")
        else:
            print(f"❌ Failed to get public sessions: {sessions_response.text}")
            
    except Exception as e:
        print(f"❌ Public sessions request failed: {e}")
    
    # Test 3: Try to get organization sessions for a specific org
    try:
        # Try a common org ID (you may need to adjust this)
        test_org_id = 1
        org_sessions_response = requests.get(f"{BASE_URL}/admin/organization/{test_org_id}/sessions", timeout=10)
        print(f"\n🏢 Organization {test_org_id} sessions: {org_sessions_response.status_code}")
        
        if org_sessions_response.status_code == 200:
            org_data = org_sessions_response.json()
            print(f"Response: {json.dumps(org_data, indent=2)}")
        else:
            print(f"Response: {org_sessions_response.text}")
            
    except Exception as e:
        print(f"❌ Organization sessions request failed: {e}")

if __name__ == '__main__':
    test_live_server_session_visibility()
