# User/Student API Integration Guide

## 📋 Endpoints for User/Student Data

### 1. Get Users/Students for an Organization

#### Primary Endpoint:
```
GET /admin/users
```

#### Parameters:
- **page** (integer, optional): Page number for pagination, default is 1
- **per_page** (integer, optional): Number of results per page, default is 20
- **role** (string, optional): Filter by user role. Use `"student"` to get only students

#### Example Requests:
```javascript
// Get all users in your organization (paginated)
fetch('https://attendance-backend-go8h.onrender.com/admin/users?page=1&per_page=20', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${jwt_token}`,
    'Content-Type': 'application/json'
  }
})

// Get only students in your organization (paginated)
fetch('https://attendance-backend-go8h.onrender.com/admin/users?page=1&per_page=20&role=student', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${jwt_token}`,
    'Content-Type': 'application/json'
  }
})
```

#### Response Structure:
```json
{
  "success": true,
  "message": "Users retrieved successfully",
  "data": [
    {
      "user_id": "8fa267ed-5410-462a-98f5-fb6e3b8e4656",
      "name": "Student Name",
      "email": "student@example.com",
      "role": "student",
      "org_id": "74f8a6e5-296c-4b65-9bb3-6a3c050c3584",
      "created_at": "2025-07-15T14:23:16.591847",
      "is_active": true
    },
    // More users...
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 45,
    "total_pages": 3
  }
}
```

### 2. Get Specific User Details

```
GET /admin/users/{user_id}
```

#### Example:
```javascript
fetch(`https://attendance-backend-go8h.onrender.com/admin/users/${userId}`, {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${jwt_token}`,
    'Content-Type': 'application/json'
  }
})
```

#### Response:
```json
{
  "success": true,
  "message": "User retrieved successfully",
  "data": {
    "user_id": "8fa267ed-5410-462a-98f5-fb6e3b8e4656",
    "name": "Student Name",
    "email": "student@example.com",
    "role": "student",
    "org_id": "74f8a6e5-296c-4b65-9bb3-6a3c050c3584",
    "created_at": "2025-07-15T14:23:16.591847",
    "is_active": true
  }
}
```

## 💡 Important Notes

1. **Authorization**: All endpoints require a valid JWT token in the Authorization header
2. **Pagination**: The server uses pagination for listing users to improve performance
3. **Default Behavior**: The API automatically filters users by the current user's organization
   - Teachers see only users in their own organization
   - Admins can see users across all organizations
4. **Filtering by Role**: Use the `role` parameter to specifically get students

## 📱 Complete Working Example

```javascript
class UserAPI {
  constructor(baseURL, jwtToken) {
    this.baseURL = baseURL;
    this.jwtToken = jwtToken;
  }

  // Get headers with authentication
  get headers() {
    return {
      'Authorization': `Bearer ${this.jwtToken}`,
      'Content-Type': 'application/json'
    };
  }

  // Get all students in organization (paginated)
  async getStudents(page = 1, perPage = 20) {
    try {
      const response = await fetch(
        `${this.baseURL}/admin/users?page=${page}&per_page=${perPage}&role=student`, 
        { headers: this.headers }
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching students:', error);
      return { success: false, error: error.message };
    }
  }

  // Get specific user details
  async getUser(userId) {
    try {
      const response = await fetch(
        `${this.baseURL}/admin/users/${userId}`,
        { headers: this.headers }
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching user details:', error);
      return { success: false, error: error.message };
    }
  }
}

// Usage example
const api = new UserAPI('https://attendance-backend-go8h.onrender.com', 'your-jwt-token');

// Get students (first page)
api.getStudents().then(response => {
  if (response.success) {
    const students = response.data;
    const pagination = response.pagination;
    
    console.log(`Showing ${students.length} of ${pagination.total} students`);
    console.log(`Page ${pagination.page} of ${pagination.total_pages}`);
    
    // Display students
    students.forEach(student => {
      console.log(`${student.name} (${student.email})`);
    });
  }
});

// Get specific user details
api.getUser('8fa267ed-5410-462a-98f5-fb6e3b8e4656').then(response => {
  if (response.success) {
    const user = response.data;
    console.log(`User details for ${user.name}:`, user);
  }
});
```

## ❓ Frequently Asked Questions

### Q: Is there a separate endpoint just for students?
No, use the `/admin/users` endpoint with the `role=student` parameter to filter for students only.

### Q: Can I get users from a different organization than my own?
No, the API automatically filters by your organization. Only users with the "admin" role can access users across different organizations.

### Q: How can I search or filter users beyond just their role?
The current API version only supports filtering by role. For more advanced filtering, you'll need to filter the results client-side after retrieval.

### Q: What permissions are needed to access these endpoints?
You need either a "teacher" or "admin" role to access user information. Students cannot access these endpoints.

### Q: Does the API support searching users by name or email?
The current API version doesn't support server-side search. Implement client-side filtering for this functionality.

### Q: How does this API relate to the attendance system?
For complete attendance system integration, please refer to the separate `FRONTEND_IMPLEMENTATION_GUIDE.md` document, which details the attendance marking endpoints and location requirements for the SAHA organization.
