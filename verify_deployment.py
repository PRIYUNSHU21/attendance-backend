#!/usr/bin/env python3
"""
🚀 POST-DEPLOYMENT VERIFICATION TEST

Run this after Render deployment completes to verify the new endpoint works
"""

import requests
import time
from datetime import datetime

RENDER_URL = "https://attendance-backend-go8h.onrender.com"
TEACHER_CREDS = {"email": "beta@gmail.com", "password": "Beta123#"}

def print_status(message, status="INFO"):
    """Print colored status messages"""
    colors = {
        "INFO": "\033[94m",     # Blue
        "SUCCESS": "\033[92m",  # Green
        "ERROR": "\033[91m",    # Red
        "WARNING": "\033[93m"   # Yellow
    }
    reset = "\033[0m"
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{colors.get(status, '')}{timestamp} [{status}] {message}{reset}")

def verify_deployment():
    """Verify the deployment is working"""
    print_status("🚀 POST-DEPLOYMENT VERIFICATION", "INFO")
    print_status("=" * 60, "INFO")
    
    # Step 1: Health check
    print_status("1️⃣ Checking server health...")
    try:
        response = requests.get(f"{RENDER_URL}/health", timeout=10)
        if response.status_code == 200:
            print_status("✅ Server is healthy", "SUCCESS")
        else:
            print_status(f"❌ Health check failed: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        print_status(f"❌ Cannot reach server: {str(e)}", "ERROR")
        return False
    
    # Step 2: Teacher login
    print_status("2️⃣ Testing teacher authentication...")
    try:
        response = requests.post(f"{RENDER_URL}/auth/login", json=TEACHER_CREDS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                jwt_token = data["data"]["jwt_token"]
                teacher = data["data"]["user"]
                print_status(f"✅ Teacher login works: {teacher['name']}", "SUCCESS")
            else:
                print_status(f"❌ Login failed: {data.get('message')}", "ERROR")
                return False
        else:
            print_status(f"❌ Login HTTP error: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        print_status(f"❌ Login error: {str(e)}", "ERROR")
        return False
    
    # Step 3: Test NEW students endpoint
    print_status("3️⃣ Testing NEW /admin/students endpoint...")
    try:
        response = requests.get(
            f"{RENDER_URL}/admin/students",
            headers={"Authorization": f"Bearer {jwt_token}"},
            timeout=15
        )
        
        print_status(f"   Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                response_data = data.get("data", {})
                students = response_data.get("students", [])
                pagination = response_data.get("pagination", {})
                
                print_status("🎉 NEW STUDENTS ENDPOINT IS WORKING! 🎉", "SUCCESS")
                print_status(f"   Students found: {len(students)}")
                print_status(f"   Total in organization: {pagination.get('total', 'Unknown')}")
                print_status(f"   Pagination: Page {pagination.get('page', 1)} of {pagination.get('total_pages', 1)}")
                
                if students:
                    print_status("   📋 Sample students:")
                    for i, student in enumerate(students[:3]):  # Show first 3
                        print_status(f"     • {student.get('name', 'No name')} ({student.get('email', 'No email')})")
                
                return True
            else:
                print_status(f"❌ Endpoint failed: {data.get('message')}", "ERROR")
                return False
        elif response.status_code == 404:
            print_status("❌ Endpoint still not found - deployment may not be complete", "ERROR")
            print_status("   💡 Wait a few more minutes and try again", "WARNING")
            return False
        else:
            print_status(f"❌ HTTP error: {response.status_code}", "ERROR")
            try:
                error_data = response.json()
                print_status(f"   Error: {error_data.get('message', 'Unknown error')}", "ERROR")
            except:
                print_status(f"   Raw response: {response.text[:200]}", "ERROR")
            return False
            
    except Exception as e:
        print_status(f"❌ Error testing endpoint: {str(e)}", "ERROR")
        return False

def main():
    """Main verification function"""
    print_status("⏳ Waiting 30 seconds for deployment to complete...", "WARNING")
    time.sleep(30)
    
    success = verify_deployment()
    
    print_status("-" * 60, "INFO")
    if success:
        print_status("🎊 DEPLOYMENT VERIFICATION SUCCESSFUL! 🎊", "SUCCESS")
        print_status("✅ Frontend team can now use the /admin/students endpoint", "SUCCESS")
        print_status("📚 Documentation: See FRONTEND_STATUS_UPDATE.md", "INFO")
    else:
        print_status("❌ VERIFICATION FAILED", "ERROR")
        print_status("💡 Try running this script again in a few minutes", "WARNING")
        print_status("🔧 Or check Render deployment logs for issues", "WARNING")

if __name__ == "__main__":
    main()
