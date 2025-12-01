import os
import uuid
from pathlib import Path
from datetime import datetime
import hashlib

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    allowed_extensions = {'pdf'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def generate_filename(original_name: str) -> str:
    """Generate unique filename with timestamp"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    name_hash = hashlib.md5(original_name.encode()).hexdigest()[:8]
    base_name = Path(original_name).stem[:50]  # Limit length
    return f"{base_name}_{timestamp}_{name_hash}"

def safe_delete(filepath: Path) -> bool:
    """Safely delete a file if it exists"""
    try:
        if filepath.exists():
            filepath.unlink()
            return True
    except Exception as e:
        print(f"Error deleting {filepath}: {e}")
    return False

def format_file_size(bytes_size: int) -> str:
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

def clean_directory(directory: Path, max_age_hours: int = 24):
    """Clean old files from directory"""
    if not directory.exists():
        return
    
    current_time = datetime.now().timestamp()
    
    for filepath in directory.iterdir():
        if filepath.is_file():
            file_age = current_time - filepath.stat().st_mtime
            
            if file_age > (max_age_hours * 3600):
                safe_delete(filepath)