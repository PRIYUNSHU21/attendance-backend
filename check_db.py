#!/usr/bin/env python3
"""Check database contents"""

import sqlite3
import os

db_path = os.path.join('instance', 'attendance.db')
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print('Tables:', [t[0] for t in tables])
    
    # Check attendance_sessions
    if 'attendance_sessions' in [t[0] for t in tables]:
        cursor.execute('SELECT COUNT(*) FROM attendance_sessions')
        count = cursor.fetchone()[0]
        print(f'Attendance sessions count: {count}')
        
        if count > 0:
            cursor.execute('SELECT session_name, start_time, end_time, is_active, org_id FROM attendance_sessions ORDER BY created_at DESC LIMIT 3')
            sessions = cursor.fetchall()
            print('Recent sessions:')
            for session in sessions:
                print(f'  {session}')
    else:
        print('No attendance_sessions table found!')
    
    conn.close()
else:
    print('Database file not found!')
