# 📱 FRONTEND INTEGRATION GUIDE - COMPLETE CHANGES REQUIRED

## 🔧 **CRITICAL BACKEND CHANGES - FRONTEND ACTION REQUIRED**

### 🌐 **Updated Production URL**
```javascript
// OLD URL (might be in your config)
const OLD_API_URL = "https://attendance-backend-4njr.onrender.com"

// NEW PRODUCTION URL - UPDATE ALL REFERENCES
const API_BASE_URL = "https://attendance-backend-go8h.onrender.com"
```

---

## 🔐 **AUTHENTICATION CHANGES**

### **1. Login Response Structure CHANGED**
```javascript
// OLD RESPONSE STRUCTURE (if you were using this)
{
  "token": "jwt_token_here",
  "user": {...}
}

// NEW RESPONSE STRUCTURE - UPDATE YOUR CODE
{
  "success": true,
  "message": "Login successful",
  "data": {
    "jwt_token": "eyJhbGciOiJIUzI1NiIs...",  // ← Extract from here
    "session_id": "uuid",
    "session_token": "session_token",
    "user": {
      "user_id": "uuid",
      "email": "user@example.com",
      "name": "User Name",
      "role": "teacher|student|admin",
      "org_id": "uuid",
      "is_active": true,
      "created_at": "2025-08-03T16:03:39.367885"
    }
  }
}
```

### **Frontend Login Code Update:**
```javascript
// BEFORE
const response = await fetch(`${API_URL}/auth/login`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
});
const data = await response.json();
const token = data.token; // ❌ OLD WAY

// AFTER - UPDATE YOUR CODE
const response = await fetch(`${API_URL}/auth/login`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
});
const data = await response.json();
const token = data.data.jwt_token; // ✅ NEW WAY
const user = data.data.user;
```

---

## 📍 **SESSION CREATION CHANGES**

### **2. Session Creation API Updated**
```javascript
// ENDPOINT CHANGE
// OLD: POST /api/admin/create-session
// NEW: POST /admin/sessions

// NEW SESSION CREATION REQUEST
const createSession = async (sessionData) => {
  const response = await fetch(`${API_URL}/admin/sessions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${jwt_token}` // Use jwt_token from login
    },
    body: JSON.stringify({
      session_name: "Class Name",
      description: "Optional description",
      start_time: "2025-08-03T20:00:00", // ISO format
      end_time: "2025-08-03T22:00:00",   // ISO format
      
      // LOCATION IS NOW OPTIONAL
      latitude: 28.6139,    // Optional - can be omitted
      longitude: 77.2090,   // Optional - can be omitted  
      radius: 100           // Optional - defaults to 100 meters
    })
  });
  
  const result = await response.json();
  return result.data; // Session data is in .data property
};
```

### **3. Session Creation Response Structure**
```javascript
// SUCCESS RESPONSE
{
  "success": true,
  "message": "Attendance session created successfully",
  "data": {
    "session_id": "uuid",
    "session_name": "Class Name",
    "description": "Description",
    "org_id": "uuid",
    "start_time": "2025-08-03T20:00:00",
    "end_time": "2025-08-03T22:00:00",
    "latitude": 28.6139,    // Can be null
    "longitude": 77.2090,   // Can be null
    "radius": 100,
    "created_by": "uuid",
    "created_at": "2025-08-03T14:18:03.701787",
    "updated_at": "2025-08-03T14:18:03.701792",
    "is_active": true
  }
}
```

---

## 🎯 **ATTENDANCE MARKING CHANGES**

### **4. Attendance Marking - SIMPLIFIED API**
```javascript
// ENDPOINT: POST /simple/mark-attendance
// This is the FIREBASE-INSPIRED simplified endpoint

const markAttendance = async (sessionId, latitude, longitude) => {
  const response = await fetch(`${API_URL}/simple/mark-attendance`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${jwt_token}`
    },
    body: JSON.stringify({
      session_id: sessionId,
      latitude: latitude,
      longitude: longitude
      // That's it! Everything else is handled automatically
    })
  });
  
  const result = await response.json();
  return result;
};
```

### **5. Attendance Response Structure**
```javascript
// SUCCESS RESPONSE
{
  "success": true,
  "message": "Attendance marked successfully",
  "data": {
    "attendance_id": "uuid",
    "session_id": "uuid",
    "user_id": "uuid",
    "marked_at": "2025-08-03T14:25:10.123456",
    "location": "28.6139,77.2090",
    "distance_from_session": 25.7, // meters
    "is_within_radius": true,
    "status": "present"
  }
}

// ERROR RESPONSE EXAMPLES
{
  "success": false,
  "message": "Session not found or not active",
  "error_code": "SESSION_NOT_FOUND"
}

{
  "success": false, 
  "message": "You are too far from the session location (156.2m away, max 100m)",
  "error_code": "LOCATION_OUT_OF_RANGE"
}
```

---

## 🏢 **COMPANY/ORGANIZATION SETUP**

### **6. Company Location Setup (For Teachers/Admins)**
```javascript
// ENDPOINT: POST /simple/company/create
// Teachers and Admins can set up company locations

