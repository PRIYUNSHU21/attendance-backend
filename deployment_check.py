#!/usr/bin/env python3
"""
🔍 COMPREHENSIVE DEPLOYMENT ISSUES CHECK

This script identifies potential deployment problems before they happen.
"""

import sys
import os

def check_deployment_issues():
    """Check for common deployment issues."""
    
    print("🔍 CHECKING FOR POTENTIAL DEPLOYMENT ISSUES...")
    print("="*60)
    
    issues = []
    warnings = []
    
    # 1. Check Python version compatibility
    print("1️⃣ Checking Python version...")
    if sys.version_info >= (3, 13):
        warnings.append("⚠️ Python 3.13+ might have dependency compatibility issues")
    elif sys.version_info < (3, 8):
        issues.append("❌ Python version too old (< 3.8)")
    else:
        print("✅ Python version is compatible")
    
    # 2. Check critical files exist
    print("\n2️⃣ Checking critical files...")
    critical_files = [
        'app.py', 'wsgi.py', 'requirements.txt', 'Procfile', 'runtime.txt',
        'config/settings.py', 'config/db.py'
    ]
    
    for file in critical_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            issues.append(f"❌ Missing critical file: {file}")
    
    # 3. Check model imports issues
    print("\n3️⃣ Checking model imports...")
    try:
        # Try to import all models
        from models.user import User, create_user, find_user_by_id, update_user, delete_user, get_users_by_org, get_users_by_role
        print("✅ User model imports work")
    except ImportError as e:
        issues.append(f"❌ User model import error: {str(e)}")
    
    try:
        from models.organisation import Organisation, create_organisation, find_organisation_by_id, get_all_organisations
        print("✅ Organisation model imports work")
    except ImportError as e:
        issues.append(f"❌ Organisation model import error: {str(e)}")
    
    try:
        from models.attendance import AttendanceSession, AttendanceRecord, mark_attendance, mark_checkout, get_active_sessions
        print("✅ Attendance model imports work")
    except ImportError as e:
        issues.append(f"❌ Attendance model import error: {str(e)}")
    
    try:
        from models.session import UserSession, invalidate_organization_sessions
        print("✅ Session model imports work")
    except ImportError as e:
        issues.append(f"❌ Session model import error: {str(e)}")
    
    # 4. Check service imports
    print("\n4️⃣ Checking service imports...")
    try:
        from services.auth_services import login_user, register_user
        print("✅ Auth services imports work")
    except ImportError as e:
        issues.append(f"❌ Auth services import error: {str(e)}")
    
    try:
        from services.attendance_service import get_organization_active_sessions
        print("✅ Attendance services imports work")
    except ImportError as e:
        issues.append(f"❌ Attendance services import error: {str(e)}")
    
    # 5. Check app creation
    print("\n5️⃣ Checking app creation...")
    try:
        from app import create_app
        app = create_app('development')
        print("✅ App creation works")
    except Exception as e:
        issues.append(f"❌ App creation failed: {str(e)}")
    
    # 6. Check database configuration
    print("\n6️⃣ Checking database configuration...")
    try:
        from config.db import init_db
        print("✅ Database configuration works")
    except ImportError as e:
        issues.append(f"❌ Database configuration error: {str(e)}")
    
    # Results
    print("\n" + "="*60)
    print("📋 DEPLOYMENT READINESS REPORT")
    print("="*60)
    
    if not issues and not warnings:
        print("🎉 NO ISSUES FOUND! Ready for deployment!")
        return True
    
    if issues:
        print(f"❌ CRITICAL ISSUES FOUND ({len(issues)}):")
        for issue in issues:
            print(f"   {issue}")
    
    if warnings:
        print(f"⚠️ WARNINGS ({len(warnings)}):")
        for warning in warnings:
            print(f"   {warning}")
    
    if issues:
        print("\n💥 DEPLOYMENT WILL FAIL - Fix issues above first!")
        return False
    else:
        print("\n⚠️ DEPLOYMENT MIGHT HAVE ISSUES - Check warnings above")
        return True

if __name__ == "__main__":
    success = check_deployment_issues()
    sys.exit(0 if success else 1)
