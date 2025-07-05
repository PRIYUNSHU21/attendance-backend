"""
📨 API RESPONSE UTILITIES - utils/response.py

🎯 WHAT THIS FILE DOES:
This file provides standardized response formats for all API endpoints.
Think of it as the "response formatter" that ensures all API responses look consistent.

🔧 FOR FRONTEND DEVELOPERS:
- ALL API responses use these standardized formats
- You can rely on consistent response structure across all endpoints
- Error handling is uniform throughout the API
- Simplifies frontend response parsing and error handling

📋 STANDARD RESPONSE FORMATS:

SUCCESS RESPONSE:
{
  "success": true,
  "message": "Operation completed successfully",
  "data": { ...actual data... },
  "timestamp": "2025-07-05T10:30:00Z"
}

ERROR RESPONSE:
{
  "success": false,
  "message": "Something went wrong",
  "error_code": "VALIDATION_ERROR",
  "details": { ...error details... },
  "timestamp": "2025-07-05T10:30:00Z"
}

VALIDATION ERROR RESPONSE:
{
  "success": false,
  "message": "Validation failed",
  "errors": [
    { "field": "email", "message": "Email is required" },
    { "field": "password", "message": "Password too short" }
  ],
  "timestamp": "2025-07-05T10:30:00Z"
}

PAGINATED RESPONSE:
{
  "success": true,
  "data": [...items...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "pages": 8
  },
  "message": "Data retrieved successfully"
}

🌐 FRONTEND INTEGRATION:

HANDLING SUCCESS RESPONSES:
const response = await fetch('/api/endpoint');
const result = await response.json();

if (result.success) {
  // Use result.data for the actual content
  console.log('Data:', result.data);
  showSuccessMessage(result.message);
} else {
  // Handle error
  showErrorMessage(result.message);
}

HANDLING VALIDATION ERRORS:
if (result.errors) {
  // Display field-specific errors
  result.errors.forEach(error => {
    showFieldError(error.field, error.message);
  });
}

HANDLING PAGINATION:
const { data, pagination } = result;
// data = current page items
// pagination.total = total number of items
// pagination.pages = total number of pages

⚡ RESPONSE FUNCTIONS AVAILABLE:
1. success_response(): Standard success with data
2. error_response(): Standard error with message
3. validation_error_response(): Field validation errors
4. paginated_response(): Paginated data with metadata

📱 EXAMPLE FRONTEND ERROR HANDLING:

async function apiCall(endpoint, options) {
  try {
    const response = await fetch(endpoint, options);
    const result = await response.json();
    
    if (!result.success) {
      // Handle API errors
      if (result.errors) {
        // Validation errors
        handleValidationErrors(result.errors);
      } else {
        // General errors
        showErrorMessage(result.message);
      }
      return null;
    }
    
    return result.data;
  } catch (error) {
    // Handle network errors
    showErrorMessage('Network error. Please try again.');
    return null;
  }
}

🔄 CONSISTENT STATUS CODES:
- 200: Success
- 201: Created successfully
- 400: Bad request / Validation error
- 401: Unauthorized / Invalid token
- 403: Forbidden / Insufficient permissions
- 404: Not found
- 500: Internal server error

🛡️ ERROR HANDLING BEST PRACTICES:
- Always check result.success before using data
- Display result.message to users for context
- Handle validation errors at field level
- Implement retry logic for network errors
- Log error details for debugging
"""

from flask import jsonify
from typing import Any, Dict, Optional

def success_response(data: Any = None, message: str = "Success", status_code: int = 200) -> tuple:
    """
    Create a successful response.
    
    Args:
        data: Data to include in response
        message: Success message
        status_code: HTTP status code
        
    Returns:
        Tuple of (response, status_code)
    """
    response = {
        "success": True,
        "message": message,
        "data": data
    }
    return jsonify(response), status_code

def error_response(message: str = "An error occurred", status_code: int = 400, 
                  error_code: Optional[str] = None, details: Optional[Dict] = None) -> tuple:
    """
    Create an error response.
    
    Args:
        message: Error message
        status_code: HTTP status code
        error_code: Optional error code for client handling
        details: Optional additional error details
        
    Returns:
        Tuple of (response, status_code)
    """
    response = {
        "success": False,
        "message": message,
        "error_code": error_code,
        "details": details
    }
    return jsonify(response), status_code

def validation_error_response(errors: Dict, message: str = "Validation failed") -> tuple:
    """
    Create a validation error response.
    
    Args:
        errors: Dictionary of validation errors
        message: Error message
        
    Returns:
        Tuple of (response, status_code)
    """
    return error_response(
        message=message,
        status_code=422,
        error_code="VALIDATION_ERROR",
        details={"validation_errors": errors}
    )

def unauthorized_response(message: str = "Unauthorized access") -> tuple:
    """
    Create an unauthorized response.
    
    Args:
        message: Error message
        
    Returns:
        Tuple of (response, status_code)
    """
    return error_response(
        message=message,
        status_code=401,
        error_code="UNAUTHORIZED"
    )

def forbidden_response(message: str = "Forbidden access") -> tuple:
    """
    Create a forbidden response.
    
    Args:
        message: Error message
        
    Returns:
        Tuple of (response, status_code)
    """
    return error_response(
        message=message,
        status_code=403,
        error_code="FORBIDDEN"
    )

def not_found_response(message: str = "Resource not found") -> tuple:
    """
    Create a not found response.
    
    Args:
        message: Error message
        
    Returns:
        Tuple of (response, status_code)
    """
    return error_response(
        message=message,
        status_code=404,
        error_code="NOT_FOUND"
    )

def conflict_response(message: str = "Resource conflict") -> tuple:
    """
    Create a conflict response.
    
    Args:
        message: Error message
        
    Returns:
        Tuple of (response, status_code)
    """
    return error_response(
        message=message,
        status_code=409,
        error_code="CONFLICT"
    )

def server_error_response(message: str = "Internal server error") -> tuple:
    """
    Create a server error response.
    
    Args:
        message: Error message
        
    Returns:
        Tuple of (response, status_code)
    """
    return error_response(
        message=message,
        status_code=500,
        error_code="SERVER_ERROR"
    )

def paginated_response(data: list, page: int, per_page: int, total: int, 
                      message: str = "Success") -> tuple:
    """
    Create a paginated response.
    
    Args:
        data: List of items for current page
        page: Current page number
        per_page: Items per page
        total: Total number of items
        message: Success message
        
    Returns:
        Tuple of (response, status_code)
    """
    total_pages = (total + per_page - 1) // per_page
    
    response = {
        "success": True,
        "message": message,
        "data": data,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }
    return jsonify(response), 200