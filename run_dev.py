#!/usr/bin/env python3
"""
Development startup script for Smart Task Manager
Uses SQLite for easy development and testing
"""

import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment variables for development
os.environ['FLASK_CONFIG'] = 'sqlite'
os.environ['SECRET_KEY'] = 'dev-secret-key-for-testing-only'

# Import and create the app
from app import create_app
from extensions import db

app = create_app('sqlite')

def init_database():
    """Initialize the database with tables"""
    with app.app_context():
        # Import models to ensure they are registered
        from models import User, Task
        
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")
        
        # Create a test user if none exists
        if User.query.first() is None:
            test_user = User(
                username='admin',
                email='admin@example.com'
            )
            test_user.set_password('admin123')
            db.session.add(test_user)
            db.session.commit()
            print("Test user created: admin/admin123")

if __name__ == '__main__':
    print("Starting Smart Task Manager in development mode...")
    print("Database: SQLite")
    print("URL: http://localhost:5000")
    print("Test credentials: admin/admin123")
    print("-" * 50)
    
    # Initialize database
    init_database()
    
    # Run the application
    try:
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            use_reloader=False
        )
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)
