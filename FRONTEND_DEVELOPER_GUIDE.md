# 📁 FILE STRUCTURE GUIDE FOR FRONTEND DEVELOPERS

## 🎯 Overview
This guide explains every file in the attendance backend system and how frontend developers can work with them.

## 🌐 **PRODUCTION DEPLOYMENT STATUS**

### ✅ **LIVE & RUNNING**
- **Production URL**: https://your-app.onrender.com
- **Database**: PostgreSQL (managed by Render)
- **Status**: Deployed and operational
- **SSL/HTTPS**: Automatically configured
- **Auto-deployment**: Connected to GitHub

### 🔗 **API Base URLs**
```javascript
// Use these in your frontend:
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://your-app.onrender.com'
  : 'http://127.0.0.1:5000';

// Examples:
// Health: GET ${API_BASE_URL}/health
// Login: POST ${API_BASE_URL}/auth/login
// Check-in: POST ${API_BASE_URL}/attendance/check-in
```

### 📱 **Flutter Integration**
```dart
// In your Flutter app:
class ApiService {
  static const String baseUrl = 'https://your-app.onrender.com';
  
  // Health check
  static String get healthUrl => '$baseUrl/health';
  
  // Authentication
  static String get loginUrl => '$baseUrl/auth/login';
  static String get registerUrl => '$baseUrl/auth/register';
  
  // Attendance
  static String get checkInUrl => '$baseUrl/attendance/check-in';
}
```

---

## 📱 **ROOT LEVEL FILES**

### 🚀 `app.py` - MAIN APPLICATION ENTRY POINT
**What it does:** Creates and configures the Flask web server
**For frontend:** This is what serves your API endpoints
**Key info:** 
- Production: Live on Render with PostgreSQL database
- Development: Runs on http://127.0.0.1:5000 locally
- Registers all API routes (/auth, /attendance, /admin, /reports)
- Enables CORS for frontend communication
- **Production URL:** https://your-app.onrender.com
- **Development:** `python app.py`

### 🏃 `run.py` - ALTERNATIVE STARTUP SCRIPT
**What it does:** Alternative way to start the application
**For frontend:** Same as app.py, just different entry point
**Usage:** `python run.py`

### 🧪 `test_app.py` - API TESTING EXAMPLES
**What it does:** Tests API endpoints with real examples
**For frontend:** **PERFECT REFERENCE** for API usage patterns
**Key info:**
- Shows exact request/response formats
- Demonstrates error handling
- Provides working code examples
- **Run with:** `python test_app.py`

### 🚀 `init_db.py` - DATABASE SETUP WITH SAMPLE DATA
**What it does:** Creates database and sample data for testing
**For frontend:** Provides test users and sessions to work with
**Key info:**
- Creates sample organizations, users, sessions
- **Run once:** `python init_db.py`
- Gives you test credentials to use immediately

### 📦 `requirements.txt` - PYTHON DEPENDENCIES
**What it does:** Lists all required Python packages
**For frontend:** Install these on backend server
**Usage:** `pip install -r requirements.txt`

### 🔐 `.env` - ENVIRONMENT CONFIGURATION
**What it does:** Contains secrets and configuration
**For frontend:** Important for CORS and server settings
**Key settings:**
- `CORS_ORIGINS`: Which domains can access the API
- `SECRET_KEY`: Server security (never share)
- `DATABASE_URL`: Where data is stored

---

## ⚙️ **CONFIG FOLDER** - Server Configuration

### 🔧 `config/settings.py` - ALL APPLICATION SETTINGS
**What it does:** Central configuration for entire system
**For frontend:** 
- JWT token expiry times affect your auth flow
- CORS settings determine which domains can call API
- Geofence radius affects location-based features

### 🗄️ `config/db.py` - DATABASE CONNECTION
**What it does:** Manages database connection and table creation
**For frontend:** Handles data persistence behind API calls
**Auto-creates:** All necessary database tables on startup

### 📋 `config/schema.sql` - DATABASE STRUCTURE REFERENCE
**What it does:** Shows database table definitions
**For frontend:** Understand what data fields are available in API responses

---

## 📊 **MODELS FOLDER** - Data Structures

### 📦 `models/__init__.py` - MODEL ORGANIZATION
**What it does:** Organizes all data models
**For frontend:** Shows what data structures are available via API

### 👤 `models/user.py` - USER DATA STRUCTURE
**What it does:** Defines user accounts and authentication
**For frontend:** 
- User registration/login API data formats
- User profile information structure
- Role-based permissions (student/teacher/admin)
**Key functions:** create_user(), find_user_by_email(), update_user()

### 🏢 `models/organisation.py` - ORGANIZATION DATA
**What it does:** Multi-tenant organization management
**For frontend:**
- Organization selection in UI
- Data separation between organizations
- Organization settings and info

### 📅 `models/session.py` - LOGIN SESSION TRACKING
**What it does:** Manages user login sessions
**For frontend:** Authentication state management
**Key info:** Sessions expire based on configured time

### 📋 `models/attendance.py` - ATTENDANCE DATA
**What it does:** Attendance sessions and records
**For frontend:**
- Check-in/check-out data structures
- Attendance session information
- Location and timing data
**Key functions:** mark_attendance(), get_session_attendance()

---

## 🛠️ **SERVICES FOLDER** - Business Logic

### 🔐 `services/auth_services.py` - AUTHENTICATION LOGIC
**What it does:** Handles login, registration, logout
**For frontend:** Powers all authentication features
**Key functions:**
- `login_user()`: Verify credentials, return JWT token
- `register_user()`: Create new accounts
- `logout_user()`: End sessions safely

