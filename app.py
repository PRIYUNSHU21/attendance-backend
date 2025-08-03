"""
📱 MAIN FLASK APPLICATION - app.py

🎯 WHAT THIS FILE DOES:
This is the MAIN entry point of the entire attendance backend system.
Think of it as the "control center" that brings everything together.

🔧 FOR FRONTEND DEVELOPERS:
- This file creates the web server that your frontend will talk to
- It sets up CORS so your React/Vue/Angular/Flutter app can make API calls
- All API endpoints are registered here through "blueprints"
- Production: Deployed on Render with PostgreSQL
- Development: Runs on http://127.0.0.1:5000 locally

📋 WHAT HAPPENS HERE:
1. Creates the Flask web application
2. Enables CORS for frontend communication
3. Sets up the database connection (PostgreSQL in production, SQLite in development)
4. Registers all API routes (auth, attendance, admin, reports)
5. Provides a health check endpoint
6. Handles basic attendance endpoints for backward compatibility

🌐 API STRUCTURE FOR FRONTEND:
- Authentication: /auth/* (login, register, logout)
- Attendance: /attendance/* (check-in, check-out, history)
- Admin: /admin/* (user management, organization settings)
- Reports: /reports/* (analytics, data export)
- Health: /health (check if server is running)

⚡ QUICK START FOR FRONTEND:
Production:
1. Check health: GET https://your-app.onrender.com/health
2. Login user: POST https://your-app.onrender.com/auth/login
3. Use the JWT token for authenticated requests

Development:
1. Make sure this server is running (python app.py)
2. Check health: GET http://127.0.0.1:5000/health
3. Login user: POST http://127.0.0.1:5000/auth/login
4. Use the JWT token for authenticated requests

🔒 SECURITY NOTES:
- All sensitive endpoints require JWT authentication
- CORS is configured to allow your frontend domain
- Passwords are never returned in API responses
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db
from models.attendance import mark_attendance, get_session_attendance
from models.organisation import find_organisation_by_id
from models.session import validate_session
from config.db import init_db
from config.settings import config
from utils.response import success_response, error_response
from utils.validators import validate_attendance_data
import os

# Import route blueprints
from routes.auth import auth_bp
from routes.attendance_mark import attendance_bp
from routes.admin import admin_bp
from routes.reports import reports_bp
from routes.migration import migration_bp
from routes.simple_attendance import simple_attendance_bp
from utils.response import success_response, error_response
from utils.validators import validate_attendance_data
import os

def create_app(config_name=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Enable CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])

    # Initialize database
    init_db(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(attendance_bp, url_prefix='/attendance')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(migration_bp, url_prefix='/migration')
    app.register_blueprint(simple_attendance_bp, url_prefix='/simple')  # Friend's system approach

    # Health check endpoint
    @app.route('/', methods=['GET'])
    @app.route('/health', methods=['GET'])
    def health_check():
        """Simple health check endpoint."""
        return success_response(
            data={"status": "healthy", "service": "attendance_backend"},
            message="Service is running"
        )

    # Basic attendance endpoint
    @app.route('/check-in', methods=['POST'])
    def check_in():
        try:
            data = request.json
            
            # Validate input data
            validation = validate_attendance_data(data)
            if not validation['is_valid']:
                return error_response(
                    message="Invalid input data",
                    status_code=422,
                    details=validation['errors']
                )
            
            student_id = data.get('student_id') or data.get('user_id')
            session_id = data.get('session_id')
            lat = data.get('lat')
            lon = data.get('lon')

            if not student_id:
                return error_response(
                    message="Missing user identification (student_id or user_id required)",
                    status_code=400
                )

            # Mark attendance in database
            result = mark_attendance(
                session_id=session_id,
                user_id=student_id,
                lat=lat,
                lon=lon,
                status='present'
            )
            
            if isinstance(result, dict) and 'error' in result:
                return error_response(message=result['error'], status_code=400)
            
            return success_response(
                data={
                    'record_id': result.record_id,
                    'student_id': student_id,
                    'session_id': session_id,
                    'location': {'lat': lat, 'lon': lon},
                    'check_in_time': result.check_in_time.isoformat(),
                    'status': result.status
                },
                message='Check-in successful'
            )
            
        except Exception as e:
            return error_response(
                message=f'Database error: {str(e)}',
                status_code=500
            )

    # Get session attendance
    @app.route('/session/<session_id>/attendance', methods=['GET'])
    def get_attendance(session_id):
        try:
            records = get_session_attendance(session_id)
            return success_response(
                data={
                    'session_id': session_id,
                    'attendance_records': [record.to_dict() for record in records],
                    'total_records': len(records)
                },
                message='Attendance records retrieved successfully'
            )
        except Exception as e:
            return error_response(
                message=f'Database error: {str(e)}',
                status_code=500
            )

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return error_response(
            message='Endpoint not found',
            status_code=404
        )

    @app.errorhandler(500)
    def internal_error(error):
        import logging
        logging.error(f"Internal server error: {str(error)}")
        return error_response(
            message='Internal server error',
            status_code=500
        )

    @app.errorhandler(Exception)
    def handle_exception(error):
        import logging
        logging.error(f"Unhandled exception: {str(error)}")
        return error_response(
            message='An unexpected error occurred',
            status_code=500
        )

    return app

# Create the app instance with error handling
try:
    app = create_app()
except Exception as e:
    import logging
    logging.error(f"Failed to create app: {str(e)}")
    raise

if __name__ == '__main__':
    from datetime import datetime
    app.run(debug=True)
