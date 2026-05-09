#!/usr/bin/env python3
"""
PostgreSQL setup script for Smart Task Manager
This script helps set up PostgreSQL database and handles psycopg2 installation issues
"""

import os
import sys

def check_postgresql_requirements():
    """Check if PostgreSQL requirements are met"""
    print("Checking PostgreSQL requirements...")
    
    # Check if psycopg2 is available
    try:
        import psycopg2
        print("✓ psycopg2 is available")
        return True
    except ImportError:
        print("✗ psycopg2 is not available")
        print("\nTo install psycopg2, try one of these methods:")
        print("1. pip install psycopg2-binary")
        print("2. pip install psycopg2")
        print("3. Install PostgreSQL and add pg_config to PATH")
        return False

def setup_sqlite_fallback():
    """Set up SQLite as fallback database"""
    print("\nSetting up SQLite fallback database...")
    
    # Update config to use SQLite
    config_content = """import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///smart_task_dev.db'
    
class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://username:password@localhost/smart_task_db'

class SQLiteConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///smart_task.db'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'sqlite': SQLiteConfig,
    'default': SQLiteConfig  # Default to SQLite for easy testing
}
"""
    
    with open('config_dev.py', 'w') as f:
        f.write(config_content)
    
    print("✓ SQLite configuration created")
    return True

def create_database_setup_script():
    """Create a script to set up PostgreSQL database"""
    setup_script = """#!/bin/bash
# PostgreSQL Database Setup Script for Smart Task Manager

echo "Setting up PostgreSQL database for Smart Task Manager..."

# Check if PostgreSQL is running
if ! pg_isready -q; then
    echo "PostgreSQL is not running. Please start PostgreSQL service."
    exit 1
fi

# Create database
echo "Creating database..."
createdb smart_task_db 2>/dev/null || echo "Database already exists"

# Create user (optional)
echo "Creating user..."
createuser -s smart_task_user 2>/dev/null || echo "User already exists"

# Set up schema
echo "Setting up database schema..."
psql -d smart_task_db -f database/schema.sql

echo "PostgreSQL setup complete!"
echo "Update your DATABASE_URL to: postgresql://smart_task_user:password@localhost/smart_task_db"
"""
    
    with open('setup_postgres.sh', 'w') as f:
        f.write(setup_script)
    
    # Make script executable on Unix systems
    try:
        os.chmod('setup_postgres.sh', 0o755)
        print("✓ PostgreSQL setup script created: setup_postgres.sh")
    except:
        print("✓ PostgreSQL setup script created: setup_postgres.sh")
    
    return True

def create_windows_setup_script():
    """Create Windows setup script for PostgreSQL"""
    windows_script = """@echo off
REM PostgreSQL Database Setup Script for Smart Task Manager (Windows)

echo Setting up PostgreSQL database for Smart Task Manager...

REM Check if PostgreSQL is installed
psql --version >nul 2>&1
if errorlevel 1 (
    echo PostgreSQL is not installed or not in PATH
    echo Please install PostgreSQL from https://www.postgresql.org/download/windows/
    pause
    exit /b 1
)

REM Create database
echo Creating database...
createdb smart_task_db 2>nul || echo Database already exists

REM Set up schema
echo Setting up database schema...
psql -d smart_task_db -f database/schema.sql

echo PostgreSQL setup complete!
echo Update your DATABASE_URL to: postgresql://username:password@localhost/smart_task_db
pause
"""
    
    with open('setup_postgres.bat', 'w') as f:
        f.write(windows_script)
    
    print("✓ Windows PostgreSQL setup script created: setup_postgres.bat")
    return True

def main():
    """Main setup function"""
    print("Smart Task Manager - PostgreSQL Setup")
    print("=" * 50)
    
    if not check_postgresql_requirements():
        print("\nPostgreSQL is not properly configured.")
        choice = input("\nChoose an option:\n1. Set up SQLite fallback (recommended for development)\n2. Create PostgreSQL setup scripts\n3. Exit\n\nChoice (1-3): ")
        
        if choice == '1':
            setup_sqlite_fallback()
            print("\n✓ SQLite fallback configured. You can now run: python run_dev.py")
        elif choice == '2':
            create_database_setup_script()
            create_windows_setup_script()
            print("\n✓ Setup scripts created. Run the appropriate script for your system.")
        else:
            print("Exiting...")
            return
    else:
        print("\n✓ PostgreSQL is available. You can use PostgreSQL with the application.")
        print("To set up the database:")
        print("1. Run: psql -d postgres -c 'CREATE DATABASE smart_task_db;'")
        print("2. Run: psql -d smart_task_db -f database/schema.sql")
        print("3. Set DATABASE_URL environment variable")

if __name__ == '__main__':
    main()