const setupCompanyLocation = async (locationData) => {
  const response = await fetch(`${API_URL}/simple/company/create`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${jwt_token}`
    },
    body: JSON.stringify({
      name: "Company/School Name",
      address: "Full Address",
      latitude: 28.6139,
      longitude: 77.2090,
      radius: 100 // Default attendance radius
    })
  });
  
  return await response.json();
};
```

---

## 📊 **SESSION LISTING CHANGES**

### **7. Get Sessions for Organization**
```javascript
// ENDPOINT: GET /admin/sessions
const getSessions = async () => {
  const response = await fetch(`${API_URL}/admin/sessions`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${jwt_token}`
    }
  });
  
  const result = await response.json();
  return result.data; // Array of sessions
};
```

---

## 🔄 **ERROR HANDLING UPDATES**

### **8. Standardized Error Response Format**
```javascript
// ALL API responses now follow this format
const handleApiResponse = async (response) => {
  const data = await response.json();
  
  if (data.success) {
    return data.data; // Actual data is always in .data property
  } else {
    // Handle errors
    throw new Error(data.message || 'API Error');
  }
};

// Example usage
try {
  const sessions = await handleApiResponse(
    await fetch(`${API_URL}/admin/sessions`, { 
      headers: { 'Authorization': `Bearer ${token}` }
    })
  );
  console.log('Sessions:', sessions);
} catch (error) {
  console.error('Error:', error.message);
}
```

---

## 🧪 **TESTING CREDENTIALS**

### **9. Updated Test Credentials**
```javascript
// Use these for testing your frontend integration
const TEST_CREDENTIALS = {
  ADMIN: {
    email: "psaha21.un@gmail.com",
    password: "P21042004p#"
  },
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

---

## 🔍 **DEBUGGING & MONITORING**

### **10. Health Check Endpoint**
```javascript
// Use this to verify backend connectivity
const checkBackendHealth = async () => {
  try {
    const response = await fetch(`${API_URL}/health`);
    const data = await response.json();
    console.log('Backend Status:', data);
    return data.data.status === 'healthy';
  } catch (error) {
    console.error('Backend not reachable:', error);
    return false;
  }
};
```

---

## 📱 **COMPLETE FRONTEND EXAMPLE**

### **11. Complete Integration Example**
```javascript
class AttendanceAPI {
  constructor() {
    this.baseURL = 'https://attendance-backend-go8h.onrender.com';
    this.token = localStorage.getItem('jwt_token');
  }

  async login(email, password) {
    const response = await fetch(`${this.baseURL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    
    const data = await response.json();
    if (data.success) {
      this.token = data.data.jwt_token;
      localStorage.setItem('jwt_token', this.token);
      localStorage.setItem('user', JSON.stringify(data.data.user));
      return data.data.user;
    }
    throw new Error(data.message);
  }

  async createSession(sessionData) {
    const response = await fetch(`${this.baseURL}/admin/sessions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`
      },
      body: JSON.stringify(sessionData)
    });
    
    const data = await response.json();
    if (data.success) return data.data;
    throw new Error(data.message);
  }

  async markAttendance(sessionId, latitude, longitude) {
    const response = await fetch(`${this.baseURL}/simple/mark-attendance`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`
      },
      body: JSON.stringify({
        session_id: sessionId,
        latitude,
        longitude
      })
    });
    
    const data = await response.json();
    if (data.success) return data.data;
    throw new Error(data.message);
  }

  async getSessions() {
    const response = await fetch(`${this.baseURL}/admin/sessions`, {
      headers: { 'Authorization': `Bearer ${this.token}` }
    });
    
    const data = await response.json();
    if (data.success) return data.data;
    throw new Error(data.message);
  }
}

// Usage
const api = new AttendanceAPI();

// Login
const user = await api.login('alpha@gmail.com', 'P21042004p#');

// Create session
const session = await api.createSession({
  session_name: 'Math Class',
  description: 'Advanced Mathematics',
  start_time: '2025-08-03T20:00:00',
  end_time: '2025-08-03T21:00:00',
  latitude: 28.6139,
  longitude: 77.2090,
  radius: 100
});

// Mark attendance  
const attendance = await api.markAttendance(
  session.session_id, 
  28.6139, 
  77.2090
);
```

---

## ⚠️ **BREAKING CHANGES SUMMARY**

### **MUST UPDATE:**
1. **API Base URL** → `https://attendance-backend-go8h.onrender.com`
2. **Login Response** → Extract `data.data.jwt_token` not `data.token`
3. **Session Creation** → Use `/admin/sessions` not `/api/admin/create-session`
4. **Response Format** → All data is in `.data` property
5. **Authentication Header** → Use JWT token from login response

### **NEW FEATURES:**
1. **Optional Location** → Sessions can be created without location data
2. **Simplified Attendance** → Single endpoint handles everything
3. **Better Error Messages** → Detailed error responses
4. **Health Monitoring** → Backend health check endpoint

---

## 🎯 **NEXT STEPS FOR FRONTEND**

1. **Update API Base URL** in all configuration files
2. **Update Authentication Logic** to extract JWT from new response format  
3. **Update Session Creation** to use new endpoint and format
4. **Test All Flows** with the provided test credentials
5. **Implement Error Handling** for the new response format
6. **Test Location Optional** behavior for sessions

**Your backend is now production-ready and fully tested!** 🚀
