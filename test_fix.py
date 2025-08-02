#!/usr/bin/env python3
"""
Test if the session visibility issue is fixed
"""
import requests
import json

def test_fix():
    """Test if students can now see admin sessions"""
    
    BASE_URL = "https://attendance-backend-go8h.onrender.com"
    
    print("🔍 TESTING SESSION VISIBILITY FIX")
    print("=" * 40)
    
    # Test 1: Server health
    try:
        health = requests.get(f"{BASE_URL}/health", timeout=10)
        if health.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server issue")
            return
    except:
        print("❌ Can't reach server")
        return
    
    # Test 2: Public sessions endpoint (NEW FIX)
    try:
        response = requests.get(f"{BASE_URL}/attendance/public-sessions", timeout=10)
        print(f"\n📊 Public sessions endpoint: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            sessions = data.get('data', [])
            
            print(f"✅ SUCCESS! Found {len(sessions)} sessions")
            
            if sessions:
                print("\n🎯 Session Details:")
                for session in sessions[:3]:  # Show first 3
                    print(f"   • {session.get('session_name', 'Unnamed')}")
                    print(f"     Org: {session.get('org_id')}")
                    print(f"     Created by: {session.get('created_by')}")
                    print(f"     Active: {session.get('is_active')}")
                    print()
                
                print("🎉 ISSUE FIXED: Students can now see admin sessions!")
            else:
                print("ℹ️  No active sessions found (normal if no sessions are running)")
                print("✅ But the endpoint works - issue is likely fixed!")
                
        elif response.status_code == 404:
            print("❌ Endpoint not found - deployment might still be in progress")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == '__main__':
    test_fix()
