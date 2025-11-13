import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Supabase configuration
    SUPABASE_URL = os.environ.get('SUPABASE_URL') or 'https://mtninpdmcqqvseyhcfho.supabase.co'
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY') or 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im10bmlucGRtY3FxdnNleWhjZmhvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkxMTY5OTQsImV4cCI6MjA3NDY5Mjk5NH0.nwQB1UTK6ETi6B7ktitP-Eh7cdeDC3xZza2v5cNqUqo'
    DATABASE_NAME = os.environ.get('DATABASE_NAME') or 'security_plus_training'
    
    # Email configuration (for future use)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Application settings
    APP_NAME = 'Security Plus Training Tool'
    APP_VERSION = '1.0.0'
    # APP_URL should be set via environment variable for production
    # Default to production domain: https://securityplustrainingprogram.com
    # For local development, set: export APP_URL=http://localhost:5000
    APP_URL = os.environ.get('APP_URL', 'https://securityplustrainingprogram.com')  # Base URL for redirects
    
    # Pagination
    POSTS_PER_PAGE = 10
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    WTF_CSRF_ENABLED = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
