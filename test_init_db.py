#!/usr/bin/env python3
"""
Test the updated init_db function
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

try:
    print("1. Importing modules...")
    from app import create_app
    
    print("2. Creating app...")
    app = create_app()
    
    print("3. ✅ App created successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
