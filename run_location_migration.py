#!/usr/bin/env python3
"""
Run the database migration to add location columns to organizations table
"""

from app import create_app
from migrations.add_location_columns import run_migration

def main():
    """Run migration within Flask app context"""
    app = create_app()
    
    with app.app_context():
        print("Running migration to add location columns...")
        run_migration()
        print("Migration completed successfully!")

if __name__ == "__main__":
    main()
