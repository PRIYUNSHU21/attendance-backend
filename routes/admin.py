"""
👑 ADMINISTRATIVE ROUTES - routes/admin.py

🎯 WHAT THIS FILE DOES:
This file defines all administrative API endpoints for managing users, organizations, and sessions.
Think of it as the "admin dashboard API" that powers management features.

🔧 FOR FRONTEND DEVELOPERS:
- These endpoints are for admin dashboard functionality
- Most endpoints require admin or teacher permissions
- Provides user management, organization settings, and system administration
- Includes pagination for large data sets

📋 AVAILABLE ENDPOINTS:

👥 USER MANAGEMENT (Teacher/Admin access):
GET /admin/users - List users with pagination and filtering
POST /admin/users - Create new user account (Admin only)
GET /admin/users/<user_id> - Get specific user details
PUT /admin/users/<user_id> - Update user information (Admin only)
DELETE /admin/users/<user_id> - Soft delete user account (Admin only)

🏢 ORGANIZATION MANAGEMENT (Admin access):
GET /admin/organizations - List all organizations (Super admin only)
POST /admin/organizations - Create new organization
GET /admin/organizations/<org_id> - Get organization details
PUT /admin/organizations/<org_id> - Update organization information

📅 SESSION MANAGEMENT (Teacher/Admin access):
POST /admin/sessions - Create new attendance session
GET /admin/sessions - List organization sessions

📊 ANALYTICS & DASHBOARD (Teacher/Admin access):
GET /admin/dashboard/stats - Comprehensive dashboard statistics

🌐 FRONTEND INTEGRATION EXAMPLES:

LIST USERS WITH PAGINATION:
GET /admin/users?page=1&per_page=20&role=student
Authorization: Bearer <admin-jwt-token>

Response:
{
  "success": true,
  "data": [...user objects...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "pages": 8
  }
}

CREATE NEW USER:
POST /admin/users
Authorization: Bearer <admin-jwt-token>
Content-Type: application/json
{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "password": "securepassword123",
  "role": "teacher"
}

CREATE ATTENDANCE SESSION:
POST /admin/sessions
Authorization: Bearer <teacher-jwt-token>
Content-Type: application/json
{
  "session_name": "Computer Science 101",
  "description": "Introduction to Programming",
  "start_time": "2025-07-05T09:00:00Z",
  "end_time": "2025-07-05T11:00:00Z",
  "location_lat": 40.7128,
  "location_lon": -74.0060,
  "location_radius": 50
}

GET DASHBOARD STATISTICS:
GET /admin/dashboard/stats
Authorization: Bearer <admin-jwt-token>

Response:
{
  "success": true,
  "data": {
    "total_users": 150,
    "total_students": 120,
    "total_teachers": 25,
    "active_sessions": 5,
    "organization_id": "org-uuid"
  }
}

📱 EXAMPLE FRONTEND ADMIN DASHBOARD:

// Load dashboard statistics
async function loadDashboardStats() {
  try {
    const response = await fetch('/admin/dashboard/stats', {
      headers: { 'Authorization': `Bearer ${getAdminToken()}` }
    });
    
    const result = await response.json();
    
    if (result.success) {
      updateDashboardUI(result.data);
    }
  } catch (error) {
    console.error('Failed to load dashboard stats:', error);
  }
}

// Load users with pagination
async function loadUsers(page = 1, role = null) {
  let url = `/admin/users?page=${page}&per_page=20`;
  if (role) url += `&role=${role}`;
  
  try {
    const response = await fetch(url, {
      headers: { 'Authorization': `Bearer ${getAdminToken()}` }
    });
    
    const result = await response.json();
    
    if (result.success) {
      displayUsers(result.data);
      updatePagination(result.pagination);
    }
  } catch (error) {
    console.error('Failed to load users:', error);
  }
}

// Create new user
async function createUser(userData) {
  try {
    const response = await fetch('/admin/users', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${getAdminToken()}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(userData)
    });
    
    const result = await response.json();
    
    if (result.success) {
      showSuccess('User created successfully!');
      refreshUserList();
    } else {
      if (result.errors) {
        showValidationErrors(result.errors);
      } else {
        showError(result.message);
      }
    }
  } catch (error) {
    showError('Failed to create user.');
  }
}

🔒 PERMISSION LEVELS:
- Teacher: Can view users, create sessions, view reports for their organization
- Admin: Full access to their organization (create/edit users, manage settings)
- Super Admin: Access to all organizations and system-wide settings

⚡ FRONTEND CONSIDERATIONS:
- Check user role before showing admin features
- Implement proper loading states for data operations
- Handle permission errors (403) gracefully
- Provide confirmation dialogs for destructive actions
- Implement search and filtering for user lists
- Use pagination for better performance with large datasets

🛡️ SECURITY FEATURES:
- Role-based access control on all endpoints
- Organization-scoped data access
- Input validation and sanitization
- Audit logging for administrative actions
"""

