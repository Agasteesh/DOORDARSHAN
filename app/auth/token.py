"""
Token generation and email sending utilities for password reset and email confirmation.
"""
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask_mail import Message
from app.extensions import mail
from flask import render_template, current_app, url_for
from threading import Thread

def generate_password_reset_token(user_id, expiration=3600):
    """Generate a timed password reset token for a user."""
    s = Serializer(current_app.config['SECRET_KEY'], expiration)
    return s.dumps({'user_id': user_id}).decode('utf-8')

def verify_password_reset_token(token, max_age=3600):
    """Verify a password reset token and return the user_id if valid."""
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token, max_age=max_age)
    except Exception:
        return None
    return data.get('user_id')

def send_async_email(app, msg):
    """Send email asynchronously in a separate thread."""
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    """Send an email with both text and HTML bodies."""
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()

def send_password_reset_email(user):
    """Send a password reset email to the user."""
    token = generate_password_reset_token(user.id)
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    send_email('[Your OTT Platform] Reset Your Password',
               sender=current_app.config['MAIL_USERNAME'],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token, reset_url=reset_url),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token, reset_url=reset_url))