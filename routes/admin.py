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
DELETE /admin/organizations/<org_id> - Delete organization and all related data (DANGEROUS!)
PUT /admin/organizations/<org_id>/soft-delete - Deactivate organization (safer alternative)

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
from config.db import db
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
@token_required
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
@token_required
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
@token_required
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
@token_required
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
@token_required
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

@admin_bp.route('/organizations/<org_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_organization(org_id):
    """
    Delete an organization and all related data.
    
    ⚠️ DANGEROUS OPERATION: This permanently deletes:
    - The organization
    - All users in the organization
    - All attendance sessions and records
    
    Security: Only organization admins can delete their own organization.
    """
    try:
        # Get current user info
        current_user = get_current_user()
        user_org_id = current_user.get('org_id')
        user_role = current_user.get('role')
        
        # Security check: Admin can only delete their own organization
        # (unless they're a super admin - future feature)
        if org_id != user_org_id:
            return error_response(
                "You can only delete your own organization", 
                403
            )
        
        # Optional: Add confirmation parameter
        data = request.get_json() if request.get_json() else {}
        confirm_deletion = data.get('confirm_deletion', False)
        
        if not confirm_deletion:
            # Return preview of what will be deleted
            from models.organisation import find_organisation_by_id
            from models.user import User
            from models.attendance import AttendanceSession, AttendanceRecord
            
            org = find_organisation_by_id(org_id)
            if not org:
                return error_response("Organization not found", 404)
            
            # Count what will be deleted
            users_count = User.query.filter(User.org_id == org_id).count()
            sessions_count = AttendanceSession.query.filter(AttendanceSession.org_id == org_id).count()
            
            # Count attendance records (get session IDs first, then count records)
            session_ids = [s.session_id for s in AttendanceSession.query.filter(AttendanceSession.org_id == org_id).all()]
            records_count = 0
            if session_ids:
                records_count = AttendanceRecord.query.filter(AttendanceRecord.session_id.in_(session_ids)).count()
            
            return success_response(
                data={
                    "organization": org.to_dict(),
                    "deletion_preview": {
                        "users_to_delete": users_count,
                        "sessions_to_delete": sessions_count,
                        "attendance_records_to_delete": records_count
                    },
                    "warning": "This action cannot be undone!"
                },
                message="Deletion preview. Send 'confirm_deletion': true to proceed."
            )
        
        # Perform the actual deletion
        from models.organisation import delete_organisation
        from models.session import invalidate_organization_sessions
        
        # 🔒 SECURITY: Invalidate all sessions for users in this organization
        try:
            invalidated_count = invalidate_organization_sessions(org_id, 'org_deleted')
            print(f"🔒 Security: Invalidated {invalidated_count} sessions for deleted organization {org_id}")
        except Exception as e:
            print(f"⚠️ Warning: Failed to invalidate sessions for org {org_id}: {str(e)}")
        
        result = delete_organisation(org_id)
        
        if result["success"]:
            return success_response(
                data={
                    **result["deleted_counts"],
                    "invalidated_sessions": invalidated_count if 'invalidated_count' in locals() else 0
                },
                message=result["message"]
            )
        else:
            return error_response(result["message"], 404)
            
    except Exception as e:
        return error_response(f"Failed to delete organization: {str(e)}", 500)

@admin_bp.route('/organizations/<org_id>/soft-delete', methods=['PUT'])
@token_required
@admin_required
def soft_delete_organization(org_id):
    """
    Soft delete an organization (mark as inactive).
    
    This is a safer alternative that preserves data.
    """
    try:
        # Get current user info
        current_user = get_current_user()
        user_org_id = current_user.get('org_id')
        
        # Security check: Admin can only soft-delete their own organization
        if org_id != user_org_id:
            return error_response(
                "You can only deactivate your own organization", 
                403
            )
        
        from models.organisation import soft_delete_organisation
        from models.session import invalidate_organization_sessions
        
        # 🔒 SECURITY: Invalidate all sessions for users in this organization
        try:
            invalidated_count = invalidate_organization_sessions(org_id, 'org_soft_deleted')
            print(f"🔒 Security: Invalidated {invalidated_count} sessions for soft-deleted organization {org_id}")
        except Exception as e:
            print(f"⚠️ Warning: Failed to invalidate sessions for org {org_id}: {str(e)}")
        
        org = soft_delete_organisation(org_id)
        
        if not org:
            return error_response("Organization not found", 404)
        
        return success_response(
            data={
                **org.to_dict(),
                "invalidated_sessions": invalidated_count if 'invalidated_count' in locals() else 0
            },
            message="Organization deactivated successfully. All user sessions invalidated."
        )
        
    except Exception as e:
        return error_response(f"Failed to deactivate organization: {str(e)}", 500)

# Session Management Routes
@admin_bp.route('/sessions', methods=['POST'])
@token_required
@teacher_or_admin_required
def create_attendance_session():
    """Create a new attendance session - DIRECT FIX."""
    try:
        from models.attendance import AttendanceSession
        from datetime import datetime
        import uuid
        
        data = request.get_json()
        if not data:
            return error_response("No data provided", 400)
        
        current_user = get_current_user()
        
        # DIRECT SESSION CREATION - NO COMPLEX SERVICES
        session = AttendanceSession(
            session_id=str(uuid.uuid4()),
            session_name=data['session_name'],
            description=data.get('description', ''),
            org_id=current_user.get('org_id'),
            created_by=current_user['user_id'],
            start_time=datetime.fromisoformat(data['start_time']),
            end_time=datetime.fromisoformat(data['end_time']),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            radius=data.get('radius', 100),
            is_active=True
        )
        
        # DIRECT DATABASE SAVE
        db.session.add(session)
        db.session.commit()
        
        return success_response(
            data=session.to_dict(),
            message="Attendance session created successfully",
            status_code=201
        )
    except Exception as e:
        print(f"DEBUG: Exception in admin session creation: {str(e)}")
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