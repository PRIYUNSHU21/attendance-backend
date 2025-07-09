# 🧪 STEP-BY-STEP TESTING GUIDE

## 🎯 **COMPLETE TESTING CHECKLIST**

This guide walks you through testing every aspect of the attendance backend system, from basic health checks to complete user flows.

---

## 📋 **TESTING PHASES**

### **Phase 1: Basic Health & Setup** ⚡
### **Phase 2: Public Endpoints (No Auth)** 🔓  
### **Phase 3: Authentication Flow** 🔐
### **Phase 4: Protected Endpoints** 🛡️
### **Phase 5: Admin Functions** 👑
### **Phase 6: Complete User Journey** 🚀

---

## ⚡ **PHASE 1: BASIC HEALTH & SETUP**

### **Step 1.1: Test Backend Health**
```bash
# Test local backend
curl http://127.0.0.1:5000/health

# Test production backend  
curl https://attendance-backend-go8h.onrender.com/health
```

**Expected Response:**
```json
{
  "data": {
    "service": "attendance_backend",
    "status": "healthy"
  },
  "message": "Service is running",
  "success": true
}
```

### **Step 1.2: Start Local Backend (if testing locally)**
```bash
cd "C:\Users\Priyunshu Saha\OneDrive\Desktop\ATTENDANCE_BACKEND"
python app.py
```

**Expected Output:**
```
Database tables created successfully!
* Running on http://127.0.0.1:5000
```

### **Step 1.3: Run Built-in Test Suite**
```bash
# Run comprehensive backend tests
python test_app.py
```

**Expected: All tests should pass** ✅

---

## 🔓 **PHASE 2: PUBLIC ENDPOINTS (NO AUTH REQUIRED)**

### **Step 2.1: List Organizations**
```bash
# Production
curl https://attendance-backend-go8h.onrender.com/auth/public/organizations

# Local  
curl http://127.0.0.1:5000/auth/public/organizations
```

**Expected Response:**
```json
{
  "success": true,
  "data": [
    {
      "org_id": "uuid-here",
      "name": "Test University", 
      "description": "A test university",
      "contact_email": "admin@testuni.edu"
    }
  ],
  "message": "Organizations retrieved successfully"
}
```

### **Step 2.2: Create New Organization**
```bash
# Production
curl -X POST https://attendance-backend-go8h.onrender.com/auth/public/organizations \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Test University",
    "description": "Testing organization creation",
    "contact_email": "admin@mytestuni.edu"
  }'

# Local
curl -X POST http://127.0.0.1:5000/auth/public/organizations \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Test University", 
    "description": "Testing organization creation",
    "contact_email": "admin@mytestuni.edu"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "org_id": "new-org-uuid-here",
    "name": "My Test University",
    "description": "Testing organization creation", 
    "contact_email": "admin@mytestuni.edu"
  },
  "message": "Organization created successfully"
}
```

**📝 SAVE THE ORG_ID** - You'll need it for the next step!

### **Step 2.3: Create First Admin**
```bash
# Replace "new-org-uuid-here" with the org_id from step 2.2
curl -X POST https://attendance-backend-go8h.onrender.com/auth/public/admin \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Admin",
    "email": "testadmin@mytestuni.edu",
    "password": "AdminPass123!",
    "org_id": "new-org-uuid-here"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "user_id": "admin-uuid",
    "name": "Test Admin",
    "email": "testadmin@mytestuni.edu", 
    "role": "admin",
    "org_id": "new-org-uuid-here",
    "is_active": true
  },
  "message": "Admin user created successfully"
}
```

**📝 SAVE THE ADMIN CREDENTIALS** - You'll need them for authentication!

---

## 🔐 **PHASE 3: AUTHENTICATION FLOW**

### **Step 3.1: Login with New Admin**
```bash
curl -X POST https://attendance-backend-go8h.onrender.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testadmin@mytestuni.edu",
    "password": "AdminPass123!"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "user_id": "admin-uuid",
      "name": "Test Admin",
      "email": "testadmin@mytestuni.edu",
      "role": "admin",
      "org_id": "org-uuid"
    },
    "token": "jwt-token-very-long-string-here",
    "session": {
      "session_id": "session-uuid",
      "expires_at": "2025-07-16T..."
    }
  },
  "message": "Login successful"
}
```

**📝 SAVE THE JWT TOKEN** - You'll need it for all protected endpoints!

### **Step 3.2: Verify Token Works**
```bash
# Replace "jwt-token-here" with the actual token from step 3.1
curl https://attendance-backend-go8h.onrender.com/auth/verify \
  -H "Authorization: Bearer jwt-token-here"
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "user_id": "admin-uuid",
      "role": "admin",
      "org_id": "org-uuid"
    }
  },
  "message": "Token is valid"
}
```

---

## 🛡️ **PHASE 4: PROTECTED ENDPOINTS**

