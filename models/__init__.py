"""
📊 DATA MODELS PACKAGE - models/__init__.py

🎯 WHAT THIS FILE DOES:
This file organizes all the data models (database tables) in the correct order.
Think of it as the "table of contents" for all the data structures in the system.

🔧 FOR FRONTEND DEVELOPERS:
- These models define what data you can send/receive via API
- Each model represents a database table with specific fields
- Understanding these helps you know what data is available
- API responses follow these model structures

📋 DATA MODELS AVAILABLE:
1. User: People who use the system (students, teachers, admins)
2. Organisation: Schools, companies, or groups using the system
3. UserSession: Login sessions and authentication tracking
4. AttendanceSession: Classes, meetings, or events that track attendance
5. AttendanceRecord: Individual check-in/check-out records

🌐 FOR API INTEGRATION:
- GET requests return data in these model formats
- POST/PUT requests should send data matching these structures
- Each model has a to_dict() method for JSON responses
- Field validation happens at the model level

🔄 RELATIONSHIPS BETWEEN MODELS:
- User belongs to Organisation
- AttendanceSession belongs to Organisation
- AttendanceRecord belongs to User and AttendanceSession
- UserSession belongs to User

⚡ EXAMPLE API DATA STRUCTURE:
{
  "user": {
    "user_id": "uuid",
    "name": "John Doe", 
    "email": "john@example.com",
    "role": "student",
    "org_id": "org-uuid"
  }
}

📚 WHAT EACH MODEL CONTAINS:
- User: Personal info, role, organization
- Organisation: Company/school details
- AttendanceSession: Class/meeting info, location, timing
- AttendanceRecord: Check-in/out times, location, status
- UserSession: Login tokens, device info, expiration
"""

from config.db import db

# Import all models in the correct order
from .user import User
from .organisation import Organisation
from .session import UserSession
from .attendance import AttendanceSession, AttendanceRecord

# Export all models
__all__ = ['db', 'User', 'Organisation', 'UserSession', 'AttendanceSession', 'AttendanceRecord']
