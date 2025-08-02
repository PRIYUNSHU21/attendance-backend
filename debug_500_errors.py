#!/usr/bin/env python3
"""
🔧 BACKEND DEVELOPER: 500 ERROR DEBUGGING
Investigate and fix the authentication and attendance marking 500 errors
"""

import requests
import json

def debug_500_errors():
    """Debug the 500 errors in authentication and attendance"""
    base_url = "https://attendance-backend-go8h.onrender.com"
    
    print("🚨 DEBUGGING 500 ERRORS")
    print("=" * 50)
    
    # Test 1: Authentication endpoint detailed analysis
    print("1️⃣ AUTHENTICATION ERROR ANALYSIS")
    print("-" * 40)
    
    try:
        # Test different authentication requests
        test_cases = [
            ("GET /auth/login", "get", {}),
            ("POST /auth/login (empty)", "post", {}),
            ("POST /auth/login (test data)", "post", {
                "email": "test@example.com",
                "password": "testpass"
            }),
            ("POST /auth/register", "post", {
                "name": "Test User",
                "email": "debug@test.com",
                "password": "testpass123",
                "role": "student"
            })
        ]
        
        for test_name, method, data in test_cases:
            try:
                if method == "get":
                    response = requests.get(f"{base_url}/auth/login", timeout=10)
                else:
                    response = requests.post(f"{base_url}/auth/login" if "login" in test_name else f"{base_url}/auth/register", 
                                           json=data, timeout=10)
                
                print(f"   {test_name}: {response.status_code}")
                if response.status_code != 500:
                    print(f"      Response: {response.text[:100]}...")
                else:
                    print(f"      500 Error: {response.text[:200]}...")
                    
            except Exception as e:
                print(f"   {test_name}: Connection error - {e}")
        
    except Exception as e:
        print(f"   Authentication debug failed: {e}")
    
    # Test 2: Attendance endpoint detailed analysis
    print("\n2️⃣ ATTENDANCE ERROR ANALYSIS")
    print("-" * 40)
    
    try:
        attendance_test_cases = [
            ("GET /attendance/check-in", "get", {}),
            ("POST /attendance/check-in (empty)", "post", {}),
            ("POST /attendance/check-in (minimal)", "post", {
                "session_id": "test-session"
            }),
            ("POST /attendance/check-in (with location)", "post", {
                "session_id": "test-session",
                "lat": 40.7128,
                "lon": -74.0060
            })
        ]
        
        for test_name, method, data in attendance_test_cases:
            try:
                if method == "get":
                    response = requests.get(f"{base_url}/attendance/check-in", timeout=10)
                else:
                    response = requests.post(f"{base_url}/attendance/check-in", 
                                           json=data, timeout=10)
                
                print(f"   {test_name}: {response.status_code}")
                if response.status_code != 500:
                    print(f"      Response: {response.text[:100]}...")
                else:
                    print(f"      500 Error: {response.text[:200]}...")
                    
            except Exception as e:
                print(f"   {test_name}: Connection error - {e}")
        
    except Exception as e:
        print(f"   Attendance debug failed: {e}")
    
    # Test 3: Check other endpoints for patterns
    print("\n3️⃣ ENDPOINT PATTERN ANALYSIS")
    print("-" * 40)
    
    test_endpoints = [
        "/health",
        "/attendance/public-sessions", 
        "/attendance/sessions/test-id",
        "/admin/sessions",
        "/reports/attendance"
    ]
    
    working_count = 0
    error_500_count = 0
    
    for endpoint in test_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            print(f"   {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                working_count += 1
            elif response.status_code == 500:
                error_500_count += 1
                print(f"      500 Error: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   {endpoint}: Connection failed")
    
    print(f"\n   Working endpoints: {working_count}")
    print(f"   500 error endpoints: {error_500_count}")
    
    # Test 4: Check if it's a specific route issue
    print("\n4️⃣ ROUTE REGISTRATION ANALYSIS")
    print("-" * 40)
    
    # Based on app.py, these routes should exist
    expected_routes = [
        ("/auth/login", "POST"),
        ("/auth/register", "POST"), 
        ("/attendance/check-in", "POST"),
        ("/attendance/public-sessions", "GET"),
        ("/admin/sessions", "GET"),
        ("/health", "GET")
    ]
    
    print("   Expected routes from app.py:")
    for route, method in expected_routes:
        print(f"      {method} {route}")
    
    # Test 5: Hypothesis about the errors
    print("\n5️⃣ ERROR HYPOTHESIS")
    print("-" * 40)
    print("   Possible causes of 500 errors:")
    print("   1. Database connection issues")
    print("   2. Missing environment variables")
    print("   3. Import errors in route handlers")
    print("   4. Unhandled exceptions in auth/attendance logic")
    print("   5. Missing dependencies or service imports")
    
    # Test 6: Try to identify the specific error
    print("\n6️⃣ SPECIFIC ERROR IDENTIFICATION")
    print("-" * 40)
    
    try:
        # Try a simple POST to see detailed error
        response = requests.post(f"{base_url}/auth/login", 
                               json={"email": "test", "password": "test"}, 
                               timeout=10)
        
        if response.status_code == 500:
            error_text = response.text
            print(f"   Detailed 500 error:")
            print(f"   {error_text}")
            
            # Look for common error patterns
            if "ImportError" in error_text:
                print("   💡 LIKELY CAUSE: Missing import in auth routes")
            elif "Database" in error_text or "SQLAlchemy" in error_text:
                print("   💡 LIKELY CAUSE: Database connection issue")
            elif "AttributeError" in error_text:
                print("   💡 LIKELY CAUSE: Missing method or attribute")
            elif "KeyError" in error_text:
                print("   💡 LIKELY CAUSE: Missing configuration key")
            else:
                print("   💡 CAUSE: Unknown server error")
        
    except Exception as e:
        print(f"   Error identification failed: {e}")

def suggest_fixes():
    """Suggest potential fixes for the 500 errors"""
    print("\n🔧 SUGGESTED FIXES")
    print("=" * 50)
    
    print("1️⃣ CHECK ROUTE IMPORTS:")
    print("   - Verify all blueprint imports in app.py")
    print("   - Check if auth_bp and attendance_bp are properly imported")
    print("   - Look for circular import issues")
    
    print("\n2️⃣ CHECK DATABASE CONNECTION:")
    print("   - Verify DATABASE_URL environment variable")
    print("   - Check if database tables exist")
    print("   - Test SQLAlchemy connection")
    
    print("\n3️⃣ CHECK ROUTE HANDLERS:")
    print("   - Look for syntax errors in routes/auth.py")
    print("   - Check routes/attendance_mark.py for issues")
    print("   - Verify all function definitions")
    
    print("\n4️⃣ CHECK DEPENDENCIES:")
    print("   - Verify all required packages are installed")
    print("   - Check requirements.txt matches deployment")
    print("   - Look for version conflicts")
    
    print("\n5️⃣ IMMEDIATE ACTIONS:")
    print("   - Review server logs in Render dashboard")
    print("   - Check for any recent deployment issues")
    print("   - Verify environment variables are set")

if __name__ == "__main__":
    debug_500_errors()
    suggest_fixes()
