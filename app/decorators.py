"""
Custom decorators for authentication and authorization.
"""
from functools import wraps
from flask import flash, redirect, url_for, abort
from flask_login import current_user

def admin_required(f):
    """
    Decorator to restrict access to admin users only.
    Redirects unauthenticated users to login, and unauthorized users (non-admin)
    to a 403 Forbidden error.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login')) # Assuming 'auth.login' is your login route
        if not current_user.is_admin():
            abort(403) # Forbidden - user is authenticated but not an admin
        return f(*args, **kwargs)
    return decorated_function