from flask import Flask
from config.db import configure_db, db

app = Flask(__name__)
configure_db(app)

with app.app_context():
    try:
        # Check users
        result = db.session.execute(db.text('SELECT email, role FROM users LIMIT 5'))
        print("Available users:")
        for row in result:
            print(f"Email: {row[0]}, Role: {row[1]}")
        
        # Check organizations
        orgs = db.session.execute(db.text('SELECT org_id, name FROM organisations LIMIT 5'))
        print("\nAvailable organizations:")
        for org in orgs:
            print(f"ID: {org[0]}, Name: {org[1]}")
    except Exception as e:
        print(f"Error: {str(e)}")
