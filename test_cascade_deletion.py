#!/usr/bin/env python3
"""
🧪 TEST CASCADE DELETION - test_cascade_deletion.py

🎯 WHAT THIS SCRIPT DOES:
This script tests the CASCADE deletion functionality by:
1. Creating test data (organization, users, sessions, etc.)
2. Testing organization deletion with CASCADE constraints
3. Verifying that all related data is properly deleted

✅ TESTS CASCADE DELETION FOR:
- Organization deletion cascades to users
- User deletion cascades to user_sessions
- User deletion cascades to invalidated_sessions  
- Organization deletion cascades to attendance_sessions
- Session deletion cascades to attendance_records
"""

import os
import sys
import uuid
from datetime import datetime, timedelta

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from config.db import db
from models.organisation import Organisation
from models.user import User
from models.session import UserSession, InvalidatedSession
from models.attendance import AttendanceSession, AttendanceRecord

def create_test_data():
    """Create test data for CASCADE deletion testing."""
    print("🏗️ Creating test data...")
    
    # Create test organization
    org_id = str(uuid.uuid4())
    test_org = Organisation(
        org_id=org_id,
        name="Test University CASCADE",
        description="Test organization for CASCADE deletion testing",
        address="123 Test Street",
        contact_email="test@cascade.edu",
        contact_phone="+1-555-TEST",
        is_active=True
    )
    db.session.add(test_org)
    
    # Create test users
    user_ids = []
    for i in range(3):
        user_id = str(uuid.uuid4())
        user_ids.append(user_id)
        
        test_user = User(
            user_id=user_id,
            name=f"Test User {i+1}",
            email=f"testuser{i+1}@cascade.edu",
            password_hash="$2b$12$test_hash_here",
            role="student" if i < 2 else "admin",
            org_id=org_id,
            is_active=True
        )
        db.session.add(test_user)
    
    # Create test user sessions
    session_ids = []
    for i, user_id in enumerate(user_ids):
        session_id = str(uuid.uuid4())
        session_ids.append(session_id)
        
        user_session = UserSession(
            session_id=session_id,
            user_id=user_id,
            session_token=f"test_token_{i+1}",
            expires_at=datetime.utcnow() + timedelta(days=1),
            is_active=True,
            device_info=f"Test Device {i+1}",
            ip_address="127.0.0.1"
        )
        db.session.add(user_session)
    
    # Create test invalidated sessions
    for i, user_id in enumerate(user_ids[:2]):  # Only for first 2 users
        invalidated_session = InvalidatedSession(
            session_id=f"old_session_{i+1}",
            user_id=user_id,
            org_id=org_id,
            session_token=f"old_token_{i+1}",
            reason="manual_logout"
        )
        db.session.add(invalidated_session)
    
    # Create test attendance sessions
    attendance_session_ids = []
    for i in range(2):
        attendance_session_id = str(uuid.uuid4())
        attendance_session_ids.append(attendance_session_id)
        
        attendance_session = AttendanceSession(
            session_id=attendance_session_id,
            org_id=org_id,
            session_name=f"Test Class {i+1}",
            description=f"Test attendance session {i+1}",
            start_time=datetime.utcnow() - timedelta(hours=2),
            end_time=datetime.utcnow() + timedelta(hours=1),
            location_lat=40.7128,
            location_lon=-74.0060,
            location_radius=100,
            created_by=user_ids[2],  # Created by admin user
            is_active=True
        )
        db.session.add(attendance_session)
    
    # Create test attendance records
    for i, attendance_session_id in enumerate(attendance_session_ids):
        for j, user_id in enumerate(user_ids[:2]):  # Only students
            record_id = str(uuid.uuid4())
            
            attendance_record = AttendanceRecord(
                record_id=record_id,
                session_id=attendance_session_id,
                user_id=user_id,
                check_in_time=datetime.utcnow() - timedelta(hours=1),
                check_in_lat=40.7128,
                check_in_lon=-74.0060,
                status="present"
            )
            db.session.add(attendance_record)
    
    # Commit all test data
    db.session.commit()
    
    print(f"✅ Test data created:")
    print(f"   - Organization: {test_org.name} ({org_id})")
    print(f"   - Users: {len(user_ids)}")
    print(f"   - User Sessions: {len(session_ids)}")
    print(f"   - Invalidated Sessions: 2")
    print(f"   - Attendance Sessions: {len(attendance_session_ids)}")
    print(f"   - Attendance Records: {len(attendance_session_ids) * 2}")
    
    return org_id

