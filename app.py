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
from config.db import init_db
from config.settings import config
from utils.response import success_response, error_response
import os

# Import route blueprints
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.reports import reports_bp
from routes.bulletproof_attendance import bulletproof_bp

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
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(bulletproof_bp, url_prefix='/bulletproof')   # Main attendance system

    # Health check endpoint
    @app.route('/', methods=['GET'])
    @app.route('/health', methods=['GET'])
    def health_check():
        """Simple health check endpoint."""
        return success_response(
            data={"status": "healthy", "service": "attendance_backend"},
            message="Service is running"
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
