#!/usr/bin/env python3
"""Quick DB check"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.db import db
from models.attendance import AttendanceSession
from app import app

with app.app_context():
    count = AttendanceSession.query.count()
    print(f"📊 AttendanceSession records: {count}")
    
    if count > 0:
        sessions = AttendanceSession.query.all()
        for session in sessions:
            print(f"  - {session.session_name} (ID: {session.session_id})")
            print(f"    Org: {session.org_id}")
            print(f"    Active: {session.is_active}")
    else:
        print("  No sessions found in database!")
