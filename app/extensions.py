"""
Flask extension initialization and configuration.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
import boto3
import os

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()

def configure_extensions(app):
    """Initialize Flask extensions with the given app instance."""
    db.init_app(app)
    migrate.init_app(app, db)  # Initialized Flask-Migrate with the app and db
    login_manager.init_app(app)  # Used 'login_manager'
    mail.init_app(app)
    login_manager.login_view = 'auth.login' # Set the login view

    # User loader callback for Flask-Login
    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

# S3 configuration (use environment variables or config.py in production)
S3_BUCKET = os.environ.get('S3_BUCKET')
S3_REGION = os.environ.get('S3_REGION')
S3_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY_ID')
S3_SECRET_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

s3_client = boto3.client(
    's3',
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    region_name=S3_REGION
)

def upload_file_to_s3(file_obj, filename, folder=None, bucket_name=S3_BUCKET):
    """Uploads a file object to S3 in the specified folder and returns the file URL."""
    if folder:
        s3_key = f"{folder}/{filename}"
    else:
        s3_key = filename
    s3_client.upload_fileobj(file_obj, bucket_name, s3_key)
    url = f"https://{bucket_name}.s3.{S3_REGION}.amazonaws.com/{s3_key}"
    return url