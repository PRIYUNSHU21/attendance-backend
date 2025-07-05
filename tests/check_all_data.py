"""
🔍 COMPREHENSIVE DATABASE CHECK - check_all_data.py

Check all data in the database to understand current state.
"""

import sys
import os

# Add the parent directory to the Python path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models.organisation import get_all_organisations
from config.db import db
from models.user import User
from models.session import UserSession
from models.attendance import AttendanceSession, AttendanceRecord

def check_all_data():
    print("🗄️ COMPREHENSIVE DATABASE CHECK")
    print("=" * 50)
    
    app = create_app()
    with app.app_context():
        # Check organizations
        orgs = get_all_organisations()
        print(f"\n🏢 Organizations: {len(orgs)}")
        for org in orgs:
            print(f"  - ID: {org.org_id}")
            print(f"    Name: {org.name}")
            print(f"    Email: {org.contact_email}")
        
        # Check users - query directly
        users = User.query.all()
        print(f"\n👥 Users: {len(users)}")
        for user in users:
            print(f"  - ID: {user.user_id}")
            print(f"    Name: {user.name}")
            print(f"    Email: {user.email}")
            print(f"    Role: {user.role}")
            print(f"    Active: {user.is_active}")
            print(f"    Org ID: {user.org_id}")
        
        # Check sessions (attendance sessions)
        sessions = AttendanceSession.query.all()
        print(f"\n📅 Attendance Sessions: {len(sessions)}")
        for session in sessions:
            print(f"  - ID: {session.session_id}")
            print(f"    Name: {session.session_name}")
            print(f"    Created By: {session.created_by}")
            print(f"    Active: {session.is_active}")
            print(f"    Start: {session.start_time}")
            print(f"    End: {session.end_time}")
        
        # Check user sessions (login sessions)  
        user_sessions = UserSession.query.all()
        print(f"\n🔑 User Sessions: {len(user_sessions)}")
        for session in user_sessions:
            print(f"  - ID: {session.session_id}")
            print(f"    User ID: {session.user_id}")
            print(f"    Active: {session.is_active}")
            print(f"    Expires: {session.expires_at}")
        
        # Check attendance records
        records = AttendanceRecord.query.all()
        print(f"\n✅ Attendance Records: {len(records)}")
        for record in records:
            print(f"  - ID: {record.record_id}")
            print(f"    User ID: {record.user_id}")
            print(f"    Session ID: {record.session_id}")
            print(f"    Status: {record.status}")

if __name__ == "__main__":
    check_all_data()
