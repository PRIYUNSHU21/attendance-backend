#!/usr/bin/env python3
"""
Check session times to find valid sessions
"""
import requests
from datetime import datetime

BASE_URL = "https://attendance-backend-go8h.onrender.com"

def check_session_times():
    """Check all session times"""
    print("🕐 CHECKING SESSION TIMES")
    print("=" * 40)
    
    # Get sessions
    response = requests.get(f"{BASE_URL}/attendance/public-sessions")
    if response.status_code != 200:
        print(f"❌ Failed to get sessions: {response.text}")
        return
    
    sessions = response.json()["data"]
    current_time = datetime.now()
    print(f"Current time: {current_time}")
    
    valid_sessions = []
    
    for session in sessions:
        start_time = datetime.fromisoformat(session['start_time'].replace('Z', '+00:00')).replace(tzinfo=None)
        end_time = datetime.fromisoformat(session['end_time'].replace('Z', '+00:00')).replace(tzinfo=None)
        
        is_active = start_time <= current_time <= end_time
        time_status = "ACTIVE" if is_active else "EXPIRED" if current_time > end_time else "FUTURE"
        
        print(f"\n📅 {session['session_name']}")
        print(f"   Org: {session['org_id']}")
        print(f"   Start: {start_time}")
        print(f"   End: {end_time}")
        print(f"   Status: {time_status}")
        
        if is_active:
            valid_sessions.append(session)
    
    print(f"\n✅ Found {len(valid_sessions)} active sessions")
    
    if not valid_sessions:
        print("❌ No active sessions found - this is why attendance is failing!")
        print("💡 SOLUTION: Need to create a new session or extend existing ones")
    
    return valid_sessions

if __name__ == "__main__":
    valid_sessions = check_session_times()