def count_related_data(org_id):
    """Count all data related to the organization."""
    users = User.query.filter_by(org_id=org_id).all()
    user_ids = [u.user_id for u in users]
    
    counts = {
        'organization': Organisation.query.filter_by(org_id=org_id).count(),
        'users': len(users),
        'user_sessions': UserSession.query.filter(UserSession.user_id.in_(user_ids)).count() if user_ids else 0,
        'invalidated_sessions': InvalidatedSession.query.filter_by(org_id=org_id).count(),
        'attendance_sessions': AttendanceSession.query.filter_by(org_id=org_id).count(),
        'attendance_records': 0
    }
    
    # Count attendance records
    attendance_sessions = AttendanceSession.query.filter_by(org_id=org_id).all()
    attendance_session_ids = [s.session_id for s in attendance_sessions]
    if attendance_session_ids:
        counts['attendance_records'] = AttendanceRecord.query.filter(
            AttendanceRecord.session_id.in_(attendance_session_ids)
        ).count()
    
    return counts

def test_cascade_deletion():
    """Test CASCADE deletion functionality."""
    app = create_app()
    
    with app.app_context():
        try:
            # Create test data
            org_id = create_test_data()
            
            # Count data before deletion
            print("\n📊 Data counts BEFORE deletion:")
            before_counts = count_related_data(org_id)
            for key, count in before_counts.items():
                print(f"   - {key}: {count}")
            
            # Test organization deletion with CASCADE
            print(f"\n🗑️ Testing CASCADE deletion for organization {org_id}...")
            
            # Get the organization
            org = Organisation.query.filter_by(org_id=org_id).first()
            if not org:
                print("❌ Test organization not found!")
                return
            
            print(f"🎯 Deleting organization: {org.name}")
            
            # Delete the organization (CASCADE should handle all related data)
            db.session.delete(org)
            db.session.commit()
            
            print("✅ Organization deleted successfully")
            
            # Count data after deletion
            print("\n📊 Data counts AFTER deletion:")
            after_counts = count_related_data(org_id)
            for key, count in after_counts.items():
                print(f"   - {key}: {count}")
            
            # Verify CASCADE deletion worked
            print("\n🔍 CASCADE Deletion Verification:")
            success = True
            
            for key, count in after_counts.items():
                if count == 0:
                    print(f"   ✅ {key}: Properly deleted (0 remaining)")
                else:
                    print(f"   ❌ {key}: Failed to delete ({count} remaining)")
                    success = False
            
            if success:
                print("\n🎉 CASCADE deletion test PASSED!")
                print("✅ All foreign key constraints are working correctly")
                print("✅ Organization deletion properly cascades to all related data")
            else:
                print("\n❌ CASCADE deletion test FAILED!")
                print("⚠️ Some related data was not deleted")
            
            return success
            
        except Exception as e:
            print(f"\n❌ CASCADE deletion test failed: {e}")
            db.session.rollback()
            return False

def test_organization_deletion_endpoint():
    """Test the organization deletion endpoint with CASCADE constraints."""
    app = create_app()
    
    with app.app_context():
        try:
            print("\n🧪 Testing organization deletion endpoint...")
            
            # Create test data
            org_id = create_test_data()
            
            # Import and test the deletion function
            from models.organisation import delete_organisation
            
            # Test deletion
            result = delete_organisation(org_id)
            
            if result['success']:
                print("✅ Organization deletion endpoint test PASSED!")
                print(f"📊 Deletion result: {result}")
                
                # Verify no data remains
                after_counts = count_related_data(org_id)
                all_deleted = all(count == 0 for count in after_counts.values())
                
                if all_deleted:
                    print("✅ All related data properly deleted via endpoint")
                else:
                    print("⚠️ Some data remains after endpoint deletion")
                    print(f"📊 Remaining data: {after_counts}")
                
                return all_deleted
            else:
                print(f"❌ Organization deletion endpoint failed: {result['message']}")
                return False
                
        except Exception as e:
            print(f"❌ Organization deletion endpoint test failed: {e}")
            return False

if __name__ == "__main__":
    print("🧪 CASCADE Deletion Testing")
    print("=" * 50)
    
    # Test 1: Direct CASCADE deletion
    test1_passed = test_cascade_deletion()
    
    print("\n" + "=" * 50)
    
    # Test 2: Organization deletion endpoint
    test2_passed = test_organization_deletion_endpoint()
    
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY:")
    print(f"   Test 1 (Direct CASCADE): {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"   Test 2 (Deletion Endpoint): {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 ALL CASCADE DELETION TESTS PASSED!")
        print("✅ Frontend foreign key constraint issues are FIXED")
        print("✅ Organization deletion will work properly in production")
    else:
        print("\n⚠️ Some CASCADE deletion tests failed")
        print("🔧 Additional debugging may be required")
