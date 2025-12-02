import PyPDF2
from typing import Optional, Tuple
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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
        logger.info(f"Starting text extraction from PDF: {pdf_path}")
        
        # Verify file exists
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            logger.error(f"PDF file does not exist: {pdf_path}")
            raise Exception(f"PDF file not found: {pdf_path}")
        
        logger.info(f"PDF file found. Size: {pdf_file.stat().st_size} bytes")
        
        try:
            # Try primary extractor
            logger.debug("Attempting extraction with PyPDF2...")
            text, success = self._extract_with_pypdf2(pdf_path)
            text_length = len(text.strip()) if text else 0
            
            logger.info(f"PyPDF2 extraction result - Success: {success}, Length: {text_length} chars")
            
            if success and text_length > 50:
                logger.info(f"Extraction successful with PyPDF2. Returning {text_length} characters")
                return text
            
            # Try alternative extractors if primary fails
            logger.warning(f"PyPDF2 extraction produced insufficient text ({text_length} chars). Trying alternatives...")
            for extractor_name, extractor_func in self.text_extractors.items():
                if extractor_name == 'pypdf2':
                    continue  # Already tried
                
                logger.debug(f"Trying alternative extractor: {extractor_name}")
                text, success = extractor_func(pdf_path)
                if success:
                    logger.info(f"Extraction successful with {extractor_name}")
                    return text
            
            logger.warning(f"All extractors completed. Final text length: {text_length} chars")
            return text if text else ""
            
        except Exception as e:
            logger.error(f"PDF extraction failed with error: {str(e)}", exc_info=True)
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def _extract_with_pypdf2(self, pdf_path: str) -> Tuple[str, bool]:
        """Extract text using PyPDF2"""
        text = ""
        try:
            logger.debug(f"Opening PDF file: {pdf_path}")
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                page_count = len(reader.pages)
                logger.info(f"PDF loaded. Total pages: {page_count}")
                
                # Check if PDF is encrypted
                if reader.is_encrypted:
                    logger.error("PDF is encrypted and cannot be read")
                    return "PDF is encrypted and cannot be read", False
                
                # Extract text from each page
                logger.info(f"Extracting text from {page_count} pages...")
                extracted_pages = 0
                
                for page_num, page in enumerate(reader.pages, 1):
                    try:
                        page_text = page.extract_text()
                        if page_text and len(page_text.strip()) > 0:
                            text += f"--- Page {page_num} ---\n{page_text}\n\n"
                            extracted_pages += 1
                            logger.debug(f"Page {page_num}: Extracted {len(page_text)} characters")
                        else:
                            logger.debug(f"Page {page_num}: No text found")
                    except Exception as page_error:
                        logger.warning(f"Error extracting from page {page_num}: {page_error}")
                
                total_length = len(text.strip())
                logger.info(f"Extraction complete. Pages with text: {extracted_pages}/{page_count}. Total length: {total_length} characters")
                
                return text, total_length > 0
                
        except Exception as e:
            logger.error(f"PyPDF2 extraction error: {str(e)}", exc_info=True)
            return f"Extraction error: {str(e)}", False
    
    def get_metadata(self, pdf_path: str) -> dict:
        """Extract PDF metadata"""
        logger.info(f"Extracting metadata from: {pdf_path}")
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                metadata = reader.metadata
                result = {
                    'title': metadata.get('/Title', 'Unknown') if metadata else 'Unknown',
                    'author': metadata.get('/Author', 'Unknown') if metadata else 'Unknown',
                    'pages': len(reader.pages),
                    'encrypted': reader.is_encrypted
                }
                logger.info(f"Metadata extracted: {result}")
                return result
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}", exc_info=True)
            return {}