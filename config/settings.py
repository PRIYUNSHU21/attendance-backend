"""
⚙️ APPLICATION CONFIGURATION - config/settings.py

🎯 WHAT THIS FILE DOES:
This file contains ALL the settings and configuration for the attendance system.
Think of it as the "settings menu" that controls how the entire system behaves.

🔧 FOR FRONTEND DEVELOPERS:
- These settings affect API behavior (timeouts, security, etc.)
- Database connection settings are here
- CORS origins (which domains can access the API) are configured here
- Default values for attendance features (like geofence radius)

📋 KEY CONFIGURATIONS:
- JWT_SECRET_KEY: Used for securing authentication tokens
- DATABASE_URL: Where all the data is stored
- DEFAULT_GEOFENCE_RADIUS: How close users need to be to check in (meters)
- SESSION_EXPIRY_HOURS: How long login sessions last
- CORS_ORIGINS: Which frontend domains are allowed to call the API

🌍 ENVIRONMENTS:
- Development: Debug mode ON, local database, relaxed security
- Production: Debug mode OFF, external database, strict security
- Testing: In-memory database, fast testing

⚡ FOR FRONTEND INTEGRATION:
- Make sure your frontend domain is in CORS_ORIGINS
- JWT tokens expire after SESSION_EXPIRY_HOURS
- Location-based features use DEFAULT_GEOFENCE_RADIUS
- Check environment-specific API URLs

🔒 SECURITY SETTINGS:
- Never commit real SECRET_KEY values to git
- Use .env file for production secrets
- Different keys for development vs production
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class with common settings."""
    
    # Security settings
    SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key-change-in-production")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-secret-key-change-in-production")
    
    # Database settings
    if os.environ.get("RENDER"):
        # Use a writable directory on Render
        SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:////tmp/attendance.db")
    else:
        # Default for local development
        SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///attendance.db")
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.environ.get("SQLALCHEMY_ECHO", "False").lower() == "true"
    
    # Attendance settings
    DEFAULT_GEOFENCE_RADIUS = float(os.environ.get("DEFAULT_GEOFENCE_RADIUS", 100))  # in meters
    MAX_GEOFENCE_RADIUS = float(os.environ.get("MAX_GEOFENCE_RADIUS", 1000))  # in meters
    
    # Session settings
    SESSION_EXPIRY_HOURS = int(os.environ.get("SESSION_EXPIRY_HOURS", 24))
    TOKEN_EXPIRY_DAYS = int(os.environ.get("TOKEN_EXPIRY_DAYS", 1))
    
    # CORS settings
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")
    
    # Pagination settings
    DEFAULT_PAGE_SIZE = int(os.environ.get("DEFAULT_PAGE_SIZE", 20))
    MAX_PAGE_SIZE = int(os.environ.get("MAX_PAGE_SIZE", 100))

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_ECHO = False

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}