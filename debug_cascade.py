#!/usr/bin/env python3
"""
🔍 DEBUG CASCADE DELETION - debug_cascade.py

This script tests CASCADE deletion step by step to identify the issue.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.db import db
from models.organisation import Organisation
from models.user import User
from models.session import UserSession, InvalidatedSession
from models.attendance import AttendanceSession, AttendanceRecord
from app import app
import uuid
from datetime import datetime

def check_foreign_key_support():
    """Check if foreign key constraints are enabled in SQLite."""
    with app.app_context():
        with db.engine.connect() as conn:
            result = conn.execute(db.text("PRAGMA foreign_keys;")).fetchone()
            print(f"🔗 Foreign keys enabled: {result[0] if result else 'Unknown'}")
            
            # Check table schemas
            tables = ['organisations', 'users', 'user_sessions', 'invalidated_sessions', 'attendance_sessions', 'attendance_records']
            for table in tables:
                try:
                    result = conn.execute(db.text(f"PRAGMA table_info({table});")).fetchall()
                    print(f"\n📋 {table} schema:")
                    for row in result:
                        print(f"  - {row[1]} {row[2]} {'NOT NULL' if row[3] else 'NULL'} {'PRIMARY KEY' if row[5] else ''}")
                    
                    # Check foreign keys
                    fk_result = conn.execute(db.text(f"PRAGMA foreign_key_list({table});")).fetchall()
                    if fk_result:
                        print(f"🔗 Foreign keys in {table}:")
                        for fk in fk_result:
                            print(f"  - {fk[3]} -> {fk[2]}.{fk[4]} (ON DELETE: {fk[6]})")
                    else:
                        print(f"🔗 No foreign keys in {table}")
                except Exception as e:
                    print(f"❌ Error checking {table}: {e}")

def test_cascade_step_by_step():
    """Test CASCADE deletion step by step."""
    with app.app_context():
        print("🧹 Cleaning existing data...")
        # Clean up in reverse dependency order
        AttendanceRecord.query.delete()
        AttendanceSession.query.delete()
        InvalidatedSession.query.delete()
        UserSession.query.delete()
        User.query.delete()
        Organisation.query.delete()
        db.session.commit()
        
        # Enable foreign keys for the session
        with db.engine.connect() as conn:
            conn.execute(db.text("PRAGMA foreign_keys = ON;"))
            conn.commit()
            # Verify it's enabled
            result = conn.execute(db.text("PRAGMA foreign_keys;")).fetchone()
            print(f"� Foreign keys enabled after setting: {result[0] if result else 'Unknown'}")
        
        print("�📊 Creating test data...")
        
        # Create organization
        org = Organisation(
            org_id=str(uuid.uuid4()),
            name="Test Cascade Org",
            description="Testing CASCADE deletion",
            address="123 Test St",
            contact_email="test@example.com",
            contact_phone="555-0123",
            is_active=True
        )
        db.session.add(org)
        db.session.flush()  # Get the org_id
        print(f"✅ Created organization: {org.org_id}")
        
        # Create user (using correct field name 'name' not 'username')
        user = User(
            user_id=str(uuid.uuid4()),
            name="Test User",
            email="test@example.com",
            password_hash="dummy_hash",
            role="student",
            org_id=org.org_id,
            is_active=True
        )
        db.session.add(user)
        db.session.flush()
        print(f"✅ Created user: {user.user_id}")
        
        # Create user session
        session = UserSession(
            session_id=str(uuid.uuid4()),
            user_id=user.user_id,
            session_token="dummy_token",
            expires_at=datetime.utcnow(),
            is_active=True
        )
        db.session.add(session)
        db.session.flush()
        print(f"✅ Created user session: {session.session_id}")
        
        # Create attendance session
        att_session = AttendanceSession(
            session_id=str(uuid.uuid4()),
            session_name="Test Session",
            org_id=org.org_id,
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow(),
            created_by=user.user_id,
            is_active=True
        )
        db.session.add(att_session)
        db.session.flush()
        print(f"✅ Created attendance session: {att_session.session_id}")
        
        # Create attendance record
        att_record = AttendanceRecord(
            record_id=str(uuid.uuid4()),
            session_id=att_session.session_id,
            user_id=user.user_id,
            check_in_time=datetime.utcnow(),
            status="present"
        )
        db.session.add(att_record)
        db.session.commit()
        print(f"✅ Created attendance record: {att_record.record_id}")
        
        # Check counts before deletion
        print("\n📊 Counts before deletion:")
        print(f"  - Organizations: {Organisation.query.count()}")
        print(f"  - Users: {User.query.count()}")
        print(f"  - User Sessions: {UserSession.query.count()}")
        print(f"  - Attendance Sessions: {AttendanceSession.query.count()}")
        print(f"  - Attendance Records: {AttendanceRecord.query.count()}")
        
        # Test CASCADE deletion
        print(f"\n🗑️ Deleting organization: {org.org_id}")
        try:
            db.session.delete(org)
            db.session.commit()
            print("✅ Organization deleted successfully")
        except Exception as e:
            print(f"❌ Error deleting organization: {e}")
            db.session.rollback()
            return
        
        # Check counts after deletion
        print("\n📊 Counts after deletion:")
        print(f"  - Organizations: {Organisation.query.count()}")
        print(f"  - Users: {User.query.count()}")
        print(f"  - User Sessions: {UserSession.query.count()}")
        print(f"  - Attendance Sessions: {AttendanceSession.query.count()}")
        print(f"  - Attendance Records: {AttendanceRecord.query.count()}")
        
        # Check if CASCADE worked
        remaining_users = User.query.filter_by(org_id=org.org_id).count()
        remaining_sessions = UserSession.query.filter_by(org_id=org.org_id).count()
        remaining_att_sessions = AttendanceSession.query.filter_by(org_id=org.org_id).count()
        remaining_att_records = AttendanceRecord.query.filter_by(org_id=org.org_id).count()
        
        if remaining_users == 0 and remaining_sessions == 0 and remaining_att_sessions == 0 and remaining_att_records == 0:
            print("🎉 CASCADE deletion worked perfectly!")
        else:
            print(f"❌ CASCADE deletion failed:")
            print(f"  - Remaining users: {remaining_users}")
            print(f"  - Remaining user sessions: {remaining_sessions}")
            print(f"  - Remaining attendance sessions: {remaining_att_sessions}")
            print(f"  - Remaining attendance records: {remaining_att_records}")

if __name__ == "__main__":
    print("🔍 DEBUGGING CASCADE DELETION")
    print("=" * 50)
    
    check_foreign_key_support()
    print("\n" + "=" * 50)
    test_cascade_step_by_step()
