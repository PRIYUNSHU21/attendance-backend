# 🚀 FRONTEND INTEGRATION GUIDE - ATTENDANCE SYSTEM FIXED ✅

## 🎉 GOOD NEWS: All Backend Issues Resolved!

The attendance marking system is now **100% FUNCTIONAL**. All critical errors have been fixed and tested successfully.

---

## 📡 PRODUCTION API BASE URL

```javascript
const API_BASE_URL = "https://attendance-backend-go8h.onrender.com"
```

---

## 🔑 AUTHENTICATION FLOW

### 1. Login Endpoint
```javascript
// POST /auth/login
const loginResponse = await fetch(`${API_BASE_URL}/auth/login`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    email: "student@example.com",
    password: "password123"
  })
});

const loginData = await loginResponse.json();

// ✅ IMPORTANT: Extract tokens correctly
const jwtToken = loginData.data.jwt_token;        // For API authentication
const sessionToken = loginData.data.session_token; // For attendance marking
const userInfo = loginData.data.user;             // User details
```

### 2. Response Format
```javascript
{
  "success": true,
  "message": "Login successful", 
  "data": {
    "jwt_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "session_token": "wRGXCg0ZA1FZo6Io9R-Z...",
    "user": {
      "user_id": "8fa267ed-5410-462a-98f5-fb6e3b8e4656",
      "name": "Student Name",
      "email": "student@example.com", 
      "role": "student",
      "org_id": "74f8a6e5-296c-4b65-9bb3-6a3c050c3584"
    }
  }
}
```

---

## 📍 ATTENDANCE MARKING (MAIN ENDPOINT)

### ⚠️ IMPORTANT: Organization Location

The SAHA organization has its location set to **Kolkata, India**:
- **Latitude**: 22.6499919
- **Longitude**: 88.3640317
- **Radius**: 100 meters

Students must be within the 100-meter radius to be marked as **PRESENT**. Any location outside this radius will be marked as **ABSENT**.

### Endpoint: `/simple/mark-attendance`

```javascript
// ✅ WORKING EXAMPLE - Copy this exactly!
const markAttendance = async (jwtToken, sessionToken, latitude, longitude) => {
  const response = await fetch(`${API_BASE_URL}/simple/mark-attendance`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${jwtToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      session_code: sessionToken,  // ✅ Use session_token from login
      latitude: latitude,          // ✅ String, number, or decimal - all work!
      longitude: longitude,        // ✅ String, number, or decimal - all work!
      accuracy: 10                 // Optional: GPS accuracy in meters
    })
  });

  return await response.json();
};

// Usage examples:
await markAttendance(jwtToken, sessionToken, "22.6499919", "88.3640317");     // ✅ PRESENT (org location)
await markAttendance(jwtToken, sessionToken, 22.6499919, 88.3640317);         // ✅ PRESENT (numbers work)  
await markAttendance(jwtToken, sessionToken, 22.6500919, 88.3641317);         // ✅ PRESENT (nearby - 15m away)
// Usage examples:
await markAttendance(jwtToken, sessionToken, "22.6499919", "88.3640317");     // ✅ PRESENT (org location)
await markAttendance(jwtToken, sessionToken, 22.6499919, 88.3640317);         // ✅ PRESENT (numbers work)  
await markAttendance(jwtToken, sessionToken, 22.6500919, 88.3641317);         // ✅ PRESENT (nearby - 15m away)
await markAttendance(jwtToken, sessionToken, 28.6139, 77.2090);               // ✅ ABSENT (Delhi - far away)
```

### 3. Success Response
```javascript
{
  "success": true,
  "message": "Attendance recorded - present", // or "absent"
  "data": {
    "record_id": "ce3e9bdb-7c08-4bd2-837c-51ac372e7d7d",
    "status": "present", // or "absent" 
    "check_in_time": "2025-08-03T18:20:29.508478",
    "distance_from_session": 15.5, // meters from session location
    "user_id": "8fa267ed-5410-462a-98f5-fb6e3b8e4656"
  }
}
```

### 4. Error Response
```javascript
{
  "success": false,
  "message": "Error description",
  "error": "Detailed error information"
}
```

---

## 🧪 TEST ACCOUNTS (Ready to Use)

```javascript
// ✅ WORKING TEST CREDENTIALS
const TEST_ACCOUNTS = {
  TEACHER: { 
    email: "alpha@gmail.com", 
    password: "P21042004p#" 
  },
  STUDENT: { 
    email: "beta@gmail.com", 
    password: "P21042004p#" 
  },
  ADMIN: { 
    email: "psaha21.un@gmail.com", 
    password: "P21042004p#" 
  }
};
```

---

## 📱 COMPLETE WORKING EXAMPLE

