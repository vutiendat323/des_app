import os

class Config:
    """Application configuration with secure defaults"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')
    
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Available chat rooms - stored as constant for now, could be moved to database
    CHAT_ROOMS = [
        'General',
        'Zero to Knowing',
    ]