### **Step 4.1: Get User Profile**
```bash
curl https://attendance-backend-go8h.onrender.com/auth/profile \
  -H "Authorization: Bearer jwt-token-here"
```

**Expected: User profile data** ✅

### **Step 4.2: Register Regular User**
```bash
curl -X POST https://attendance-backend-go8h.onrender.com/auth/register \
  -H "Authorization: Bearer jwt-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Student",
    "email": "student@mytestuni.edu", 
    "password": "StudentPass123!",
    "org_id": "your-org-uuid-here"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "user_id": "student-uuid",
    "name": "Test Student",
    "role": "student",
    "org_id": "org-uuid"
  },
  "message": "User registered successfully"
}
```

### **Step 4.3: Test Student Login**
```bash
curl -X POST https://attendance-backend-go8h.onrender.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@mytestuni.edu",
    "password": "StudentPass123!"
  }'
```

**Expected: Student JWT token** ✅

---

## 👑 **PHASE 5: ADMIN FUNCTIONS**

### **Step 5.1: List All Users (Admin Only)**
```bash
curl https://attendance-backend-go8h.onrender.com/admin/users \
  -H "Authorization: Bearer admin-jwt-token-here"
```

**Expected Response:**
```json
{
  "success": true,
  "data": [
    {
      "user_id": "admin-uuid",
      "name": "Test Admin",
      "role": "admin"
    },
    {
      "user_id": "student-uuid", 
      "name": "Test Student",
      "role": "student"
    }
  ]
}
```

### **Step 5.2: Create Attendance Session**
```bash
curl -X POST https://attendance-backend-go8h.onrender.com/admin/sessions \
  -H "Authorization: Bearer admin-jwt-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Class Session",
    "description": "Testing attendance functionality",
    "start_time": "2025-07-09T14:00:00",
    "end_time": "2025-07-09T15:00:00",
    "location_lat": 40.7128,
    "location_lon": -74.0060,
    "location_name": "Test Classroom",
    "geofence_radius": 100
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "session_id": "session-uuid",
    "title": "Test Class Session",
    "start_time": "2025-07-09T14:00:00",
    "end_time": "2025-07-09T15:00:00"
  },
  "message": "Session created successfully"
}
```

**📝 SAVE THE SESSION_ID** - You'll need it for attendance testing!

---

## 🚀 **PHASE 6: COMPLETE USER JOURNEY**

### **Step 6.1: Student Check-in**
```bash
# Use student JWT token from step 4.3
curl -X POST https://attendance-backend-go8h.onrender.com/attendance/check-in \
  -H "Authorization: Bearer student-jwt-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-uuid-from-step-5.2",
    "lat": 40.7128,
    "lon": -74.0060
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "record_id": "attendance-record-uuid",
    "status": "present",
    "check_in_time": "2025-07-09T14:05:00"
  },
  "message": "Attendance marked successfully"
}
```

### **Step 6.2: View Attendance History**
```bash
curl https://attendance-backend-go8h.onrender.com/attendance/my-history \
  -H "Authorization: Bearer student-jwt-token-here"
```

**Expected: List of attendance records** ✅

### **Step 6.3: Admin View Session Report**
```bash
curl https://attendance-backend-go8h.onrender.com/reports/session/session-uuid-here/detailed \
  -H "Authorization: Bearer admin-jwt-token-here"
```

**Expected: Detailed attendance report** ✅

---

## 🛠️ **AUTOMATED TESTING SCRIPTS**

### **Quick Test All Public Endpoints**
```bash
python test_public_endpoints.py
```

### **Test Live Production Server**
```bash
python test_live_render.py
```

### **Complete Backend Test Suite**
```bash
python test_app.py
```

---

## ✅ **SUCCESS CRITERIA CHECKLIST**

### **Basic Infrastructure:**
- [ ] Health endpoint returns 200 status
- [ ] Database connection works
- [ ] All required tables exist

### **Public Endpoints:**
- [ ] Can list organizations (GET /auth/public/organizations)
- [ ] Can create organization (POST /auth/public/organizations)  
- [ ] Can create first admin (POST /auth/public/admin)
- [ ] Cannot create duplicate admin

### **Authentication:**
- [ ] Admin login works and returns JWT token
- [ ] JWT token includes org_id and role
- [ ] Token validation works
- [ ] Student registration and login works

### **Authorization & Security:**
- [ ] Admin can access admin endpoints
- [ ] Students cannot access admin endpoints
- [ ] Users only see data from their organization
- [ ] Cross-organization data leakage prevented

### **Core Functionality:**
- [ ] Admin can create attendance sessions
- [ ] Students can check-in to sessions
- [ ] Location/geofence validation works
- [ ] Attendance reports generate correctly

### **Error Handling:**
- [ ] Invalid credentials return 401
- [ ] Missing authorization returns 401  
- [ ] Invalid data returns 400 with validation errors
- [ ] Non-existent resources return 404

