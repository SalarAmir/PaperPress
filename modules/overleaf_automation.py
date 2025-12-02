"""
Overleaf API Integration
Automates uploading LaTeX to Overleaf and downloading compiled PDFs
"""

import requests
import logging
import time
from pathlib import Path
from typing import Optional, Dict, Tuple
import json
import subprocess

logger = logging.getLogger(__name__)


class OverleafAutomation:
    """Handles automated Overleaf compilation"""
    
    def __init__(self):
        self.base_url = "https://www.overleaf.com/api/v0"
        self.session = requests.Session()
        # Add headers to mimic browser request
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.timeout = 60
        self.max_retries = 3
    
    def compile_latex_online(self, latex_content: str, filename: str, output_dir: Path) -> Optional[Path]:
        """
        Compile LaTeX using QuickLaTeX or similar service
        Simpler and more reliable than Overleaf API
        """
        try:
            logger.info(f"Attempting online LaTeX compilation for: {filename}")
            
            # Try QuickLaTeX API (simplified, for equations and documents)
            pdf_path = self._try_quicklatex(latex_content, filename, output_dir)
            if pdf_path:
                return pdf_path
            
            # Try LaTeX Online service
            pdf_path = self._try_latex_online(latex_content, filename, output_dir)
            if pdf_path:
                return pdf_path
            
            logger.warning("No online LaTeX service available")
            return None
            
        except Exception as e:
            logger.error(f"Online compilation error: {str(e)}")
            return None
    
    def _try_quicklatex(self, latex_content: str, filename: str, output_dir: Path) -> Optional[Path]:
        """Try QuickLaTeX API"""
        try:
            logger.debug("Trying QuickLaTeX API...")
            
            url = "https://quicklatex.com/api/v3/numericalAPI"
            
            payload = {
                'formula': latex_content,
                'format': 'pdf',
                'fsize': '50px',
                'mode': '0',
                'cache': '0',
                'user_id': '0'
            }
            
            response = requests.post(url, data=payload, timeout=30)
            
            if response.status_code == 200:
                pdf_path = output_dir / f"{filename}.pdf"
                with open(pdf_path, 'wb') as f:
                    f.write(response.content)
                logger.info(f"QuickLaTeX success: {pdf_path}")
                return pdf_path
                
        except Exception as e:
            logger.debug(f"QuickLaTeX failed: {str(e)}")
            return None
    
    def _try_latex_online(self, latex_content: str, filename: str, output_dir: Path) -> Optional[Path]:
        """Try LaTeX Online service"""
        try:
            logger.debug("Trying LaTeX Online API...")
            
            url = "https://latex.ytotech.com/builds/sync"
            
            payload = {
                'compiler': 'pdflatex',
                'resources': [
                    {
                        'main': True,
                        'filename': 'main.tex',
                        'content': latex_content
                    }
                ]
            }
            
            response = requests.post(url, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                if 'pdf' in result:
                    # PDF is base64 encoded
                    import base64
                    pdf_data = base64.b64decode(result['pdf'])
                    pdf_path = output_dir / f"{filename}.pdf"
                    with open(pdf_path, 'wb') as f:
                        f.write(pdf_data)
                    logger.info(f"LaTeX Online success: {pdf_path}")
                    return pdf_path
                    
        except Exception as e:
            logger.debug(f"LaTeX Online failed: {str(e)}")
            return None
