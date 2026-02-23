import os
import uuid
from pathlib import Path
from app.config import settings


def ensure_upload_directory() -> str:
    """Ensure upload directory exists"""
    upload_dir = settings.UPLOAD_DIR
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir


def save_uploaded_file(file_content: bytes, original_filename: str, assessment_id: int, response_id: int) -> str:
    """
    Save uploaded file and return relative path.
    Files stored in: uploads/evidence/{assessment_id}/{response_id}/
    """
    ensure_upload_directory()
    
    # Create directory structure
    file_dir = os.path.join(settings.UPLOAD_DIR, "evidence", str(assessment_id), str(response_id))
    os.makedirs(file_dir, exist_ok=True)
    
    # Generate unique filename to prevent conflicts
    file_ext = Path(original_filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    
    file_path = os.path.join(file_dir, unique_filename)
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Return relative path from upload directory
    return os.path.relpath(file_path, settings.UPLOAD_DIR)


def validate_file_type(file_ext: str) -> bool:
    """Validate file extension against allowed types"""
    if not file_ext:
        return False
    return file_ext.lower() in settings.allowed_file_types_list


def validate_file_size(file_size_bytes: int) -> bool:
    """Validate file size against maximum allowed"""
    max_size_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    return file_size_bytes <= max_size_bytes


def delete_file(file_path: str) -> bool:
    """Delete a file from storage"""
    full_path = os.path.join(settings.UPLOAD_DIR, file_path)
    if os.path.exists(full_path):
        try:
            os.remove(full_path)
            return True
        except Exception:
            return False
    return False