---

## 🐛 **TROUBLESHOOTING**

### **Common Issues:**

**❌ "Connection refused"**
```bash
# Check if backend is running
curl http://127.0.0.1:5000/health
# If fails, start backend: python app.py
```

**❌ "401 Unauthorized"**
```bash
# Check JWT token format
curl https://attendance-backend-go8h.onrender.com/auth/verify \
  -H "Authorization: Bearer your-token-here"
```

**❌ "404 Not Found"**
```bash
# Check endpoint URL spelling
# Verify route is registered in app.py
```

**❌ "400 Bad Request"**
```bash
# Check JSON format and required fields
# Review API documentation for expected data
```

---

## 📱 **FRONTEND TESTING EXAMPLES**

### **JavaScript/React Testing:**
```javascript
// Test organization creation
const createOrg = async () => {
  const response = await fetch('https://attendance-backend-go8h.onrender.com/auth/public/organizations', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: 'Test University',
      description: 'Testing from React',
      contact_email: 'admin@test.edu'
    })
  });
  
  const data = await response.json();
  console.log('Organization created:', data);
  return data;
};

// Test admin creation  
const createAdmin = async (orgId) => {
  const response = await fetch('https://attendance-backend-go8h.onrender.com/auth/public/admin', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: 'Test Admin',
      email: 'admin@test.edu',
      password: 'AdminPass123!',
      org_id: orgId
    })
  });
  
  const data = await response.json();
  console.log('Admin created:', data);
  return data;
};

// Test login
const login = async () => {
  const response = await fetch('https://attendance-backend-go8h.onrender.com/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: 'admin@test.edu',
      password: 'AdminPass123!'
    })
  });
  
  const data = await response.json();
  console.log('Login result:', data);
  return data.data.token;
};

// Run complete test
(async () => {
  try {
    const org = await createOrg();
    const admin = await createAdmin(org.data.org_id);
    const token = await login();
    console.log('✅ Complete onboarding flow successful!');
    console.log('JWT Token:', token);
  } catch (error) {
    console.error('❌ Test failed:', error);
  }
})();
```

### **Flutter/Dart Testing:**
```dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiTester {
  static const String baseUrl = 'https://attendance-backend-go8h.onrender.com';
  
  // Test organization creation
  static Future<Map<String, dynamic>> createOrganization() async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/public/organizations'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'name': 'Flutter Test University',
        'description': 'Testing from Flutter app',
        'contact_email': 'admin@fluttertest.edu'
      }),
    );
    
    print('Create Org Status: ${response.statusCode}');
    final data = jsonDecode(response.body);
    print('Create Org Response: $data');
    return data;
  }
  
  // Test admin creation
  static Future<Map<String, dynamic>> createAdmin(String orgId) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/public/admin'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'name': 'Flutter Admin',
        'email': 'admin@fluttertest.edu',
        'password': 'FlutterPass123!',
        'org_id': orgId
      }),
    );
    
    print('Create Admin Status: ${response.statusCode}');
    final data = jsonDecode(response.body);
    print('Create Admin Response: $data');
    return data;
  }
  
  // Test login
  static Future<String?> login() async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'email': 'admin@fluttertest.edu',
        'password': 'FlutterPass123!'
      }),
    );
    
    print('Login Status: ${response.statusCode}');
    final data = jsonDecode(response.body);
    print('Login Response: $data');
    
    if (data['success']) {
      return data['data']['token'];
    }
    return null;
  }
  
  // Run complete test
  static Future<void> runCompleteTest() async {
    try {
      print('🧪 Starting Flutter API test...');
      
      final org = await createOrganization();
      final orgId = org['data']['org_id'];
      
      final admin = await createAdmin(orgId);
      final token = await login();
      
      if (token != null) {
        print('✅ Complete Flutter onboarding flow successful!');
        print('JWT Token: $token');
      } else {
        print('❌ Login failed');
      }
    } catch (error) {
      print('❌ Test failed: $error');
    }
  }
}

// Usage in Flutter app:
void main() async {
  await ApiTester.runCompleteTest();
}
```

---

## 🎉 **FINAL VERIFICATION**

### **Expected Results Summary:**
- ✅ All curl commands return success responses
- ✅ Organization creation and admin registration work
- ✅ JWT authentication functions properly
- ✅ Organization isolation prevents data leakage
- ✅ Both admin and student flows complete successfully
- ✅ Frontend can integrate using provided examples

### **If All Tests Pass:**
🎉 **Congratulations! Your attendance backend is fully functional and ready for production use.**

### **If Tests Fail:**
1. Check the specific error messages
2. Verify JSON format and required fields
3. Ensure JWT tokens are properly formatted
4. Review the troubleshooting section
5. Run automated test scripts for detailed diagnostics

---

**💡 Pro Tip:** Run this testing sequence every time you make changes to ensure everything still works correctly!