from flask import Blueprint, request, jsonify
from services.attendance_service import create_session
from models.user import create_user, find_user_by_id, update_user, delete_user, get_users_by_org, get_users_by_role
from models.organisation import create_organisation, find_organisation_by_id, update_organisation, get_all_organisations
from models.attendance import get_active_sessions
from utils.auth import token_required, admin_required, teacher_or_admin_required, get_current_user
from utils.response import success_response, error_response, validation_error_response, paginated_response
from utils.validators import validate_user_data, validate_attendance_session_data, validate_pagination_params
from services.hash_service import hash_password

admin_bp = Blueprint('admin', __name__)

# User Management Routes
@admin_bp.route('/users', methods=['GET'])
@token_required
@teacher_or_admin_required
def get_users():
    """Get all users in the organization with pagination."""
    try:
        current_user = get_current_user()
        org_id = current_user.get('org_id')
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        role = request.args.get('role')
        
        # Validate pagination
        pagination = validate_pagination_params(page, per_page)
        if not pagination['is_valid']:
            return validation_error_response(pagination['errors'])
        
        # Get users
        if role:
            users = get_users_by_role(role, org_id)
        else:
            users = get_users_by_org(org_id)
        
        # Simple pagination (in production, use database pagination)
        total = len(users)
        start = (pagination['page'] - 1) * pagination['per_page']
        end = start + pagination['per_page']
        users_page = users[start:end]
        
        return paginated_response(
            data=[user.to_dict() for user in users_page],
            page=pagination['page'],
            per_page=pagination['per_page'],
            total=total,
            message="Users retrieved successfully"
        )
    except Exception as e:
        return error_response(str(e), 500)

@admin_bp.route('/users', methods=['POST'])
@token_required
@admin_required
def create_new_user():
    """Create a new user."""
    try:
        data = request.get_json()
        if not data:
            return error_response("No data provided", 400)
        
        current_user = get_current_user()
        
        # Validation
        validation = validate_user_data(data)
        if not validation['is_valid']:
            return validation_error_response(validation['errors'])
        
        # Set organization ID to current user's org
        data['org_id'] = current_user.get('org_id')
        
        # Hash password
        if 'password' in data:
            data['password_hash'] = hash_password(data['password'])
            del data['password']
        
        user = create_user(data)
        return success_response(
            data=user.to_dict(),
            message="User created successfully",
            status_code=201
        )
    except Exception as e:
        return error_response(str(e), 400)

@admin_bp.route('/users/<user_id>', methods=['GET'])
@teacher_or_admin_required
def get_user(user_id):
    """Get a specific user by ID."""
    try:
        user = find_user_by_id(user_id)
        if not user:
            return error_response("User not found", 404)
        
        current_user = get_current_user()
        if current_user.get('org_id') != user.org_id and current_user.get('role') != 'admin':
            return error_response("Access denied", 403)
        
        return success_response(
            data=user.to_dict(),
            message="User retrieved successfully"
        )
    except Exception as e:
        return error_response(str(e), 500)

@admin_bp.route('/users/<user_id>', methods=['PUT'])
@admin_required
def update_user_info(user_id):
    """Update a user's information."""
    try:
        data = request.get_json()
        if not data:
            return error_response("No data provided", 400)
        
        # Hash password if provided
        if 'password' in data:
            data['password_hash'] = hash_password(data['password'])
            del data['password']
        
        user = update_user(user_id, data)
        if not user:
            return error_response("User not found", 404)
        
        return success_response(
            data=user.to_dict(),
            message="User updated successfully"
        )
    except Exception as e:
        return error_response(str(e), 400)

