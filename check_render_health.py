#!/usr/bin/env python3
"""
Health check script for Render deployment debugging
"""
import requests
import sys
import time

def check_health(url, max_retries=5, delay=10):
    """Check if the backend is healthy."""
    
    print(f"🔍 Checking health of: {url}")
    
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries}...")
            
            response = requests.get(f"{url}/health", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS: {data}")
                return True
            else:
                print(f"❌ HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {str(e)}")
            
        if attempt < max_retries - 1:
            print(f"Waiting {delay} seconds before retry...")
            time.sleep(delay)
    
    print("❌ All attempts failed")
    return False

def test_endpoints(url):
    """Test key endpoints."""
    
    endpoints = [
        "/health",
        "/auth/public/organizations",
        "/"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"Testing {endpoint}...")
            response = requests.get(f"{url}{endpoint}", timeout=10)
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                print("  ✅ OK")
            else:
                print(f"  ❌ Failed: {response.text[:100]}")
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")

if __name__ == "__main__":
    # Test production URL
    prod_url = "https://attendance-backend-go8h.onrender.com"
    
    print("🚀 RENDER DEPLOYMENT HEALTH CHECK")
    print("=" * 50)
    
    # Check if it's healthy
    is_healthy = check_health(prod_url)
    
    if is_healthy:
        print("\n🧪 Testing endpoints...")
        test_endpoints(prod_url)
    
    sys.exit(0 if is_healthy else 1)
