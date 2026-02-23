import re
import os
from typing import Optional


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_project_code(code: str) -> bool:
    """Validate project code format (alphanumeric, hyphens, underscores)"""
    pattern = r'^[A-Za-z0-9_-]+$'
    return bool(re.match(pattern, code))


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent directory traversal and other issues"""
    # Remove path components
    filename = os.path.basename(filename)
    # Remove dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:250] + ext
    return filename
