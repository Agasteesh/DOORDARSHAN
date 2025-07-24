"""
Database models for users, videos, genres, and related entities.
"""
from app.extensions import db, login_manager  # Assuming 'db' and 'login_manager' are initialized in extensions.py
from flask_login import UserMixin
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app

# -----------------------------
# MODELS
# -----------------------------

class User(db.Model, UserMixin):
    """User model for authentication and authorization."""
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))  # Store hashed passwords
    role = db.Column(db.String(20), default='user', nullable=False)  # 'user' or 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    videos = db.relationship('Video', backref='uploader', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id}).decode('utf-8')  # decode to str

    def is_admin(self):
        return self.role == 'admin'

    @staticmethod
    def verify_reset_password_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        user_id = data.get('user_id')
        if user_id is None:
            return None
        return db.session.get(User, user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', 'Role: {self.role}')"

class Genre(db.Model):
    __tablename__ = 'genre'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    content = db.relationship('Content', backref='genre_obj', lazy='select')

    def __repr__(self):
        return f'<Genre {self.name}>'

class Content(db.Model):
    """Content model for uploaded video content."""
    __tablename__ = 'content'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    release_date = db.Column(db.Date)
    duration_seconds = db.Column(db.Integer)  # Duration in seconds

    original_video_url = db.Column(db.String(255))   # S3 URL to original uploaded file
    processed_video_url = db.Column(db.String(255))  # S3 URL to processed (web-friendly) video
    thumbnail_url = db.Column(db.String(255))        # S3 URL to thumbnail image

    genre_id = db.Column(db.Integer, db.ForeignKey('genre.id'))
    status = db.Column(db.String(50), default='pending_processing')  # 'ready', 'failed', etc.
    is_premium = db.Column(db.Boolean, default=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Content {self.title}>'

video_genre = db.Table(
    'video_genre',
    db.Column('video_id', db.Integer, db.ForeignKey('video.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True)
)

class Video(db.Model):
    """Video model for video files and metadata."""
    __tablename__ = 'video'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

    video_url = db.Column(db.String(255), unique=True, nullable=False)  # S3 URL for video
    thumbnail_url = db.Column(db.String(255))

    upload_date = db.Column(db.DateTime, default=datetime.utcnow)

    uploader_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    genres = db.relationship('Genre', secondary=video_genre, backref=db.backref('videos', lazy='dynamic'))
    genre_names = db.Column(db.String(255))  # Comma-separated genre names for denormalized access

    def update_genre_names(self):
        self.genre_names = ', '.join([g.name for g in self.genres])

    def __repr__(self):
        return f"Video('{self.title}', '{self.upload_date}')"

# -----------------------------
# Flask-Login User Loader
# -----------------------------

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))