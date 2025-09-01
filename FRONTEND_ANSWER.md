# Frontend Team - User/Student API Information

## 🎯 DIRECT ANSWERS TO YOUR QUESTIONS

### Q: What is the correct API endpoint to get users/students for an organization?

**Answer:** 
```
GET /admin/users
```

### Q: What parameters does the endpoint expect?

**Answer:**
- `page` (optional, default=1): Page number for pagination
- `per_page` (optional, default=20): Number of results per page  
- `role` (optional): Filter by role - use `role=student` to get only students

## 🚀 API USAGE EXAMPLES

### Get All Students in Organization:
```javascript
fetch('https://attendance-backend-go8h.onrender.com/admin/users?role=student&page=1&per_page=20', {
  headers: {
    'Authorization': `Bearer ${jwtToken}`,
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => {
  console.log('Students:', data.data);
  console.log('Pagination:', data.pagination);
});
```

### Get All Users (Students + Teachers):
```javascript
fetch('https://attendance-backend-go8h.onrender.com/admin/users?page=1&per_page=20', {
  headers: {
    'Authorization': `Bearer ${jwtToken}`,
    'Content-Type': 'application/json'
  }
})
```

### Get Specific User Details:
```javascript
fetch(`https://attendance-backend-go8h.onrender.com/admin/users/${userId}`, {
  headers: {
    'Authorization': `Bearer ${jwtToken}`,
    'Content-Type': 'application/json'
  }
})
```

## 📋 RESPONSE FORMAT

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
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 45,
    "total_pages": 3
  }
}
```

## 🔑 IMPORTANT NOTES

1. **Authorization Required**: Must include JWT token in Authorization header
2. **Organization Filtering**: API automatically filters by your organization
3. **Pagination**: Server uses pagination for performance
4. **Role Filtering**: Use `role=student` to get only students

## 📞 TEST ACCOUNTS

```javascript
const TEST_ACCOUNTS = {
  TEACHER: { 
    email: "alpha@gmail.com", 
    password: "P21042004p#" 
  },
  STUDENT: { 
    email: "beta@gmail.com", 
    password: "P21042004p#" 
  }
};
```

That's it! Use the `/admin/users` endpoint with the parameters above.
