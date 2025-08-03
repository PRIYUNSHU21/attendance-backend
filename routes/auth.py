"""
🔑 AUTHENTICATION ROUTES - routes/auth.py

🎯 WHAT THIS FILE DOES:
This file defines all authentication-related API endpoints (routes).
Think of it as the "login/logout API" that your frontend will call for user authentication.

🔧 FOR FRONTEND DEVELOPERS:
- These are the API endpoints you'll call for authentication features
- All endpoints return standardized JSON responses
- Handles login, registration, logout, and profile management
- Provides JWT tokens for subsequent authenticated requests

📋 AVAILABLE ENDPOINTS:

🔓 PUBLIC ENDPOINTS (No authentication required):
POST /auth/login - User login
POST /auth/register - User registration
GET /auth/public/organizations - List organizations
POST /auth/public/organizations - Create organization
POST /auth/public/admin - Register first admin

🔒 PROTECTED ENDPOINTS (Require JWT token):
POST /auth/logout - User logout
GET /auth/verify - Verify token validity
GET /auth/profile - Get current user profile
POST /auth/change-password - Change user password

🌐 FRONTEND INTEGRATION EXAMPLES:

USER LOGIN:
POST /auth/login
Content-Type: application/json
{
  "email": "user@example.com",
  "password": "password123",
  "device_info": "Mozilla/5.0..." (optional)
}

Response:
{
  "success": true,
  "data": {
    "user": {...user data...},
    "token": "jwt-token-here",
    "session": {...session info...}
  },
  "message": "Login successful"
}

USER REGISTRATION:
POST /auth/register
Content-Type: application/json
{
  "name": "John Doe",
  "email": "john@example.com", 
  "password": "securepassword123",
  "role": "student",
  "org_id": "organization-uuid"
}

USER LOGOUT:
POST /auth/logout
Authorization: Bearer <jwt-token>
Content-Type: application/json
{
  "session_token": "session-token-here"
}

GET USER PROFILE:
GET /auth/profile
Authorization: Bearer <jwt-token>

CHANGE PASSWORD:
POST /auth/change-password
Authorization: Bearer <jwt-token>
Content-Type: application/json
{
  "old_password": "currentpassword",
  "new_password": "newpassword123"
}

⚡ FRONTEND AUTHENTICATION FLOW:

1. LOGIN:
   - User submits login form
   - Call POST /auth/login
   - Store returned token in localStorage/sessionStorage
   - Redirect to dashboard

2. AUTHENTICATED REQUESTS:
   - Include token in Authorization header
   - Handle 401 responses (token expired)

3. LOGOUT:
   - Call POST /auth/logout
   - Clear stored token
   - Redirect to login page

📱 EXAMPLE FRONTEND IMPLEMENTATION:

// Login function
async function login(email, password) {
  try {
    const response = await fetch('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    
    const result = await response.json();
    
    if (result.success) {
      // Store token and redirect
      localStorage.setItem('token', result.data.token);
      localStorage.setItem('user', JSON.stringify(result.data.user));
      window.location.href = '/dashboard';
    } else {
      // Show error message
      showError(result.message);
    }
  } catch (error) {
    showError('Login failed. Please try again.');
  }
}

// Logout function
async function logout() {
  const token = localStorage.getItem('token');
  
  await fetch('/auth/logout', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  window.location.href = '/login';
}

🔒 SECURITY CONSIDERATIONS:
- Passwords are never returned in responses
- JWT tokens have expiration times
- Failed login attempts are logged
- Sessions are tracked for security monitoring
"""

