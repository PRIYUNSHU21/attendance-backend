#!/usr/bin/env python3
"""
🔍 QUICK SERVER CHECK

Test if the backend server is running and responding.
"""

import requests

BASE_URL = "https://attendance-backend-3l6a.onrender.com"

def check_server():
    """Check if server is responding."""
    print("🔄 Checking if server is running...")
    
    try:
        # Try a simple endpoint
        response = requests.get(f"{BASE_URL}/public/organizations", timeout=10)
        print(f"✅ Server is responding! Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Public organizations endpoint works")
            return True
        else:
            print(f"⚠️ Server responded but with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server - deployment may still be in progress")
        return False
    except requests.exceptions.Timeout:
        print("❌ Server timeout - may be starting up")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    check_server()
