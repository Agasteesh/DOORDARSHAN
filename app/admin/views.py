"""
Admin dashboard and management routes for users and videos.
"""
import os
from flask import render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_required, current_user
from app import db
from app.models import User, Video, Genre
from app.decorators import admin_required
from app.utils.file_handling import save_uploaded_file, delete_associated_files
from app.admin import admin_bp
from app.forms import BaseUserForm, BaseVideoForm
from wtforms import FileField
from flask_wtf.file import FileAllowed, FileRequired

@admin_bp.route('/edit_video_inline/<int:video_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_video_inline(video_id):
    """Edit a video inline from the admin dashboard."""
    video = Video.query.get_or_404(video_id)
    form = EditVideoForm(obj=video)
    if request.method == 'POST':
        genre_ids = request.form.getlist('genres') or request.form.getlist('genres[]')
        form.genres.data = [int(gid) for gid in genre_ids if gid.isdigit()]
    else:
        genre_ids = [g.id for g in video.genres]
        form.genres.data = genre_ids
    if form.validate_on_submit():
        try:
            if form.video_file.data and form.video_file.data.filename != '':
                delete_associated_files(video_filename=video.video_url)
                video.video_url = save_uploaded_file(form.video_file.data)
            if form.thumbnail_file.data and form.thumbnail_file.data.filename != '':
                delete_associated_files(thumbnail_filename=video.thumbnail_url)
                video.thumbnail_url = save_uploaded_file(form.thumbnail_file.data)

            form_data = {field.name: field.data for field in form if field.name != 'genres'}
            for key, value in form_data.items():
                setattr(video, key, value)
            selected_genres = Genre.query.filter(Genre.id.in_(form.genres.data)).all()
            if not selected_genres:
                flash('Please select at least one genre.', 'danger')
                return render_template('admin/edit_video_inline.html', form=form, video=video)
            video.genres = selected_genres
            video.update_genre_names()
            db.session.commit()
            flash('Video details updated successfully!', 'success')
            return redirect(url_for('admin.admin_dashboard', section='videos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating video: {e}', 'danger')
            return render_template('admin/edit_video_inline.html', form=form, video=video)
    # On GET or failed POST, return the form HTML
    return render_template('admin/edit_video_inline.html', form=form, video=video)

@admin_bp.route('/')
@login_required
@admin_required
def admin_dashboard():
    """Admin dashboard main view with user and video management."""
    users = User.query.all()
    videos = Video.query.all()
    add_user_form = AddUserForm()
    add_video_form = AddVideoForm()
    return render_template(
        'admin/admin_dashboard.html',
        users=users,
        videos=videos,
        add_user_form=add_user_form,
        add_video_form=add_video_form
    )

# --- User Management ---
@admin_bp.route('/users')
@login_required
@admin_required
def list_users():
    """List all users (legacy, not used in unified dashboard)."""
    users = User.query.all()
    return render_template('admin/user_list.html', users=users)

@admin_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    """Add a new user from the admin dashboard."""
    form = AddUserForm()
    try:
        if form.validate_on_submit():
            user = User(username=form.username.data,
                        email=form.email.data,
                        role=form.role.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash(f'User "{user.username}" added successfully!', 'success')
            return redirect(url_for('admin.admin_dashboard', section='users'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding user: {e}', 'danger')
    # If not valid, redirect back to dashboard with adduser section and flash errors
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text}: {error}", 'danger')
    return redirect(url_for('admin.admin_dashboard', section='adduser'))

@admin_bp.route('/users/remove/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def remove_user(user_id):
    """Remove a user by ID, except self."""
    user = User.query.get_or_404(user_id)
    # Prevent admin from deleting themselves
    if user.id == current_user.id:
        flash('You cannot delete your own admin account.', 'danger')
        return redirect(url_for('admin.list_users'))
    try:
        db.session.delete(user)
        db.session.commit()
        flash(f'User "{user.username}" removed.', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'Error removing user: {e}', 'danger')
    return redirect(url_for('admin.admin_dashboard', section='users'))

# --- Video Management ---
@admin_bp.route('/videos')
@login_required
@admin_required
def list_videos():
    """List all videos (legacy, not used in unified dashboard)."""
    videos = Video.query.all()
    return render_template('admin/video_list.html', videos=videos)

@admin_bp.route('/videos/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_video():
    """Add a new video from the admin dashboard."""
    form = AddVideoForm()
    if request.method == 'POST':
        genre_ids = request.form.getlist('genres') or request.form.getlist('genres[]')
        try:
            video_path = save_uploaded_file(form.video_file.data)
            thumbnail_path = save_uploaded_file(form.thumbnail_file.data)
            if not video_path or not thumbnail_path:
                raise ValueError("Video file and thumbnail are required.")
            new_video = Video(
                title=form.title.data,
                description=form.description.data,
                video_url=video_path,
                thumbnail_url=thumbnail_path,
                uploader=current_user
            )
            genre_ids = [int(gid) for gid in genre_ids if gid.isdigit()]
            selected_genres = Genre.query.filter(Genre.id.in_(genre_ids)).all()
            new_video.genres = selected_genres
            new_video.update_genre_names()
            db.session.add(new_video)
            db.session.commit()
            flash('Video added successfully!', 'success')
            return redirect(url_for('admin.admin_dashboard', section='videos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding video: {e}', 'danger')
            # Re-render dashboard with form errors and section open
            users = User.query.all()
            videos = Video.query.all()
            add_user_form = AddUserForm()
            add_video_form = form
            return render_template(
                'admin/admin_dashboard.html',
                users=users,
                videos=videos,
                add_user_form=add_user_form,
                add_video_form=add_video_form,
                section='addvideo'
            )
    return redirect(url_for('admin.admin_dashboard', section='addvideo'))

@admin_bp.route('/videos/edit/<int:video_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_video(video_id):
    """Edit a video from the admin dashboard."""
    video = Video.query.get_or_404(video_id)
    form = EditVideoForm(obj=video)
    if request.method == 'POST':
        genre_ids = request.form.getlist('genres') or request.form.getlist('genres[]')
        form.genres.data = [int(gid) for gid in genre_ids if gid.isdigit()]
    else:
        genre_ids = [g.id for g in video.genres]
        form.genres.data = genre_ids
    if form.validate_on_submit():
        try:
            if form.video_file.data and form.video_file.data.filename != '':
                delete_associated_files(video_filename=video.video_url)
                video.video_url = save_uploaded_file(form.video_file.data)
            if form.thumbnail_file.data and form.thumbnail_file.data.filename != '':
                delete_associated_files(thumbnail_filename=video.thumbnail_url)
                video.thumbnail_url = save_uploaded_file(form.thumbnail_file.data)

            # Manually populate all fields except genres
            form_data = {field.name: field.data for field in form if field.name != 'genres'}
            for key, value in form_data.items():
                setattr(video, key, value)
            # Now set genres using model instances
            selected_genres = Genre.query.filter(Genre.id.in_(form.genres.data)).all()
            video.genres = selected_genres
            video.update_genre_names()
            db.session.commit()
            flash('Video details updated successfully!', 'success')
            return redirect(url_for('admin.list_videos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating video: {e}', 'danger')
    # On failed POST, genres stay checked
    return render_template('admin/edit_video.html', form=form, video=video)

@admin_bp.route('/videos/delete/<int:video_id>', methods=['POST'])
@login_required
@admin_required
def delete_video(video_id):
    """Delete a video and its associated files."""
    video = Video.query.get_or_404(video_id)

    try:
        # Delete associated files from the file system first
        delete_associated_files(
            video_filename=video.video_url,
            thumbnail_filename=video.thumbnail_url
        )
        db.session.delete(video)
        db.session.commit()
        flash(f'Video "{video.title}" and associated files deleted successfully.', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting video: {e}', 'danger')

    # Redirect to admin dashboard and show videos section
    return redirect(url_for('admin.admin_dashboard', section='videos'))

class AddUserForm(BaseUserForm):
    """Form for adding a user in the admin dashboard."""
    pass


class AddVideoForm(BaseVideoForm):
    """Form for adding a video in the admin dashboard."""
    video_file = FileField('Video File', validators=[
        FileRequired(),
        FileAllowed(['mp4', 'mkv', 'webm', 'mov', 'avi'], 'Videos only!')
    ])
    thumbnail_file = FileField('Thumbnail Image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])

class EditVideoForm(BaseVideoForm):
    """Form for editing a video in the admin dashboard."""
    video_file = FileField('Video File', validators=[
        FileAllowed(['mp4', 'mkv', 'webm', 'mov', 'avi'], 'Videos only!')
    ])
    thumbnail_file = FileField('Thumbnail Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])