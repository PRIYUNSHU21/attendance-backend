"""
🐛 Debug Session Creation
This script will test session creation step by step
"""
import sys
sys.path.append('.')

from datetime import datetime, timedelta
from models.session import create_session
from config.db import db
from app import app

# Test the create_session function directly
print("🔍 Testing create_session function...")

with app.app_context():
    try:
        print("📝 Creating session with explicit expires_at...")
        
        # Test with explicit parameters
        session = create_session(
            user_id="test-user-id",
            session_token="test-token-123",
            device_info="Test Device",
            ip_address="127.0.0.1",
            duration_hours=24
        )
        
        print(f"✅ Session created successfully!")
        print(f"   Session ID: {session.session_id}")
        print(f"   User ID: {session.user_id}")
        print(f"   Session Token: {session.session_token}")
        print(f"   Expires At: {session.expires_at}")
        print(f"   Is Active: {session.is_active}")
        print(f"   Device Info: {session.device_info}")
        print(f"   IP Address: {session.ip_address}")
        
        # Clean up
        db.session.delete(session)
        db.session.commit()
        print("🧹 Test session cleaned up")
        
    except Exception as e:
        print(f"❌ Error creating session: {e}")
        import traceback
        traceback.print_exc()
