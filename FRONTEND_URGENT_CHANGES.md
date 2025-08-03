# 🚨 FRONTEND URGENT CHANGES - QUICK REFERENCE

## 🔥 **IMMEDIATE ACTION REQUIRED**

### 1. **UPDATE API BASE URL**
```javascript
// CHANGE THIS EVERYWHERE IN YOUR CODE
const API_BASE_URL = "https://attendance-backend-go8h.onrender.com"
```

### 2. **FIX LOGIN CODE** 
```javascript
// OLD (BROKEN)
const token = response.data.token;

// NEW (WORKING)
const token = response.data.data.jwt_token;
```

### 3. **FIX SESSION CREATION**
```javascript
// OLD ENDPOINT (404 ERROR)
POST /api/admin/create-session

// NEW ENDPOINT (WORKING)
POST /admin/sessions
```

### 4. **UPDATE ALL API CALLS**
```javascript
// ALL responses now have this format:
{
  "success": true,
  "message": "Success message", 
  "data": { /* actual data here */ }
}

// Extract data like this:
const result = await response.json();
const actualData = result.data; // ← Always use .data
```

---

## 🧪 **TEST WITH THESE CREDENTIALS**

```javascript
// WORKING TEST ACCOUNTS
TEACHER: { email: "alpha@gmail.com", password: "P21042004p#" }
STUDENT: { email: "beta@gmail.com", password: "P21042004p#" }
ADMIN: { email: "psaha21.un@gmail.com", password: "P21042004p#" }
```

---

## ✅ **VERIFICATION CHECKLIST**

- [ ] Updated API base URL to `attendance-backend-go8h.onrender.com`
- [ ] Fixed login to extract `data.data.jwt_token`
- [ ] Updated session creation to use `/admin/sessions`
- [ ] Updated all API responses to use `.data` property
- [ ] Tested login with teacher credentials
- [ ] Tested session creation
- [ ] Tested attendance marking

---

**Priority Level: 🔥 CRITICAL - Backend is live, frontend needs these changes to work!**