from flask import Blueprint, request, jsonify
from services.auth_services import login_user, register_user, logout_user, verify_session
from utils.auth import token_required, get_current_user
from utils.response import success_response, error_response, validation_error_response
from utils.validators import validate_user_data

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint."""
    try:
        data = request.get_json()
        if not data:
            return error_response("No data provided", 400)
        
        email = data.get('email')
        password = data.get('password')
        device_info = data.get('device_info')
        ip_address = request.remote_addr

        if not email or not password:
            return error_response("Email and password are required", 400)

        result = login_user(email, password, device_info, ip_address)
        return success_response(
            data=result,
            message="Login successful"
        )
    except Exception as e:
        return error_response(str(e), 401)

@auth_bp.route('/register', methods=['POST'])
def register():
    """User registration endpoint."""
    try:
        data = request.get_json()
        if not data:
            return error_response("No data provided", 400)

        # Validate input data
        validation = validate_user_data(data)
        if not validation['is_valid']:
            return validation_error_response(validation['errors'])

        user = register_user(data)
        return success_response(
            data=user.to_dict(),
            message="User registered successfully",
            status_code=201
        )
    except Exception as e:
        return error_response(str(e), 400)

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """User logout endpoint."""
    try:
        data = request.get_json()
        session_token = data.get('session_token') if data else None
        
        if not session_token:
            return error_response("Session token is required", 400)

        success = logout_user(session_token)
        if success:
            return success_response(message="Logout successful")
        else:
            return error_response("Failed to logout", 400)
    except Exception as e:
        return error_response(str(e), 500)

@auth_bp.route('/verify', methods=['GET'])
@token_required
def verify_token():
    """Verify if the current token is valid."""
    try:
        current_user = get_current_user()
        return success_response(
            data=current_user,
            message="Token is valid"
        )
    except Exception as e:
        return error_response(str(e), 401)

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile():
    """Get current user profile."""
    try:
        current_user = get_current_user()
        from models.user import find_user_by_id
        
        user = find_user_by_id(current_user['user_id'])
        if not user:
            return error_response("User not found", 404)
            
        return success_response(
            data=user.to_dict(),
            message="Profile retrieved successfully"
        )
    except Exception as e:
        return error_response(str(e), 500)

@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password():
    """Change user password."""
    try:
        data = request.get_json()
        if not data:
            return error_response("No data provided", 400)
        
        current_user = get_current_user()
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if not old_password or not new_password:
            return error_response("Both old and new passwords are required", 400)
        
        from services.auth_services import change_password
        change_password(current_user['user_id'], old_password, new_password)
        
        return success_response(message="Password changed successfully")
    except Exception as e:
        return error_response(str(e), 400)

# PUBLIC ENDPOINTS FOR FRONTEND ONBOARDING
@auth_bp.route('/public/organizations', methods=['GET'])
def get_public_organizations():
    """Get list of organizations for registration (public endpoint)."""
    try:
        from models.organisation import get_all_organisations
        organizations = get_all_organisations()
        return success_response(
            data=[{
                "org_id": org.org_id,
                "name": org.name,
                "description": org.description,
                "contact_email": org.contact_email
            } for org in organizations],
            message="Organizations retrieved successfully"
        )
    except Exception as e:
        return error_response(str(e), 500)

@auth_bp.route('/public/organizations', methods=['POST'])
def create_public_organization():
    """Create new organization (public endpoint for initial setup)."""
    try:
        data = request.get_json()
        if not data:
            return error_response("No data provided", 400)
        
        required_fields = ['name', 'description', 'contact_email']
        for field in required_fields:
            if not data.get(field):
                return error_response(f"{field} is required", 400)
        
        from models.organisation import create_organisation
        org = create_organisation(data)
        return success_response(
            data={
                "org_id": org.org_id,
                "name": org.name,
                "description": org.description,
                "contact_email": org.contact_email
            },
            message="Organization created successfully",
            status_code=201
        )
    except Exception as e:
        return error_response(str(e), 400)

@auth_bp.route('/public/admin', methods=['POST'])
def create_public_admin():
    """Create first admin user for an organization (public endpoint)."""
    try:
        data = request.get_json()
        if not data:
            return error_response("No data provided", 400)
        
        required_fields = ['name', 'email', 'password', 'org_id']
        for field in required_fields:
            if not data.get(field):
                return error_response(f"{field} is required", 400)
        
        # Verify organization exists
        from models.organisation import find_organisation_by_id
        org = find_organisation_by_id(data['org_id'])
        if not org:
            return error_response("Organization not found", 404)
        
        # Check if organization already has an admin
        from models.user import get_users_by_role
        existing_admins = get_users_by_role('admin', data['org_id'])
        if existing_admins:
            return error_response("Organization already has an admin. Use regular registration.", 400)
        
        # Set role to admin
        data['role'] = 'admin'
        
        # Validate input data  
        validation = validate_user_data(data)
        if not validation['is_valid']:
            return validation_error_response(validation['errors'])
        
        user = register_user(data)
        return success_response(
            data=user.to_dict(),
            message="Admin user created successfully",
            status_code=201
        )
    except Exception as e:
        return error_response(str(e), 400)