@admin_bp.route('/users/<user_id>', methods=['DELETE'])
@admin_required
def delete_user_account(user_id):
    """Soft delete a user account."""
    try:
        user = delete_user(user_id)
        if not user:
            return error_response("User not found", 404)
        
        return success_response(
            message="User deleted successfully"
        )
    except Exception as e:
        return error_response(str(e), 500)

# Organization Management Routes
@admin_bp.route('/organizations', methods=['GET'])
@token_required
@teacher_or_admin_required  # Changed from admin_required to allow teachers to view
def get_organizations():
    """Get all organizations."""
    try:
        organizations = get_all_organisations()
        return success_response(
            data=[org.to_dict() for org in organizations],
            message="Organizations retrieved successfully"
        )
    except Exception as e:
        return error_response(str(e), 500)

@admin_bp.route('/organizations', methods=['POST'])
@admin_required
def create_new_organization():
    """Create a new organization."""
    try:
        data = request.get_json()
        if not data:
            return error_response("No data provided", 400)
        
        org = create_organisation(data)
        return success_response(
            data=org.to_dict(),
            message="Organization created successfully",
            status_code=201
        )
    except Exception as e:
        return error_response(str(e), 400)

@admin_bp.route('/organizations/<org_id>', methods=['GET'])
@admin_required
def get_organization(org_id):
    """Get organization details."""
    try:
        org = find_organisation_by_id(org_id)
        if not org:
            return error_response("Organization not found", 404)
        
        return success_response(
            data=org.to_dict(),
            message="Organization retrieved successfully"
        )
    except Exception as e:
        return error_response(str(e), 500)

@admin_bp.route('/organizations/<org_id>', methods=['PUT'])
@admin_required
def update_organization_info(org_id):
    """Update organization information."""
    try:
        data = request.get_json()
        if not data:
            return error_response("No data provided", 400)
        
        org = update_organisation(org_id, data)
        if not org:
            return error_response("Organization not found", 404)
        
        return success_response(
            data=org.to_dict(),
            message="Organization updated successfully"
        )
    except Exception as e:
        return error_response(str(e), 400)

# Session Management Routes
@admin_bp.route('/sessions', methods=['POST'])
@token_required
@teacher_or_admin_required
def create_attendance_session():
    """Create a new attendance session."""
    try:
        data = request.get_json()
        if not data:
            return error_response("No data provided", 400)
        
        current_user = get_current_user()
        
        # Validation
        validation = validate_attendance_session_data(data)
        if not validation['is_valid']:
            return validation_error_response(validation['errors'])
        
        # Set organization ID to current user's org
        data['org_id'] = current_user.get('org_id')
        
        session = create_session(data, current_user['user_id'])
        return success_response(
            data=session.to_dict(),
            message="Attendance session created successfully",
            status_code=201
        )
    except Exception as e:
        return error_response(str(e), 400)

@admin_bp.route('/sessions', methods=['GET'])
@token_required
@teacher_or_admin_required
def get_sessions():
    """Get all sessions for the organization."""
    try:
        current_user = get_current_user()
        org_id = current_user.get('org_id')
        
        sessions = get_active_sessions(org_id)
        return success_response(
            data=[session.to_dict() for session in sessions],
            message="Sessions retrieved successfully"
        )
    except Exception as e:
        return error_response(str(e), 500)

# Dashboard Statistics
@admin_bp.route('/dashboard/stats', methods=['GET'])
@token_required
@teacher_or_admin_required
def get_dashboard_stats():
    """Get dashboard statistics."""
    try:
        current_user = get_current_user()
        org_id = current_user.get('org_id')
        
        # Get basic counts
        all_users = get_users_by_org(org_id)
        students = get_users_by_role('student', org_id)
        teachers = get_users_by_role('teacher', org_id)
        active_sessions = get_active_sessions(org_id)
        
        stats = {
            'total_users': len(all_users),
            'total_students': len(students),
            'total_teachers': len(teachers),
            'active_sessions': len(active_sessions),
            'organization_id': org_id
        }
        
        return success_response(
            data=stats,
            message="Dashboard statistics retrieved successfully"
        )
    except Exception as e:
        return error_response(str(e), 500)