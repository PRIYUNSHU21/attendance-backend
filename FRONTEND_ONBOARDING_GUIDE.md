# 🚀 FRONTEND ONBOARDING GUIDE
## Complete Guide for Organization and Admin Creation

### ✅ PROBLEM SOLVED!
The backend now provides **public endpoints** that allow frontend engineers to:
1. **List existing organizations** for user selection
2. **Create new organizations** without authentication 
3. **Register the first admin** for any organization
4. **Login with the newly created admin**

---

## 🔗 AVAILABLE PUBLIC ENDPOINTS

### 1. **GET /auth/public/organizations**
**Purpose:** List all organizations for registration/login selection
**Authentication:** ❌ None required (Public)
**Method:** GET
**URL:** `http://your-backend-url/auth/public/organizations`

**Response Example:**
```json
{
  "success": true,
  "data": [
    {
      "org_id": "b7d03462-7491-46a5-8600-f1cc16225ae7",
      "name": "Test University",
      "description": "A test university for demonstration",
      "contact_email": "admin@testuni.edu"
    }
  ],
  "message": "Organizations retrieved successfully"
}
```

**Frontend Usage:**
```javascript
// Fetch organizations for dropdown/selection
const getOrganizations = async () => {
  const response = await fetch('/auth/public/organizations');
  const data = await response.json();
  return data.data; // Array of organizations
};
```

---

### 2. **POST /auth/public/organizations**
**Purpose:** Create a new organization (for new institutions/companies)
**Authentication:** ❌ None required (Public)
**Method:** POST
**URL:** `http://your-backend-url/auth/public/organizations`

**Request Body:**
```json
{
  "name": "My University",
  "description": "A great educational institution",
  "contact_email": "admin@myuni.edu"
}
```

**Response Example:**
```json
{
  "success": true,
  "data": {
    "org_id": "new-org-id-uuid",
    "name": "My University",
    "description": "A great educational institution", 
    "contact_email": "admin@myuni.edu"
  },
  "message": "Organization created successfully"
}
```

**Frontend Usage:**
```javascript
// Create new organization
const createOrganization = async (orgData) => {
  const response = await fetch('/auth/public/organizations', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(orgData)
  });
  const data = await response.json();
  return data.data; // New organization object
};
```

---

### 3. **POST /auth/public/admin**
**Purpose:** Create the first admin user for an organization
**Authentication:** ❌ None required (Public)
**Method:** POST
**URL:** `http://your-backend-url/auth/public/admin`

**Request Body:**
```json
{
  "name": "John Admin",
  "email": "john.admin@myuni.edu", 
  "password": "SecurePassword123!",
  "org_id": "organization-uuid-here"
}
```

**Response Example:**
```json
{
  "success": true,
  "data": {
    "user_id": "user-uuid",
    "name": "John Admin",
    "email": "john.admin@myuni.edu",
    "role": "admin", 
    "org_id": "organization-uuid-here",
    "is_active": true,
    "created_at": "2025-07-09T07:22:41.424588"
  },
  "message": "Admin user created successfully"
}
```

**Important Notes:**
- ⚠️ **Only works if the organization has NO existing admin**
- ✅ Automatically sets role to 'admin'
- ✅ Validates email format and password strength
- ❌ Will fail with 400 error if admin already exists

**Frontend Usage:**
```javascript
// Create first admin for organization
const createAdmin = async (adminData) => {
  const response = await fetch('/auth/public/admin', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(adminData)
  });
  const data = await response.json();
  
  if (!response.ok) {
    throw new Error(data.message);
  }
  
  return data.data; // New admin user object
};
```

---

## 🎯 COMPLETE ONBOARDING FLOW

### **Scenario A: Join Existing Organization**
```javascript
// 1. Get list of organizations
const orgs = await getOrganizations();

// 2. User selects organization from dropdown
const selectedOrg = orgs.find(org => org.org_id === userSelection);

// 3. If no admin exists, allow admin creation
try {
  const newAdmin = await createAdmin({
    name: "Admin Name",
    email: "admin@org.com", 
    password: "password123",
    org_id: selectedOrg.org_id
  });
  
  // 4. Login with new admin credentials
  const loginResponse = await login({
    email: "admin@org.com",
    password: "password123"
  });
  
} catch (error) {
  // Admin already exists - direct to regular login
  console.log("Admin exists, redirect to login");
}
```

### **Scenario B: Create New Organization + Admin**
```javascript
// 1. Create new organization
const newOrg = await createOrganization({
  name: "New University",
  description: "A new educational institution",
  contact_email: "contact@newuni.edu"
});

// 2. Create first admin for the new organization
const admin = await createAdmin({
  name: "First Admin",
  email: "admin@newuni.edu",
  password: "AdminPassword123!",
  org_id: newOrg.org_id
});

// 3. Auto-login the new admin
const loginResponse = await login({
  email: "admin@newuni.edu", 
  password: "AdminPassword123!"
});
```

---

## 🔒 AUTHENTICATION FLOW

After creating an admin, use the regular login endpoint:

**POST /auth/login**
```json
{
  "email": "admin@myuni.edu",
  "password": "AdminPassword123!",
  "device_info": "Mozilla/5.0..." // Optional
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "user_id": "uuid",
      "name": "John Admin", 
      "email": "admin@myuni.edu",
      "role": "admin",
      "org_id": "org-uuid"
    },
    "token": "jwt-token-here",
    "session": {
      "session_id": "session-uuid",
      "expires_at": "2025-07-16T07:22:41.424588"
    }
  },
  "message": "Login successful"
}
```

---

## ❌ ERROR HANDLING

### Common Error Responses:

**400 - Validation Error:**
```json
{
  "success": false,
  "message": "Email is required",
  "error": "validation_error"
}
```

**400 - Admin Already Exists:**
```json
{
  "success": false, 
  "message": "Organization already has an admin. Use regular registration.",
  "error": "admin_exists"
}
```

**404 - Organization Not Found:**
```json
{
  "success": false,
  "message": "Organization not found", 
  "error": "not_found"
}
```

---

## 🧪 TESTING

Test script available at: `test_public_endpoints.py`
```bash
python test_public_endpoints.py
```

All endpoints have been tested and verified working! ✅

---

## 🎉 SUMMARY

**✅ Frontend engineers can now:**
1. List existing organizations
2. Create new organizations  
3. Create the first admin for any organization
4. Login with newly created admins
5. Handle all error cases appropriately

**🔗 Base URL:** `http://127.0.0.1:5000` (development)
**📱 All endpoints support CORS** for frontend integration

The backend is **100% ready** for frontend onboarding! 🚀
