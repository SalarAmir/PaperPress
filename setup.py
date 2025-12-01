#!/usr/bin/env python3
"""
Setup script for Study Note Generator
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a shell command with error handling"""
    print(f"\n{description}...")
    try:
        subprocess.run(cmd, shell=True, check=True)
        print("✓ Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed: {e}")
        return False

def create_directory_structure():
    """Create the project directory structure"""
    dirs = [
        'static/css',
        'static/js',
        'templates',
        'uploads',
        'outputs',
        'modules',
        'utils'
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {dir_path}")
    
    return True

def check_python_version():
    """Check Python version"""
    if sys.version_info < (3, 8):
        print("✗ Python 3.8 or higher is required")
        return False
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_latex_installation():
    """Check if LaTeX is installed"""
    try:
        subprocess.run(['pdflatex', '--version'], 
                      capture_output=True, 
                      check=False)
        print("✓ LaTeX (pdflatex) is installed")
        return True
    except FileNotFoundError:
        print("⚠ LaTeX is not installed. PDF compilation will not work locally.")
        print("  Install TeX Live (Linux/Mac) or MiKTeX (Windows)")
        return False

def create_requirements_file():
    """Create requirements.txt file"""
    requirements = """Flask==3.0.0
google-generativeai==0.3.0
PyPDF2==3.0.0
python-dotenv==1.0.0
"""
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements)
    
    print("✓ Created requirements.txt")
    return True

def create_env_template():
    """Create .env template"""
    env_template = """# Gemini API Key (get from: https://makersuite.google.com/app/apikey)
GEMINI_API_KEY=your_api_key_here

# Flask Settings
FLASK_SECRET_KEY=generate_with: python -c "import secrets; print(secrets.token_hex(16))"
FLASK_ENV=development

# Application Settings
MAX_FILE_SIZE_MB=16
"""
    
    with open('.env.example', 'w') as f:
        f.write(env_template)
    
    print("✓ Created .env.example")
    print("  Remember to create .env file with your actual API key")
    return True

def main():
    """Main setup function"""
    print("=" * 60)
    print("STUDY NOTE GENERATOR - SETUP")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Create directory structure
    if not create_directory_structure():
        return False
    
    # Create requirements.txt
    if not create_requirements_file():
        return False
    
    # Create .env template
    if not create_env_template():
        return False
    
    # Check LaTeX installation
    check_latex_installation()
    
    # Install dependencies
    print("\n" + "=" * 60)
    print("INSTALLATION COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Get a Gemini API key from: https://makersuite.google.com/app/apikey")
    print("2. Copy .env.example to .env and add your API key")
    print("3. Install dependencies: pip install -r requirements.txt")
    print("4. Run the application: python app.py")
    print("5. Open browser to: http://localhost:5000")
    print("\nFor PDF compilation, install LaTeX:")
    print("  - Windows: MiKTeX (https://miktex.org)")
    print("  - Mac: MacTeX (https://www.tug.org/mactex)")
    print("  - Linux: sudo apt install texlive-latex-extra")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)