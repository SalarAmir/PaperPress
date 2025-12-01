import os
from pathlib import Path

# Load .env file if present so environment variables are available when running locally
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # dotenv is optional; if not installed, environment variables must be set externally
    pass

class Config:
    """Application configuration"""
    BASE_DIR = Path(__file__).parent
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # File paths
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    OUTPUT_FOLDER = BASE_DIR / 'outputs'
    
    # File restrictions
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'pdf'}
    
    # Gemini API
    # Trim whitespace to avoid issues with accidental leading/trailing spaces
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '').strip()
    
    # LaTeX settings
    LATEX_COMPILER = 'pdflatex'  # or 'xelatex'
    
    @staticmethod
    def init_app(app):
        """Initialize application with config"""
        app.config.from_object(Config)
        
        # Create directories if they don't exist
        Config.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
        Config.OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)