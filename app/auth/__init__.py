from flask import Blueprint

# Auth blueprint for authentication routes
auth_bp = Blueprint('auth', __name__, template_folder='templates')

from app.auth import views, token