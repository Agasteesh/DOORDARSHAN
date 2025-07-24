"""
Authentication and user account management routes.
"""
from flask import render_template, redirect, url_for, flash, request, Blueprint
from flask_login import current_user, login_user, logout_user, login_required
from app.extensions import db
from app.forms import RegistrationForm, LoginForm, ResetPasswordRequestForm, ResetPasswordForm, DeleteAccountForm
from app.auth.token import send_password_reset_email
from app.decorators import admin_required
from app.models import User

auth_bp = Blueprint('auth', __name__, template_folder='../templates/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login route with S3 gallery thumbnails."""
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.admin_dashboard'))
        return redirect(url_for('videos.list_content'))
    form = LoginForm()
    from app.models import Video
    s3_thumbnails = [v.thumbnail_url for v in Video.query.order_by(Video.id.desc()).limit(9).all() if v.thumbnail_url]
    try:
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user is None or not user.check_password(form.password.data):
                flash('Invalid username or password', 'danger')
                return redirect(url_for('auth.login'))
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('admin.admin_dashboard') if user.is_admin() else url_for('videos.list_content')
            return redirect(next_page)
    except Exception as e:
        flash(f'An error occurred during login: {e}', 'danger')
    return render_template('login.html', title='Sign In', form=form, s3_thumbnails=s3_thumbnails)

@auth_bp.route('/logout')
def logout():
    """Log out the current user."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('videos.list_content'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route with S3 gallery thumbnails."""
    if current_user.is_authenticated:
        return redirect(url_for('videos.list_content'))
    form = RegistrationForm()
    from app.models import Video
    s3_thumbnails = [v.thumbnail_url for v in Video.query.order_by(Video.id.desc()).limit(9).all() if v.thumbnail_url]
    if form.is_submitted() and not form.validate():
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {getattr(form, field).label.text}: {error}", 'danger')
    if form.validate_on_submit():
        try:
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            user.role = 'user'
            db.session.add(user)
            db.session.commit()
            flash('Congratulations, you are now a registered user!', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error during registration: {e}', 'danger')
    return render_template('register.html', title='Register', form=form, s3_thumbnails=s3_thumbnails)

@auth_bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """Request a password reset email."""
    if current_user.is_authenticated:
        return redirect(url_for('videos.list_content'))
    form = ResetPasswordRequestForm()
    try:
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                # send_password_reset_email(user)  # Uncomment when email is set up
                flash('Check your email for the instructions to reset your password')
                return redirect(url_for('auth.login'))
            else:
                flash('Email address not found.')
    except Exception as e:
        flash(f'Error processing password reset request: {e}', 'danger')
    return render_template('reset_password_request.html', title='Reset Password', form=form)

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password using a token."""
    if current_user.is_authenticated:
        return redirect(url_for('videos.list_content'))
    try:
        user = User.verify_reset_password_token(token)
        if not user:
            return redirect(url_for('videos.list_content'))
        form = ResetPasswordForm()
        if form.validate_on_submit():
            user.set_password(form.password.data)
            db.session.commit()
            flash('Your password has been reset.')
            return redirect(url_for('auth.login'))
        return render_template('reset_password.html', title='Reset Password', form=form)
    except Exception as e:
        flash(f'Error resetting password: {e}', 'danger')
        return redirect(url_for('auth.login'))

@auth_bp.route('/delete_account', methods=['GET', 'POST'])
@login_required
def delete_account():
    """Allow a user to delete their own account."""
    form = DeleteAccountForm()
    try:
        if form.validate_on_submit():
            if not current_user.check_password(form.password.data):
                flash('Incorrect password. Please try again.', 'danger')
            elif form.confirm_delete.data:
                db.session.delete(current_user._get_current_object())
                db.session.commit()
                logout_user()
                flash('Your account has been deleted.')
                return redirect(url_for('videos.list_content'))
            else:
                flash('Please confirm you understand the consequences of deleting your account.')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting account: {e}', 'danger')
    return render_template('delete_account.html', title='Delete Account', form=form)