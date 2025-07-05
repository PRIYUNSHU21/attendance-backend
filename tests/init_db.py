"""
🚀 DATABASE INITIALIZATION SCRIPT - init_db.py

🎯 WHAT THIS FILE DOES:
This file sets up the database and creates sample data for testing and development.
Think of it as the "database setup wizard" that prepares everything for first use.

🔧 FOR FRONTEND DEVELOPERS:
- Run this ONCE when setting up the project locally
- Creates sample organizations, users, and attendance sessions
- Provides test data so you can immediately start frontend development
- Shows what real data looks like in the system

📋 WHAT IT CREATES:

🏢 SAMPLE ORGANIZATIONS:
- "Tech University" - A sample educational institution
- "Business School" - Another sample organization for testing multi-tenancy

👥 SAMPLE USERS:
- Admin users for system management
- Teacher users for session management  
- Student users for attendance testing
- Different roles across organizations

📅 SAMPLE ATTENDANCE SESSIONS:
- "Computer Science 101" - Active session for testing check-ins
- "Business Management" - Another session for testing
- Sessions with realistic timing and locations

🌐 SAMPLE DATA FOR FRONTEND TESTING:

ORGANIZATIONS:
{
  "org_id": "uuid",
  "name": "Tech University", 
  "description": "Leading technology education",
  "address": "123 University Ave"
}

USERS:
{
  "user_id": "uuid",
  "name": "John Doe",
  "email": "john.doe@techuniversity.edu",
  "role": "student",
  "org_id": "tech-university-uuid"
}

ATTENDANCE SESSIONS:
{
  "session_id": "uuid",
  "session_name": "Computer Science 101",
  "start_time": "2025-07-05T09:00:00Z",
  "end_time": "2025-07-05T11:00:00Z",
  "location_lat": 40.7128,
  "location_lon": -74.0060,
  "location_radius": 100
}

⚡ HOW TO USE THIS:

1. FIRST TIME SETUP:
   python tests/init_db.py

2. RESET DATABASE (if needed):
   Delete attendance.db file, then run: python tests/init_db.py

3. VERIFY SETUP:
   python tests/test_app.py

📱 FRONTEND DEVELOPMENT BENEFITS:

With this sample data, you can immediately:
- Test login with predefined users
- See real attendance sessions in your UI
- Test check-in functionality with sample sessions
- Build organization selection features
- Test different user roles and permissions

🔍 SAMPLE LOGIN CREDENTIALS:

ADMIN USER:
Email: admin@techuniversity.edu
Password: admin123

TEACHER USER:  
Email: teacher@techuniversity.edu
Password: teacher123

STUDENT USER:
Email: student@techuniversity.edu
Password: student123

📚 DEVELOPMENT WORKFLOW:

1. Run init_db.py to set up database
2. Start the Flask server (python app.py)
3. Use sample credentials to test login
4. Test attendance features with sample sessions
5. Build frontend features against this stable data set

🛠️ CUSTOMIZATION:
- Modify this file to add your own test data
- Add more organizations for multi-tenant testing
- Create additional user roles or scenarios
- Add more attendance sessions for testing

⚠️ IMPORTANT NOTES:
- Only run this in development/testing environments
- Creates a fresh database each time (overwrites existing data)
- Sample passwords are for testing only (change in production)
- UUIDs are generated randomly each time you run this
"""

import sys
import os

# Add the parent directory to the Python path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models.user import create_user
from models.organisation import create_organisation
from models.attendance import create_attendance_session
from services.hash_service import hash_password
from datetime import datetime, timedelta

def init_database():
    """Initialize the database with test data."""
    app = create_app()
    
    with app.app_context():
        try:
            # Create test organization
            org_data = {
                "name": "Test University",
                "description": "A test university for demonstration",
                "address": "123 Test Street, Test City",
                "contact_email": "admin@testuni.edu",
                "contact_phone": "+1234567890"
            }
            org = create_organisation(org_data)
            print(f"Created organization: {org.name}")
            
            # Create test users
            users_data = [
                {
                    "name": "John Doe",
                    "email": "john.doe@testuni.edu",
                    "password": "password123",
                    "role": "student",
                    "org_id": org.org_id
                },
                {
                    "name": "Jane Smith",
                    "email": "jane.smith@testuni.edu",
                    "password": "password123",
                    "role": "teacher",
                    "org_id": org.org_id
                },
                {
                    "name": "Admin User",
                    "email": "admin@testuni.edu",
                    "password": "admin123",
                    "role": "admin",
                    "org_id": org.org_id
                }
            ]
            
            created_users = []
            for user_data in users_data:
                user_data["password_hash"] = hash_password(user_data["password"])
                del user_data["password"]
                user = create_user(user_data)
                created_users.append(user)
                print(f"Created user: {user.name} ({user.role})")
            
            # Create test attendance session
            session_data = {
                "org_id": org.org_id,
                "session_name": "Computer Science 101 - Lecture 1",
                "description": "Introduction to Computer Science",
                "start_time": datetime.now() - timedelta(hours=1),
                "end_time": datetime.now() + timedelta(hours=1),
                "location_lat": 40.7128,
                "location_lon": -74.0060,
                "location_radius": 100.0,
                "created_by": created_users[1].user_id  # Created by teacher
            }
            session = create_attendance_session(session_data)
            print(f"Created session: {session.session_name}")
            
            print("\n" + "="*50)
            print("Database initialized successfully!")
            print("="*50)
            print(f"Organization ID: {org.org_id}")
            print(f"Session ID: {session.session_id}")
            print(f"Student ID: {created_users[0].user_id}")
            print(f"Teacher ID: {created_users[1].user_id}")
            print(f"Admin ID: {created_users[2].user_id}")
            
        except Exception as e:
            print(f"Error initializing database: {e}")

if __name__ == "__main__":
    init_database()