```javascript
class AttendanceAPI {
  constructor() {
    this.baseURL = "https://attendance-backend-go8h.onrender.com";
    this.jwtToken = null;
    this.sessionToken = null;
  }

  // 1. Login user
  async login(email, password) {
    try {
      const response = await fetch(`${this.baseURL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      const data = await response.json();
      
      if (data.success) {
        this.jwtToken = data.data.jwt_token;
        this.sessionToken = data.data.session_token;
        return { success: true, user: data.data.user };
      } else {
        return { success: false, error: data.message };
      }
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  // Mark attendance
  async markAttendance(latitude, longitude, accuracy = 10) {
    if (!this.jwtToken || !this.sessionToken) {
      return { success: false, error: "Not logged in" };
    }

    try {
      const response = await fetch(`${this.baseURL}/simple/mark-attendance`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.jwtToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          session_code: this.sessionToken,
          latitude: latitude,
          longitude: longitude,
          accuracy: accuracy
        })
      });

      return await response.json();
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  // 3. Check server health
  async checkHealth() {
    try {
      const response = await fetch(`${this.baseURL}/health`);
      return await response.json();
    } catch (error) {
      return { success: false, error: error.message };
    }
  }
}

// Usage:
const api = new AttendanceAPI();

// Login
const loginResult = await api.login("beta@gmail.com", "P21042004p#");
if (loginResult.success) {
  console.log("Logged in:", loginResult.user.name);
  
  // Mark attendance at SAHA organization location (PRESENT)
  const attendanceResult = await api.markAttendance(22.6499919, 88.3640317);
  if (attendanceResult.success) {
    console.log("Attendance marked:", attendanceResult.data.status); // "present"
  }
  
  // Test far location (ABSENT)
  const farResult = await api.markAttendance(28.6139, 77.2090);
  if (farResult.success) {
    console.log("Far attendance:", farResult.data.status); // "absent"
  }
}
```

---

## ⚠️ IMPORTANT CHANGES FROM OLD API

### ✅ What Changed:
1. **New Base URL**: `attendance-backend-go8h.onrender.com`
2. **Token Structure**: Extract `data.data.jwt_token` (not just `data.token`)
3. **Session Parameter**: Use `session_code` (from `session_token`)
4. **Endpoint**: Use `/simple/mark-attendance` (not `/attendance/mark`)
5. **Coordinate Formats**: All formats now supported (string, number, decimal)
6. **🎯 CORRECT COORDINATES**: Use SAHA organization location for testing

### ❌ Old (Broken) vs ✅ New (Working):
```javascript
// ❌ OLD (DON'T USE)
const token = response.data.token;
POST /attendance/mark

// ✅ NEW (USE THIS)
const token = response.data.data.jwt_token;
POST /simple/mark-attendance
```

### 🎯 **CORRECT TEST COORDINATES (VERIFIED WORKING):**
```javascript
// ✅ SAHA Organization Location (PRESENT status)
const WORKING_COORDINATES = {
  // Exact organization location - PRESENT
  exact: { latitude: 22.6499919, longitude: 88.3640317 },
  
  // Near organization (within 100m radius) - PRESENT  
  nearby: { latitude: 22.6500919, longitude: 88.3641317 },
  
  // Outside radius (for testing ABSENT) - ABSENT
  far: { latitude: 28.6139, longitude: 77.2090 }  // Delhi
};

// Use these for testing:
await markAttendance(jwtToken, sessionToken, 22.6499919, 88.3640317); // → PRESENT ✅
await markAttendance(jwtToken, sessionToken, 28.6139, 77.2090);       // → ABSENT ✅
```

---

## 🔧 DEBUGGING TIPS

### 1. Check Server Health First
```javascript
const health = await fetch("https://attendance-backend-go8h.onrender.com/health");
console.log(await health.json()); // Should return {"service":"attendance_backend","status":"healthy"}
```

### 2. Validate Login Response
```javascript
// Make sure you get both tokens:
console.log("JWT Token:", loginData.data.jwt_token);
console.log("Session Token:", loginData.data.session_token);
```

### 3. Check Attendance Response
```javascript
// Status 200 = Success, 401 = Auth error, 500 = Server error
console.log("Status:", response.status);
console.log("Data:", await response.json());
```

### 4. Testing with Different Locations
```javascript
// Test locations for debugging:
const TEST_LOCATIONS = {
  // Should mark as PRESENT (exact org location)
  EXACT: {lat: 22.6499919, lon: 88.3640317}, 
  
  // Should mark as PRESENT (10m away)
  NEAR_10M: {lat: 22.6500736, lon: 88.3641016}, 
  
  // Should mark as PRESENT (75m away)
  NEAR_75M: {lat: 22.6506456, lon: 88.3643876}, 
  
  // Should mark as ABSENT (150m away - outside radius)
  FAR_150M: {lat: 22.6512019, lon: 88.3647237}, 
  
  // Should mark as ABSENT (Delhi - very far)
  DELHI: {lat: 28.6139, lon: 77.2090}
};

// Check each location against the radius
for (const [name, coords] of Object.entries(TEST_LOCATIONS)) {
  console.log(`Testing ${name}...`);
  const result = await markAttendance(jwtToken, sessionToken, coords.lat, coords.lon);
  console.log(`${name}: ${result.data.status}, distance: ${result.data.distance_from_session}m`);
}
```

---

## 📞 SUPPORT

If you encounter any issues:

1. **Check server health first**: `/health` endpoint
2. **Verify login tokens**: Make sure both JWT and session tokens are extracted
3. **Test with provided credentials**: Use `beta@gmail.com` / `P21042004p#`
4. **Check coordinate format**: Any format works now (string/number/decimal)

**All backend issues are resolved. The system is production-ready!** 🚀
