#!/usr/bin/env python3
"""
Test database initialization script
"""
from flask import Flask
from config.db import init_db

def create_test_app():
    import os
    app = Flask(__name__)
    db_path = os.path.join(os.getcwd(), 'instance', 'attendance.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    return app

if __name__ == '__main__':
    app = create_test_app()
    init_db(app)
    print("Database initialized successfully!")
