#!/usr/bin/env python3
"""
Test the backend fixes
"""
import requests

def test_backend_fixes():
    """Test if all backend issues are fixed"""
    
    BASE_URL = "https://attendance-backend-go8h.onrender.com"
    
    print("� TESTING BACKEND FIXES")
    print("=" * 40)
    
    # Test 1: Public sessions (should work)
    try:
        response = requests.get(f"{BASE_URL}/attendance/public-sessions", timeout=10)
        if response.status_code == 200:
            data = response.json()
            sessions = data.get('data', [])
            print(f"✅ Public sessions: {len(sessions)} sessions found")
            
            if sessions:
                # Test 2: Session details endpoint (NEW FIX)
                session_id = sessions[0]['session_id']
                detail_response = requests.get(f"{BASE_URL}/attendance/sessions/{session_id}", timeout=10)
                
                if detail_response.status_code == 200:
                    print("✅ Session details endpoint: Working")
                else:
                    print(f"❌ Session details endpoint: {detail_response.status_code}")
                    
        else:
            print(f"❌ Public sessions failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    print("\n🎯 Next: Deploy fixes to production")

if __name__ == '__main__':
    test_backend_fixes()
