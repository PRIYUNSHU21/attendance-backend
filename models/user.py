# models/user.py
"""
User model module for handling user-related operations.
This module provides functions to manage users in an in-memory database.
It includes functionality to create users and search for them by email.
The module uses uuid to generate unique identifiers for users:
- uuid (Universally Unique Identifier) creates random, unique IDs 
- uuid4() specifically generates random UUIDs to ensure each user 
    has a unique identifier without needing a centralized ID system
- These UUIDs are converted to strings for storage as user_id
The module maintains a simple in-memory database (USERS_DB) to store
user records with fields for identification, authentication, and 
organizational information.
"""

import uuid

USERS_DB = []

def find_user_by_email(email):
    """Find a user by their email."""
    for user in USERS_DB:
        if user['email'] == email:
            return user
    return None

def create_user(data):
    """Create a new user."""
    user = {
        "user_id": str(uuid.uuid4()),
        "name": data["name"],
        "email": data["email"],
        "password_hash": data["password_hash"],
        "role": data["role"],
        "org_id": data["org_id"]
    }
    USERS_DB.append(user)
    return user