def delete_associated_files(video_filename=None, thumbnail_filename=None):
    """
    Delete associated video and thumbnail files from S3 or local storage. This is a stub implementation.
    Extend this function to actually delete files from S3 if needed.
    """
    # Example: If using S3, you would call the S3 delete API here.
    # For now, just pass (no-op)
    pass
"""
Utility functions for file upload and validation.
"""
import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app
from app.extensions import upload_file_to_s3

def allowed_file(filename, allowed_extensions):
    """Check if a file's extension is allowed."""
    try:
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions
    except Exception as e:
        raise ValueError(f'Error checking allowed file: {e}')


def save_uploaded_file(file):
    """Upload a file to S3 in the appropriate folder and return the S3 URL. Enforces allowed extensions server-side."""
    try:
        if file.filename == '':
            return None # No file selected

        allowed_video_exts = {'mp4', 'mkv', 'webm', 'mov', 'avi'}
        allowed_image_exts = {'jpg', 'jpeg', 'png', 'gif'}
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        filename = secure_filename(file.filename)
        unique_filename = str(uuid.uuid4()) + '.' + file_extension

        # Determine type by context or filename
        if 'video' in file.name or 'video' in filename:
            if file_extension not in allowed_video_exts:
                raise ValueError('Invalid video file type.')
        elif 'thumb' in file.name or 'image' in file.name or 'thumb' in filename:
            if file_extension not in allowed_image_exts:
                raise ValueError('Invalid image file type.')
        else:
            # Fallback: only allow video or image extensions
            if file_extension not in allowed_video_exts and file_extension not in allowed_image_exts:
                raise ValueError('Invalid file type.')

        # S3-only: Determine S3 folder based on file type or context if needed
        s3_folder = ''  # Update as needed for S3 structure

        # Upload to S3 and return the S3 URL
        return upload_file_to_s3(file, unique_filename, folder=s3_folder)
    except Exception as e:
        raise ValueError(f'Error saving uploaded file: {e}')