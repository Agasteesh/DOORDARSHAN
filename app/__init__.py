"""
Flask application factory and setup for the OTT platform.
Initializes extensions, blueprints, and CLI commands.
"""
from flask import Flask, render_template
from app.extensions import db, login_manager, migrate, mail
from config import Config

def create_app(config_class=Config):
    """
    Flask application factory. Sets up extensions, blueprints, and CLI commands.
    """
    app = Flask(__name__)
    app.config.from_object(config_class or Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)

    # Import models for migrations
    from .models import User, Video, Genre, Content

    # Flask-Login config
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))

    # Register blueprints
    from app.auth.views import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.videos.views import videos_bp
    app.register_blueprint(videos_bp, url_prefix='/videos')

    from app.admin.views import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    @app.route('/')
    def index():
        return render_template("index.html")

    # Redirect /register to /auth/register for user convenience
    @app.route('/register')
    def register_redirect():
        from flask import redirect, url_for
        return redirect(url_for('auth.register'))

    @app.cli.command('seed-genres')
    def seed_genres():
        """Insert default genres into the database if not present."""
        from app.models import Genre
        default_genres = [
            'Action', 'Adventure', 'Comedy', 'Drama', 'Horror', 'Thriller', 'Crime',
            'Mystery', 'Romance', 'Fantasy', 'Sci-Fi', 'Animation', 'Musical', 'Family', 'Documentary'
        ]
        for genre_name in default_genres:
            if not Genre.query.filter_by(name=genre_name).first():
                db.session.add(Genre(name=genre_name))
        db.session.commit()
        print('Default genres seeded.')

    return app