### ✅ `services/attendance_service.py` - ATTENDANCE LOGIC
**What it does:** Check-in/check-out business logic
**For frontend:** Core attendance functionality
**Key features:**
- Location-based verification (geofencing)
- Attendance status calculation (present/late/absent)
- Session management and reporting

### 👑 `services/admin_service.py` - ADMIN OPERATIONS
**What it does:** Administrative functions like user management
**For frontend:** Admin dashboard features
**Key functions:**
- Bulk user creation
- Organization statistics
- System maintenance operations

### 📍 `services/geo_service.py` - LOCATION SERVICES
**What it does:** GPS and location calculations
**For frontend:** Location-based attendance verification
**Key functions:**
- Distance calculations between GPS coordinates
- Geofence validation (is user close enough?)

### 🔒 `services/hash_service.py` - PASSWORD SECURITY
**What it does:** Secure password hashing
**For frontend:** Password security (behind the scenes)
**Security:** Passwords never stored as plain text

---

## 🔧 **UTILS FOLDER** - Helper Functions

### 🎫 `utils/auth.py` - JWT TOKEN MANAGEMENT
**What it does:** JWT token creation and validation
**For frontend:** **CRITICAL** for authentication
**Key features:**
- Token generation after login
- Token validation for protected routes
- Role-based access decorators
- `@token_required`, `@admin_required` decorators

### 📨 `utils/response.py` - API RESPONSE FORMATTING
**What it does:** Standardizes all API responses
**For frontend:** **ESSENTIAL** - all API responses use these formats
**Standard formats:**
```json
// Success
{"success": true, "data": {...}, "message": "Success"}

// Error  
{"success": false, "message": "Error description"}

// Validation errors
{"success": false, "errors": [...field errors...]}
```

### ✔️ `utils/validators.py` - INPUT VALIDATION
**What it does:** Validates data before processing
**For frontend:** Helps you understand required fields and formats
**Validates:** User data, attendance data, session data

---

## 🛣️ **ROUTES FOLDER** - API Endpoints

### 🔑 `routes/auth.py` - AUTHENTICATION ENDPOINTS
**What it does:** Login, registration, logout APIs
**For frontend:** **START HERE** for user authentication
**Endpoints:**
- `POST /auth/login` - User login
- `POST /auth/register` - User registration  
- `POST /auth/logout` - User logout
- `GET /auth/profile` - Get user profile
- `POST /auth/change-password` - Change password

### ✅ `routes/attendance_mark.py` - ATTENDANCE ENDPOINTS
**What it does:** Check-in, check-out, attendance tracking
**For frontend:** Core attendance features
**Endpoints:**
- `POST /attendance/check-in` - Mark attendance
- `POST /attendance/check-out` - Complete attendance
- `GET /attendance/my-history` - User attendance history
- `GET /attendance/active-sessions` - Available sessions

### 👑 `routes/admin.py` - ADMIN MANAGEMENT ENDPOINTS
**What it does:** User management, organization settings
**For frontend:** Admin dashboard functionality
**Endpoints:**
- `GET /admin/users` - List users
- `POST /admin/users` - Create users
- `POST /admin/sessions` - Create attendance sessions
- `GET /admin/dashboard/stats` - Dashboard statistics

### 📊 `routes/reports.py` - REPORTING ENDPOINTS
**What it does:** Analytics, reports, data export
**For frontend:** Reporting and analytics features
**Endpoints:**
- `GET /reports/session/<id>/detailed` - Session reports
- `GET /reports/organization/summary` - Organization analytics
- `GET /reports/export/csv` - Data export

---

## 📁 **INSTANCE FOLDER** - Runtime Data

### 🗄️ `instance/attendance.db` - SQLITE DATABASE FILE
**What it does:** Stores all application data
**For frontend:** Contains all your data (users, attendance, etc.)
**Note:** Auto-created when app starts

---

## 🚀 **QUICK START FOR FRONTEND DEVELOPERS**

### 1. **First Time Setup:**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Set up database with sample data
python init_db.py

# Start the server
python app.py
```

### 2. **Test the API:**
```bash
# Verify everything works
python test_app.py
```

### 3. **Key Files to Understand:**
1. **`test_app.py`** - See working API examples
2. **`routes/auth.py`** - Authentication endpoints
3. **`routes/attendance_mark.py`** - Core attendance features
4. **`utils/response.py`** - API response formats
5. **`init_db.py`** - Sample data for testing

### 4. **Sample API Calls:**
```javascript
// Health check
GET http://127.0.0.1:5000/health

// Login
POST http://127.0.0.1:5000/auth/login
{"email": "student@techuniversity.edu", "password": "student123"}

// Check in (requires token)
POST http://127.0.0.1:5000/attendance/check-in
Authorization: Bearer <token>
{"session_id": "session-uuid", "lat": 40.7128, "lon": -74.0060}
```

---

## 🎯 **FRONTEND INTEGRATION PRIORITY**

### **PRIORITY 1 - Essential:**
- `routes/auth.py` - User authentication
- `routes/attendance_mark.py` - Core attendance
- `utils/response.py` - API response handling
- `test_app.py` - Working examples

### **PRIORITY 2 - Important:**
- `routes/admin.py` - Admin features
- `models/user.py` - User data structure
- `utils/auth.py` - JWT token management

### **PRIORITY 3 - Advanced:**
- `routes/reports.py` - Analytics and reporting
- `services/attendance_service.py` - Business logic
- `config/settings.py` - Configuration options

---

**💡 Pro Tip:** Start with `test_app.py` to see working examples, then implement similar patterns in your frontend framework (React, Vue, Angular, etc.).
