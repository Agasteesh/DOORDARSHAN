"""
Video content, upload, and streaming routes for the OTT platform.
All file storage is S3-only. Local storage logic has been removed.
"""
from flask import render_template, redirect, url_for, flash, request, Response, current_app
from flask_login import login_required, current_user
from app.videos import videos_bp
from app.models import Content, Genre, Video
from app.extensions import db, upload_file_to_s3
from datetime import datetime
from app.decorators import admin_required
from app.forms import BaseVideoForm
from app.utils.file_handling import save_uploaded_file

@videos_bp.route('/')
@login_required
def list_content():
    """List all video content, grouped by genre, with optional search."""
    genre_id = request.args.get('genre', type=int)
    search_query = request.args.get('search', '').strip()
    all_genres = Genre.query.order_by(Genre.name).all()
    # Build a dict: genre -> list of videos (filtered by search and genre)
    genre_videos = {genre: [] for genre in all_genres}
    base_query = Video.query
    if search_query:
        base_query = base_query.filter(
            (Video.title.ilike(f"%{search_query}%")) | (Video.description.ilike(f"%{search_query}%"))
        )
    videos = base_query.all()
    for video in videos:
        for genre in video.genres:
            if genre in genre_videos:
                genre_videos[genre].append(video)
    selected_genre_id = genre_id
    return render_template(
        'videos/list_content.html',
        genres=all_genres,
        genre_videos=genre_videos,
        selected_genre_id=selected_genre_id
    )

@videos_bp.route('/video/<int:video_id>')
@login_required
def video_detail(video_id):
    """Show details for a single video."""
    video = Video.query.get_or_404(video_id)
    return render_template('videos/video_detail.html', video=video)

@videos_bp.route('/<int:content_id>')
@login_required
def content_detail(content_id):
    """Show details for a content item, including watch progress."""
    content = db.session.get(Content, content_id) # Use db.session.get for primary key
    if not content or content.status != 'ready':
        flash('Content not found or not yet processed.', 'warning')
        return redirect(url_for('videos.list_content'))
    
    return render_template('videos/content_detail.html', content=content)

@videos_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_content():
    """Admin route to upload new video content."""
    if not current_user.is_admin:
        flash('You do not have permission to upload content.', 'danger')
        return redirect(url_for('videos.list_content'))

    form = BaseVideoForm()
    if form.validate_on_submit():
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
            # Always assign Genre objects, not IDs
            genre_ids = request.form.getlist('genres') or request.form.getlist('genres[]')
            genre_ids = [int(gid) for gid in genre_ids if str(gid).isdigit()]
            if not genre_ids:
                flash('Please select at least one genre.', 'danger')
                return render_template('videos/upload_content.html', form=form)
            selected_genres = Genre.query.filter(Genre.id.in_(genre_ids)).all()
            new_video.genres = selected_genres
            new_video.update_genre_names()
            db.session.add(new_video)
            db.session.commit()
            flash('Video uploaded successfully!', 'success')
            return redirect(url_for('videos.list_content'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error uploading video: {e}', 'danger')
    return render_template('videos/upload_content.html', form=form)

@videos_bp.route('/stream/<filename>')
def stream_video(filename):
    """Stream a processed video file with HTTP Range support."""
    # S3-only: implement S3 streaming logic here if needed
    return "S3 streaming not implemented", 501

@videos_bp.route('/thumbnails/<filename>')
def serve_thumbnail(filename):
    """Serve a video thumbnail image from S3 (not implemented)."""
    return "S3 thumbnail serving not implemented", 501