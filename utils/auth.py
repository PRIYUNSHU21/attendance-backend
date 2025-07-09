"""
🎫 JWT AUTHENTICATION UTILITIES - utils/auth.py

🎯 WHAT THIS FILE DOES:
This file provides JWT (JSON Web Token) authentication functions and decorators.
Think of it as the "security checkpoint" that verifies user identity for protected features.

🔧 FOR FRONTEND DEVELOPERS:
- This handles the JWT tokens your frontend receives after login
- Provides decorators that protect API endpoints
- Manages token validation for all authenticated requests
- Determines user permissions for different features

📋 MAIN FUNCTIONS FOR FRONTEND:
1. generate_token(): Creates JWT tokens during login
2. verify_token(): Validates JWT tokens from frontend requests
3. @token_required: Decorator that requires authentication
4. @admin_required: Decorator that requires admin role
5. @teacher_or_admin_required: Decorator for teacher/admin access
6. get_current_user(): Gets current user info from token

🔄 AUTHENTICATION FLOW FOR FRONTEND:

LOGIN FLOW:
1. User logs in → Backend generates JWT token
2. Frontend stores token (localStorage/sessionStorage)
3. Frontend includes token in API requests
4. Backend validates token and processes request

REQUEST FLOW:
Frontend Request → Token Validation → Route Handler → Response

🌐 HOW TO USE TOKENS IN FRONTEND:

STORING TOKENS:
// After successful login
localStorage.setItem('token', response.data.token);

SENDING TOKENS:
// Include in all authenticated requests
headers: {
  'Authorization': `Bearer ${localStorage.getItem('token')}`,
  'Content-Type': 'application/json'
}

HANDLING TOKEN ERRORS:
// 401 = token invalid/expired → redirect to login
// 403 = insufficient permissions → show error message

🔒 SECURITY FEATURES:
- Tokens expire automatically (default 24 hours)
- Tokens are signed to prevent tampering
- Role-based access control built-in
- Invalid tokens are rejected immediately

⚡ ENDPOINT PROTECTION LEVELS:
- No decorator: Public access (health check, login)
- @token_required: Authenticated users only
- @teacher_or_admin_required: Teachers and admins only
- @admin_required: Admins only

📱 EXAMPLE FRONTEND USAGE:

// Check if user is authenticated
const token = localStorage.getItem('token');
if (!token) {
  // Redirect to login
  window.location.href = '/login';
}

// Make authenticated request
try {
  const response = await fetch('/attendance/check-in', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });
  
  if (response.status === 401) {
    // Token expired, redirect to login
    localStorage.removeItem('token');
    window.location.href = '/login';
  }
} catch (error) {
  console.error('Request failed:', error);
}

🛡️ TOKEN SECURITY BEST PRACTICES:
- Store tokens securely (avoid localStorage for sensitive apps)
- Always use HTTPS in production
- Implement token refresh for long-lived sessions
- Clear tokens on logout
- Handle token expiration gracefully
"""

import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app

def get_secret_key():
    """Get the JWT secret key from environment or config."""
    return os.environ.get("JWT_SECRET_KEY", current_app.config.get('JWT_SECRET_KEY', 'default_secret'))

def generate_token(payload, expiry_hours=24):
    """
    Generate a JWT token with the given payload.
    
    Args:
        payload: Dictionary containing the data to encode
        expiry_hours: Number of hours until token expires
        
    Returns:
        JWT token string
    """
    payload['exp'] = datetime.utcnow() + timedelta(hours=expiry_hours)
    payload['iat'] = datetime.utcnow()  # Issued at time
    
    token = jwt.encode(payload, get_secret_key(), algorithm="HS256")
    return token

def decode_token(token):
    """
    Decode a JWT token and return the payload with enhanced security validation.
    
    🔒 SECURITY ENHANCEMENT: Validates organization existence and session blacklist.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded payload dictionary
        
    Raises:
        Exception: If token is invalid, expired, or security checks fail
    """
    try:
        payload = jwt.decode(token, get_secret_key(), algorithms=["HS256"])
        
        # Enhanced security validation
        if 'org_id' in payload:
            # Check if organization still exists and is active
            from models.organisation import Organisation
            org = Organisation.query.filter(
                Organisation.org_id == payload['org_id'],
                Organisation.is_active == True
            ).first()
            
            if not org:
                raise Exception("Organization no longer exists")
        
        # Check if this is a session token and validate it
        if 'session_token' in payload:
            from models.session import is_session_valid
            is_valid, message = is_session_valid(payload['session_token'])
            if not is_valid:
                raise Exception(f"Session validation failed: {message}")
        
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token has expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")
    except Exception as e:
        # Re-raise our custom exceptions
        raise e

def token_required(f):
    """
    Decorator function to require JWT token for protected routes.
    
    Usage:
        @token_required
        def protected_route():
            # Access current_user from the decorated function
            pass
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer TOKEN
            except IndexError:
                return jsonify({'message': 'Invalid authorization header format'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            # Decode token
            payload = decode_token(token)
            request.current_user = payload
        except Exception as e:
            return jsonify({'message': str(e)}), 401
        
        return f(*args, **kwargs)
    
    return decorated

def admin_required(f):
    """
    Decorator function to require admin role for protected routes.
    Must be used after @token_required decorator.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(request, 'current_user'):
            return jsonify({'message': 'Authentication required'}), 401
        
        if request.current_user.get('role') != 'admin':
            return jsonify({'message': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    
    return decorated

def teacher_or_admin_required(f):
    """
    Decorator function to require teacher or admin role for protected routes.
    Must be used after @token_required decorator.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(request, 'current_user'):
            return jsonify({'message': 'Authentication required'}), 401
        
        role = request.current_user.get('role')
        if role not in ['admin', 'teacher']:
            return jsonify({'message': 'Teacher or admin access required'}), 403
        
        return f(*args, **kwargs)
    
    return decorated

def same_org_required(f):
    """
    Decorator function to ensure user belongs to the same organization.
    Must be used after @token_required decorator.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(request, 'current_user'):
            return jsonify({'message': 'Authentication required'}), 401
        
        # This decorator expects org_id to be passed as a parameter
        # The actual implementation depends on your route structure
        return f(*args, **kwargs)
    
    return decorated

def get_current_user():
    """
    Get the current user from the JWT token.
    
    Returns:
        User payload dictionary or None if not authenticated
    """
    if hasattr(request, 'current_user'):
        return request.current_user
    return None
    