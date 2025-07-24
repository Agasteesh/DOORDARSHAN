from flask import Blueprint

# Videos blueprint for video-related routes
videos_bp = Blueprint('videos', __name__, template_folder='templates')

from app.videos import views