# 📱 Frontend API Guide - Students Endpoint

## ✅ Working Endpoint

### Get Students in Teacher's Organization

```
GET https://attendance-backend-go8h.onrender.com/admin/students
```

**Headers:**
```javascript
{
  "Authorization": "Bearer <teacher_jwt_token>",
  "Content-Type": "application/json"
}
```

**Query Parameters (Optional):**
```
?page=1&per_page=10
```

## 📊 Response Format

### Success Response (200 OK)
```json
{
  "success": true,
  "message": "Found 1 students in organization",
  "data": {
    "students": [
      {
        "user_id": "student-uuid",
        "name": "GAMMA",
        "email": "gama@gmail.com",
        "role": "student",
        "org_id": "fc063474-991b-4747-ab88-43058fd50f4c",
        "is_active": true,
        "created_at": "2025-07-09T..."
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 10,
      "total": 1,
      "total_pages": 1,
      "has_next": false,
      "has_prev": false
    }
  }
}
```

## 🔐 Authentication

First login to get JWT token:

```javascript
// Login Teacher
POST https://attendance-backend-go8h.onrender.com/auth/login
{
  "email": "beta@gmail.com",
  "password": "Beta123#"
}

// Response
{
  "success": true,
  "data": {
    "user": {
      "name": "BETA",
      "role": "teacher",
      "org_id": "fc063474-991b-4747-ab88-43058fd50f4c"
    },
    "jwt_token": "eyJ..."
  }
}
```

## 🛠️ Frontend Implementation Example

```javascript
// Get JWT token from login
const teacherToken = "eyJ..."; // From login response

// Fetch students
const response = await fetch('https://attendance-backend-go8h.onrender.com/admin/students', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${teacherToken}`,
    'Content-Type': 'application/json'
  }
});

const data = await response.json();

if (data.success) {
  const students = data.data.students;
  const pagination = data.data.pagination;
  
  console.log(`Found ${students.length} students`);
  console.log(`Total: ${pagination.total}`);
  
  students.forEach(student => {
    console.log(`${student.name} (${student.email})`);
  });
}
```

## ✅ Status

- **Endpoint Status**: ✅ Live and Working
- **Authentication**: ✅ Teacher login working
- **Data**: ✅ Returns students with pagination
- **Last Tested**: September 1, 2025
