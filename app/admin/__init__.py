from flask import Blueprint

# Admin blueprint for admin dashboard and management routes
admin_bp = Blueprint('admin', __name__)

from app.admin import views