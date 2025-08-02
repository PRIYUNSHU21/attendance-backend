#!/usr/bin/env python3
"""
🔍 DEBUG ACTIVE SESSIONS - debug_active_sessions.py

This script directly tests the get_active_sessions function to identify the issue.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from models.attendance import AttendanceSession, get_active_sessions
from datetime import datetime

def debug_active_sessions():
    """Debug the active sessions function directly."""
    
    with app.app_context():
        print("🔍 DEBUGGING ACTIVE SESSIONS FUNCTION")
        print("=" * 50)
        
        # Get all sessions in database
        all_sessions = AttendanceSession.query.all()
        print(f"📊 Total sessions in database: {len(all_sessions)}")
        
        if len(all_sessions) > 0:
            for session in all_sessions:
                print(f"\n📅 Session: {session.session_name}")
                print(f"   ID: {session.session_id}")
                print(f"   Org: {session.org_id}")
                print(f"   Start: {session.start_time}")
                print(f"   End: {session.end_time}")
                print(f"   Active: {session.is_active}")
                
                # Check current time
                current_time = datetime.now()
                print(f"   Current Time: {current_time}")
                
                # Check time conditions
                if session.start_time:
                    start_ok = session.start_time <= current_time
                    print(f"   Start <= Current: {start_ok}")
                
                if session.end_time:
                    end_ok = session.end_time >= current_time
                    print(f"   End >= Current: {end_ok}")
                
                # Test get_active_sessions for this org
                active_sessions = get_active_sessions(session.org_id)
                print(f"   Active sessions found: {len(active_sessions)}")
        else:
            print("❌ No sessions found in database!")

if __name__ == "__main__":
    debug_active_sessions()
