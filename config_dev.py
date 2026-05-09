import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
class DevelopmentConfig(Config):
    DEBUG = True
    # Use SQLite for development/testing
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///smart_task_dev.db'
    
class ProductionConfig(Config):
    DEBUG = False
    # Use PostgreSQL for production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://username:password@localhost/smart_task_db'

class SQLiteConfig(Config):
    DEBUG = True
    # SQLite configuration for easy testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///smart_task.db'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'sqlite': SQLiteConfig,
    'default': SQLiteConfig  # Default to SQLite for easy testing
}
