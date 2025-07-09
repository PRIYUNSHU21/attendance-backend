#!/usr/bin/env python3
"""
Production startup script with enhanced error handling for Render deployment
"""
import os
import logging
import sys
from app import create_app

# Configure logging for production debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main production startup with comprehensive error handling."""
    
    logger.info("🚀 Starting Attendance Backend on Render...")
    
    # Log environment info
    logger.info(f"Python version: {sys.version}")
    logger.info(f"FLASK_ENV: {os.getenv('FLASK_ENV', 'not set')}")
    logger.info(f"PORT: {os.getenv('PORT', 'not set')}")
    logger.info(f"DATABASE_URL: {'set' if os.getenv('DATABASE_URL') else 'not set'}")
    
    try:
        # Create Flask app
        config_name = os.getenv('FLASK_ENV', 'production')
        logger.info(f"Creating app with config: {config_name}")
        
        app = create_app(config_name)
        logger.info("✅ Flask app created successfully")
        
        # Test basic functionality
        with app.app_context():
            logger.info("✅ App context established")
            
            # Test database connection
            from config.db import db
            try:
                # Simple query to test DB connection
                db.session.execute("SELECT 1").fetchone()
                logger.info("✅ Database connection successful")
            except Exception as db_error:
                logger.error(f"❌ Database connection failed: {str(db_error)}")
                raise
        
        logger.info("🎉 App startup successful!")
        return app
        
    except Exception as e:
        logger.error(f"❌ App startup failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

if __name__ == "__main__":
    app = main()
    port = int(os.getenv('PORT', 5000))
    host = '0.0.0.0'
    
    logger.info(f"Starting server on {host}:{port}")
    app.run(host=host, port=port, debug=False)
else:
    # For gunicorn
    app = main()
