"""
🔐 AUTHENTICATION SERVICE - services/auth_services.py

🎯 WHAT THIS FILE DOES:
This file handles all user authentication (login/logout/registration).
Think of it as the "security guard" that checks if users are who they claim to be.

🔧 FOR FRONTEND DEVELOPERS:
- This powers your login, registration, and logout features
- Provides JWT tokens for authenticated API calls
- Handles password security and validation
- Manages user sessions and device tracking

📋 MAIN FUNCTIONS FOR FRONTEND:
1. login_user(): Handles user login process
2. register_user(): Creates new user accounts  
3. logout_user(): Ends user sessions safely
4. verify_session(): Checks if user is still logged in
5. change_password(): Updates user passwords securely

🌐 API INTEGRATION EXAMPLES:

LOGIN PROCESS:
Frontend sends: { "email": "user@example.com", "password": "password123" }
Service returns: { 
  "user": {...user data...}, 
  "token": "jwt-token-here",
  "session": {...session info...}
}

REGISTRATION PROCESS:
Frontend sends: { "name": "John", "email": "john@example.com", "password": "pass123" }
Service returns: { "user": {...new user data...} }

LOGOUT PROCESS:
Frontend sends: { "session_token": "session-token-here" }
Service returns: { "success": true }

🔒 SECURITY FEATURES:
- Passwords are hashed with bcrypt (never stored as plain text)
- JWT tokens for stateless authentication
- Session tracking with device information
- Automatic session expiration
- Password strength validation

⚡ FRONTEND USAGE FLOW:
1. User submits login form → call login_user()
2. Store returned JWT token in localStorage/sessionStorage
3. Include token in Authorization header for API calls
4. On logout → call logout_user() and clear stored token
5. Check token validity with verify_session() on app startup

🛡️ TOKEN MANAGEMENT:
- JWT tokens expire after configured time (default 24 hours)
- Include token in requests: "Authorization: Bearer <token>"
- Refresh tokens before expiration
- Handle 401 responses by redirecting to login

📱 EXAMPLE FRONTEND CODE:
// Login
const response = await fetch('/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
});

// Authenticated requests
const response = await fetch('/attendance/check-in', {
  method: 'POST',
  headers: { 
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json' 
  },
  body: JSON.stringify(data)
});
"""

from models.user import find_user_by_email, create_user
from models.session import create_session, validate_session, invalidate_session
from services.hash_service import hash_password, verify_password
from utils.auth import generate_token
import secrets
import uuid

def login_user(email, password, device_info=None, ip_address=None):
    """
    Authenticate a user and create a session.
    
    Args:
        email: User's email address
        password: User's password
        device_info: Optional device information
        ip_address: Optional IP address
        
    Returns:
        Dictionary containing user info and session token
        
    Raises:
        Exception: If authentication fails
    """
    user = find_user_by_email(email)
    if not user:
        raise Exception("User not found")

    if not verify_password(password, user.password_hash):
        raise Exception("Incorrect password")

    # Generate session token
    session_token = secrets.token_urlsafe(32)
    
    # Create session
    session = create_session(
        user_id=user.user_id,
        session_token=session_token,
        device_info=device_info,
        ip_address=ip_address
    )
    
    # Generate JWT token with session token for enhanced security validation
    jwt_token = generate_token({
        "user_id": user.user_id,
        "org_id": user.org_id,
        "role": user.role,
        "session_id": session.session_id,
        "session_token": session_token  # 🔒 SECURITY: Include session token for validation
    })
    
    return {
        "user": user.to_dict(),
        "session_token": session_token,
        "jwt_token": jwt_token,
        "session_id": session.session_id
    }

def register_user(data):
    """
    Register a new user.
    
    Args:
        data: Dictionary containing user information
        
    Returns:
        Created user object
        
    Raises:
        Exception: If registration fails
    """
    # Check if user already exists
    existing_user = find_user_by_email(data["email"])
    if existing_user:
        raise Exception("User with this email already exists")
    
    # Hash the password
    data["password_hash"] = hash_password(data["password"])
    del data["password"]  # Remove plain password from data
    
    # Create user
    return create_user(data)

def logout_user(session_token):
    """
    Logout a user by invalidating their session.
    
    Args:
        session_token: The session token to invalidate
        
    Returns:
        True if logout successful, False otherwise
    """
    return invalidate_session(session_token)

def verify_session(session_token):
    """
    Verify if a session token is valid.
    
    Args:
        session_token: The session token to verify
        
    Returns:
        User object if valid, None otherwise
    """
    return validate_session(session_token)

def change_password(user_id, old_password, new_password):
    """
    Change a user's password.
    
    Args:
        user_id: The user's ID
        old_password: Current password
        new_password: New password
        
    Returns:
        True if password changed successfully
        
    Raises:
        Exception: If password change fails
    """
    from models.user import find_user_by_id, update_user
    
    user = find_user_by_id(user_id)
    if not user:
        raise Exception("User not found")
    
    if not verify_password(old_password, user.password_hash):
        raise Exception("Current password is incorrect")
    
    # Hash new password
    new_password_hash = hash_password(new_password)
    
    # Update user
    update_user(user_id, {"password_hash": new_password_hash})
    
    return True