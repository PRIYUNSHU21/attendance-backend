"""
🗄️ DATABASE CONNECTION - config/db.py

🎯 WHAT THIS FILE DOES:
This file sets up the connection between the Flask app and the database.
Think of it as the "bridge" that lets the app save and retrieve data.

🔧 FOR FRONTEND DEVELOPERS:
- This handles all database operations behind the scenes
- When your frontend calls an API, this file helps save/retrieve data
- Database tables are automatically created when the app starts
- No direct interaction needed, but good to understand the foundation

📋 WHAT HAPPENS HERE:
1. Creates the SQLAlchemy database object (db)
2. Connects to the database specified in settings
3. Creates all necessary tables automatically
4. Provides the foundation for all data operations

💾 DATABASE TABLES CREATED:
- users: User accounts and authentication info
- organizations: Different schools/companies using the system
- attendance_sessions: Classes/meetings that track attendance
- attendance_records: Individual check-in/check-out records
- user_sessions: Login session tracking

⚡ FOR FRONTEND INTEGRATION:
- All API endpoints use this database connection
- Data is automatically saved when users interact with your frontend
- Database changes are reflected immediately in API responses
- Supports transactions for data consistency

🔄 HOW IT WORKS:
Frontend → API Call → Route Handler → Service Function → Database (via this file) → Response back to Frontend

🛠️ SUPPORTED DATABASES:
- SQLite: Default for development (file-based)
- PostgreSQL: Recommended for production
- MySQL: Also supported for production
"""

from flask_sqlalchemy import SQLAlchemy

# Create the database instance
db = SQLAlchemy()

def init_db(app):
    """Initialize the database with the Flask app."""
    db.init_app(app)
    
    # Create all tables within app context
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

def reset_db(app):
    """Reset the database (drop all tables and recreate)."""
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Database reset successfully!")