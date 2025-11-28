"""
Utility functions for file upload and validation.
"""
import os
import re
import hashlib
from pathlib import Path
from typing import Tuple, Optional
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings


def validate_file(file: UploadedFile) -> Tuple[bool, Optional[str]]:
    """
    Validate uploaded file.
    
    Args:
        file: Django uploaded file object
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check file size
    if file.size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
        return False, f"File size exceeds maximum allowed size of {settings.FILE_UPLOAD_MAX_MEMORY_SIZE / (1024*1024):.1f} MB"
    
    # Check file extension
    file_ext = Path(file.name).suffix.lower()
    if file_ext not in settings.ALLOWED_FILE_EXTENSIONS:
        return False, f"Unsupported file extension: {file_ext}"
    
    # Check MIME type
    if file.content_type not in settings.ALLOWED_FILE_TYPES:
        return False, f"Unsupported MIME type: {file.content_type}"
    
    return True, None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal and special characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove directory separators and special characters
    filename = re.sub(r'[^\w\s.-]', '', filename)
    filename = re.sub(r'\.{2,}', '', filename)  # Remove multiple dots
    filename = filename.strip('.')
    
    # Ensure unique filename using hash
    name, ext = os.path.splitext(filename)
    hash_part = hashlib.md5(name.encode()).hexdigest()[:8]
    filename = f"{name}_{hash_part}{ext}"
    
    return filename


def ensure_upload_dir():
    """Ensure upload directory exists."""
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

