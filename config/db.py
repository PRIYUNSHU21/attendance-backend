"""
🗄️ DATABASE CONFIGURATION - config/db.py

🎯 WHAT THIS FILE DOES:
This file sets up the database connection and initialization for the Flask app.
It configures SQLAlchemy to handle all database operations.

🔧 DATABASE SETUP:
- Creates SQLAlchemy instance for database operations
- Provides init_db() function to initialize database with app
- Handles database table creation and setup
"""

from flask_sqlalchemy import SQLAlchemy

# Create SQLAlchemy instance
db = SQLAlchemy()

def init_db(app):
    """Initialize database with Flask app."""
    db.init_app(app)
    
    with app.app_context():
        # Import all models to ensure they're registered with SQLAlchemy
        from models.user import User
        from models.organisation import Organisation
        from models.session import UserSession
        from models.attendance import AttendanceSession, AttendanceRecord
        
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully!")
        
    return db