"""
🔧 DATABASE USER SETUP - setup_production_users.py

🎯 WHAT THIS DOES:
Sets up the production users in the database with the correct credentials.
Creates admin, teacher, and student accounts for testing.
"""

import sqlite3
import uuid
from datetime import datetime
import bcrypt

# Database path
DB_PATH = "instance/attendance.db"

# Production user data
USERS = [
    {
        "email": "psaha21.un@gmail.com",
        "password": "P21042004p#",
        "name": "Admin User",
        "role": "admin"
    },
    {
        "email": "alpha@gmail.com", 
        "password": "P21042004p#",
        "name": "Teacher Alpha",
        "role": "teacher"
    },
    {
        "email": "beta@gmail.com",
        "password": "P21042004p#",
        "name": "Student Beta",
        "role": "student"
    }
]

def hash_password(password):
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def setup_database():
    """Set up the database with production users."""
    
    print("🔧 Setting up production users in database...")
    
    try:
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if organisations table exists and has an organization
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='organisations'")
        if not cursor.fetchone():
            print("❌ Organisations table not found")
            return False
        
        # Check for existing organization
        cursor.execute("SELECT org_id, name FROM organisations LIMIT 1")
        org = cursor.fetchone()
        
        if not org:
            # Create a default organization
            org_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO organisations (org_id, name, description, created_at, is_active)
                VALUES (?, ?, ?, ?, ?)
            """, (org_id, "Test Organization", "Default organization for testing", datetime.now(), True))
            print(f"✅ Created organization: {org_id}")
        else:
            org_id = org[0]
            print(f"✅ Using existing organization: {org[1]} ({org_id})")
        
        # Check existing users
        cursor.execute("SELECT email FROM users")
        existing_emails = {row[0] for row in cursor.fetchall()}
        
        # Create users
        created_count = 0
        for user_data in USERS:
            if user_data["email"] in existing_emails:
                print(f"⚠️ User {user_data['email']} already exists")
                continue
            
            user_id = str(uuid.uuid4())
            password_hash = hash_password(user_data["password"])
            
            cursor.execute("""
                INSERT INTO users (user_id, name, email, password_hash, role, org_id, created_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                user_data["name"],
                user_data["email"],
                password_hash,
                user_data["role"],
                org_id,
                datetime.now(),
                True
            ))
            
            print(f"✅ Created {user_data['role']}: {user_data['email']}")
            created_count += 1
        
        # Add location columns to organisations if missing
        try:
            cursor.execute("ALTER TABLE organisations ADD COLUMN location_lat DECIMAL(10, 8)")
            print("✅ Added location_lat column")
        except sqlite3.OperationalError:
            print("ℹ️ location_lat column already exists")
        
        try:
            cursor.execute("ALTER TABLE organisations ADD COLUMN location_lon DECIMAL(11, 8)")
            print("✅ Added location_lon column")
        except sqlite3.OperationalError:
            print("ℹ️ location_lon column already exists")
        
        try:
            cursor.execute("ALTER TABLE organisations ADD COLUMN location_radius INTEGER DEFAULT 50")
            print("✅ Added location_radius column")
        except sqlite3.OperationalError:
            print("ℹ️ location_radius column already exists")
        
        # Set default location for the organization
        cursor.execute("""
            UPDATE organisations 
            SET location_lat = ?, location_lon = ?, location_radius = ?
            WHERE org_id = ?
        """, (40.7128, -74.0060, 50, org_id))
        print("✅ Set default organization location (New York)")
        
        conn.commit()
        conn.close()
        
        print(f"\n🎉 Database setup complete!")
        print(f"   - Created {created_count} new users")
        print(f"   - Organization: {org_id}")
        print(f"   - Location: 40.7128, -74.0060 (50m radius)")
        
        return True
        
    except Exception as e:
        print(f"❌ Database setup error: {str(e)}")
        return False

def verify_setup():
    """Verify the database setup is correct."""
    
    print("\n🔍 Verifying database setup...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check users
        cursor.execute("SELECT email, role FROM users WHERE is_active = 1")
        users = cursor.fetchall()
        
        print(f"📊 Found {len(users)} active users:")
        for email, role in users:
            print(f"   - {role}: {email}")
        
        # Check organisation
        cursor.execute("SELECT name, location_lat, location_lon, location_radius FROM organisations LIMIT 1")
        org = cursor.fetchone()
        
        if org:
            name, lat, lon, radius = org
            print(f"🏢 Organization: {name}")
            print(f"📍 Location: {lat}, {lon} (radius: {radius}m)")
        
        # Check if simple_attendance_records table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='simple_attendance_records'")
        if cursor.fetchone():
            print("✅ simple_attendance_records table exists")
        else:
            print("⚠️ simple_attendance_records table missing")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Verification error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Production Database Setup")
    print("=" * 40)
    
    if setup_database():
        verify_setup()
        
        print("\n✅ Setup complete! You can now test with:")
        print("   python production_flow_test.py")
    else:
        print("\n❌ Setup failed. Check errors above.")
