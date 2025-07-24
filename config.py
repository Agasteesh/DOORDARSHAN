"""
Application configuration for Flask, database, email, and other settings.
"""
import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

# Define basedir at the module level, pointing to the root of the ott_platform directory
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base configuration class for Flask app settings."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Database URI: prefers environment variable, falls back to local SQLite
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'app.db')


    # Allowed extensions (still useful for validation)
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'mkv', 'webm', 'mov'}
    ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')


    # No local media folders needed; all uploads use S3

    # Celery configuration (uncomment if using Celery)
    # CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'redis://localhost:6379/0'
    # CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://localhost:6379/0'

class DevelopmentConfig(Config):
    DEBUG = True
    # Development database URI: prefers environment variable, falls back to local SQLite
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

class ProductionConfig(Config):
    DEBUG = False
    # Production database URI: prefers environment variable, should be a robust database like PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'postgresql://user:password@host:port/dbname' # REPLACE WITH YOUR ACTUAL PROD DB URI

    # Additional production-specific settings can go here
    # Example: LOG_LEVEL = 'INFO'

class TestingConfig(Config):
    TESTING = True
    # Testing database URI: typically an in-memory SQLite for fast, isolated tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Mapping for config types
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}