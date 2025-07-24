"""
Shared form classes for user and video management.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FileField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from flask_wtf.file import FileAllowed, FileRequired
from app.models import User, Genre
from wtforms.widgets import ListWidget, CheckboxInput

# --- Shared User Registration Form ---
class BaseUserForm(FlaskForm):
    """Base form for user registration and management."""
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('user', 'User'), ('admin', 'Admin')], validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_username(self, username):
        """Ensure the username is unique."""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        """Ensure the email is unique."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

# --- Shared Video Form ---
class BaseVideoForm(FlaskForm):
    """Base form for video upload and management."""
    title = StringField('Title', validators=[DataRequired(), Length(max=255)])
    description = TextAreaField('Description')
    video_file = FileField('Video File', validators=[
        FileRequired(),
        FileAllowed(['mp4', 'mkv', 'webm', 'mov', 'avi'], 'Videos only!')
    ])
    thumbnail_file = FileField('Thumbnail Image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    genres = SelectMultipleField('Genres', coerce=int, option_widget=CheckboxInput(), widget=ListWidget(prefix_label=False))
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        """Populate genre choices dynamically from the database."""
        super().__init__(*args, **kwargs)
        self.genres.choices = [(g.id, g.name) for g in Genre.query.order_by(Genre.name).all()]

from wtforms import HiddenField

class RegistrationForm(BaseUserForm):
    """User registration form."""
    role = HiddenField(default='user')

class LoginForm(FlaskForm):
    """User login form."""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class DeleteAccountForm(FlaskForm):
    password = PasswordField('Confirm Password', validators=[DataRequired()])
    confirm_delete = BooleanField('I understand that deleting my account is permanent and cannot be undone.', validators=[DataRequired()])
    submit = SubmitField('Delete Account')