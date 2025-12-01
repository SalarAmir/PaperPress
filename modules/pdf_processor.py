import PyPDF2
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Handles PDF text extraction"""
    
    def __init__(self):
        self.text_extractors = {
            'pypdf2': self._extract_with_pypdf2,
            # Add more extractors here if needed
        }
    
    def extract_text(self, pdf_path: str) -> str:
        """
        Extract text from PDF file
        Returns: Extracted text as string
        """
        try:
            # Try primary extractor
            text, success = self._extract_with_pypdf2(pdf_path)
            
            if success and len(text.strip()) > 50:
                return text
            
            # Try alternative extractors if primary fails
            for extractor_name, extractor_func in self.text_extractors.items():
                if extractor_name == 'pypdf2':
                    continue  # Already tried
                
                text, success = extractor_func(pdf_path)
                if success:
                    return text
            
            return text if text else ""
            
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def _extract_with_pypdf2(self, pdf_path: str) -> Tuple[str, bool]:
        """Extract text using PyPDF2"""
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                # Check if PDF is encrypted
                if reader.is_encrypted:
                    return "PDF is encrypted and cannot be read", False
                
                # Extract text from each page
                for page_num, page in enumerate(reader.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        text += f"--- Page {page_num} ---\n{page_text}\n\n"
                
                return text, len(text.strip()) > 0
                
        except Exception as e:
            logger.error(f"PyPDF2 extraction error: {e}")
            return f"Extraction error: {str(e)}", False
    
    def get_metadata(self, pdf_path: str) -> dict:
        """Extract PDF metadata"""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                metadata = reader.metadata
                return {
                    'title': metadata.get('/Title', 'Unknown'),
                    'author': metadata.get('/Author', 'Unknown'),
                    'pages': len(reader.pages),
                    'encrypted': reader.is_encrypted
                }
        except:
            return {}