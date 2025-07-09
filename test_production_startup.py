#!/usr/bin/env python3
"""
Production startup test - Check if the app can start in production mode
"""
import os
import sys
from app import create_app

def test_production_startup():
    """Test if the app can start in production configuration."""
    
    print("🚀 Testing Production Startup...")
    
    # Set production environment variables
    os.environ['FLASK_ENV'] = 'production'
    os.environ['DATABASE_URL'] = 'sqlite:///test_prod.db'  # Use SQLite for test
    
    try:
        # Create app with production config
        app = create_app('production')
        print("✅ App created successfully")
        
        # Test app context
        with app.app_context():
            print("✅ App context works")
            
            # Test basic route
            with app.test_client() as client:
                response = client.get('/health')
                print(f"✅ Health check: {response.status_code} - {response.get_json()}")
                
                # Test public endpoints
                response = client.get('/auth/public/organizations')
                print(f"✅ Public organizations: {response.status_code}")
                
        print("🎉 Production startup test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Production startup test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_production_startup()
    sys.exit(0 if success else 1)
