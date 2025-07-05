# Tests Directory

This directory contains all testing, debugging, and database initialization utilities for the Attendance Backend System.

## 📁 Directory Structure

```
tests/
├── __init__.py          # Tests package initialization with documentation
├── test_app.py          # Unit tests for Flask application components
├── test_complete.py     # Comprehensive API integration tests (100% success rate)
├── init_db.py           # Database initialization and sample data creation
└── check_all_data.py    # Database content verification and inspection utility
```

## 🧪 Test Files

### 🎯 Primary Test Suite
- **`test_complete.py`** - The main testing script with 100% success rate
  - Tests all working endpoints with proper validation
  - Comprehensive API integration testing
  - **Run with:** `python tests/test_complete.py`

### 🔧 Unit Tests
- **`test_app.py`** - Unit tests for individual Flask components
  - Tests core functionality and error handling
  - Provides API usage examples for frontend developers
  - **Run with:** `python tests/test_app.py`

## 🗄️ Database Utilities

### 🚀 Database Initialization
- **`init_db.py`** - Complete database setup and sample data creation
  - Creates sample organizations, users, and attendance sessions
  - Provides test credentials for immediate development
  - **Run with:** `python tests/init_db.py`
  - **Sample Credentials:**
    - Admin: `admin@testuni.edu` / `admin123`
    - Teacher: `teacher@testuni.edu` / `teacher123`
    - Student: `student@testuni.edu` / `student123`

### 🔍 Database Inspection
- **`check_all_data.py`** - Database content verification and debugging
  - Displays all organizations, users, sessions, and attendance records
  - Useful for debugging and understanding data structure
  - **Run with:** `python tests/check_all_data.py`

## 📋 Usage Instructions

### Quick Start Testing
```bash
# 1. Initialize database with sample data
python tests/init_db.py

# 2. Start the Flask server (in another terminal)
python app.py

# 3. Run the comprehensive test suite
python tests/test_complete.py

# 4. Check database contents (optional)
python tests/check_all_data.py
```

### Development Workflow
1. **Database Setup**: Run `init_db.py` to create fresh test data
2. **Server Start**: Launch the Flask application
3. **Testing**: Use `test_complete.py` for full API validation
4. **Debugging**: Use `check_all_data.py` to inspect database state
5. **Development**: Use `test_app.py` for unit testing during development

## 📱 Frontend Development Benefits

The test files provide:
- **Working API Examples**: Real request/response formats
- **Sample Data**: Pre-configured test users and sessions
- **Error Handling Examples**: Proper error response formats
- **Authentication Patterns**: JWT token usage examples
- **Data Validation**: Input validation requirements

## ⚠️ Important Notes

- **Run from Project Root**: All test scripts should be executed from the main project directory
- **Server Required**: Most tests require the Flask server to be running on `http://127.0.0.1:5000`
- **Fresh Database**: Use `init_db.py` to reset database with clean test data
- **Test Environment**: These scripts are designed for development/testing environments only

## 🔧 Path Handling

All test files include proper Python path handling to import project modules correctly when run from the project root directory. This ensures that imports work correctly regardless of the current working directory.
