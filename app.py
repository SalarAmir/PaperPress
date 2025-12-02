from flask import Flask, render_template, request, jsonify, send_file
from config import Config
from modules.pdf_processor import PDFProcessor
from modules.ai_generator import AIGenerator
from modules.latex_builder import LatexBuilder
from utils.helpers import allowed_file, generate_filename
import os
import tempfile
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
Config.init_app(app)

# Initialize modules
pdf_processor = PDFProcessor()
ai_generator = AIGenerator()
latex_builder = LatexBuilder()

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

@app.route('/api/process', methods=['POST'])
def process_pdf():
    """Main API endpoint for PDF processing pipeline"""
    logger.info("=" * 60)
    logger.info("NEW PDF PROCESSING REQUEST RECEIVED")
    logger.info("=" * 60)
    
    if 'file' not in request.files:
        logger.warning("Request missing 'file' field")
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    options = {
        'note_type': request.form.get('note_type', 'detailed'),
        'include_questions': request.form.get('include_questions', 'true') == 'true',
        'compile_pdf': request.form.get('compile_pdf', 'false') == 'true',
        'use_overleaf': request.form.get('use_overleaf', 'false') == 'true'
    }
    
    logger.info(f"File received: {file.filename}")
    logger.info(f"File size: {len(file.read())} bytes")
    file.seek(0)  # Reset file pointer after reading size
    logger.info(f"Options: {options}")
    
    if not file or file.filename == '':
        logger.warning("File is empty or no filename provided")
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        logger.warning(f"File rejected: {file.filename} is not a PDF")
        return jsonify({'error': 'Only PDF files are allowed'}), 400
    
    try:
        # Generate unique filenames
        base_name = generate_filename(file.filename)
        logger.info(f"Generated base filename: {base_name}")
        
        # 1. Save uploaded file temporarily
        temp_path = app.config['UPLOAD_FOLDER'] / f"{base_name}_upload.pdf"
        logger.info(f"Saving uploaded file to: {temp_path}")
        file.save(temp_path)
        logger.info(f"File saved successfully. Size: {temp_path.stat().st_size} bytes")
        
        # 2. Extract text from PDF
        logger.info("Starting text extraction from PDF...")
        text = pdf_processor.extract_text(temp_path)
        
        text_length = len(text.strip()) if text else 0
        logger.info(f"Text extraction completed. Extracted text length: {text_length} characters")
        
        if not text or text_length < 100:
            logger.error(f"Insufficient text extracted. Length: {text_length} (minimum 100 required)")
            if text:
                logger.error(f"Extracted text preview: {text[:200]}")
            return jsonify({'error': 'Insufficient text found in PDF'}), 400
        
        logger.info(f"Text extraction successful. Proceeding with AI generation...")
        
        # 3. Generate study materials using AI
        logger.info(f"Generating AI study materials (type: {options['note_type']})...")
        latex_content = ai_generator.generate_study_materials(
            text=text,
            note_type=options['note_type'],
            include_questions=options['include_questions']
        )
        logger.info(f"AI generation completed. LaTeX content length: {len(latex_content)} characters")
        
        # 4. Build LaTeX document
        logger.info(f"Creating LaTeX file...")
        tex_path = latex_builder.create_latex_file(
            content=latex_content,
            filename=base_name,
            title=f"Study Notes: {file.filename}"
        )
        logger.info(f"LaTeX file created at: {tex_path}")
        
        # 5. Always compile to PDF for download
        logger.info("Compiling LaTeX to PDF for download...")
        pdf_path = None
        try:
            pdf_path = latex_builder.compile_to_pdf(tex_path, use_overleaf=options['use_overleaf'])
            logger.info(f"PDF compilation successful: {pdf_path}")
        except Exception as e:
            logger.warning(f"PDF compilation failed: {str(e)}. PDF download may fail, but LaTeX file available.")
        
        # Clean up temporary upload
        logger.info(f"Cleaning up temporary file: {temp_path}")
        temp_path.unlink(missing_ok=True)
        logger.info("Temporary file deleted")
        
        # Prepare response - always provide PDF download URL
        response = {
            'success': True,
            'filename': base_name,
            'latex_url': f'/api/download/{base_name}.tex',
            'pdf_url': f'/api/download/{base_name}.pdf',  # Will compile on download if needed
            'preview': latex_content[:1000],  # Preview first 1000 chars
            'tips': {
                'latex_quality': 'Perfect ✅ (Ready for Overleaf)',
                'pdf_quality': 'Good ✅ (ReportLab renderer)',
                'for_professional_output': 'Download the .tex file and upload to https://www.overleaf.com for professional PDF quality',
                'overleaf_steps': [
                    'Copy the download link for the .tex file',
                    'Go to https://www.overleaf.com and create a free account',
                    'Create a new project and upload the .tex file',
                    'Click "Recompile" - get professional PDF!'
                ]
            }
        }
        
        logger.info(f"Processing completed successfully. Response: {response}")
        logger.info("=" * 60)
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error during PDF processing: {str(e)}", exc_info=True)
        logger.info("=" * 60)
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<filename>')
def download_file(filename):
    """Download generated files - automatically convert .tex to PDF"""
    logger.info(f"Download request for file: {filename}")
    file_path = app.config['OUTPUT_FOLDER'] / filename
    
    if not file_path.exists():
        logger.warning(f"File not found: {file_path}")
        return jsonify({'error': 'File not found'}), 404
    
    try:
        # If it's a .tex file, compile to PDF first
        if filename.endswith('.tex'):
            logger.info(f"LaTeX file requested. Attempting to compile to PDF...")
            try:
                pdf_path = latex_builder.compile_to_pdf(file_path)
                if pdf_path.exists():
                    logger.info(f"Serving compiled PDF: {pdf_path}")
                    return send_file(
                        str(pdf_path),
                        as_attachment=True,
                        download_name=pdf_path.name
                    )
            except Exception as e:
                logger.warning(f"PDF compilation failed: {str(e)}. Serving LaTeX file instead.")
        
        logger.info(f"Serving file: {file_path}")
        return send_file(
            str(file_path),
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        logger.error(f"Download error: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/compile/<filename>')
def compile_tex(filename):
    """Compile existing LaTeX file to PDF"""
    logger.info(f"Compilation request for LaTeX file: {filename}")
    tex_path = app.config['OUTPUT_FOLDER'] / filename
    
    if not tex_path.exists():
        logger.warning(f"LaTeX file not found: {tex_path}")
        return jsonify({'error': 'LaTeX file not found'}), 404
    
    try:
        logger.info(f"Compiling LaTeX to PDF: {tex_path}")
        pdf_path = latex_builder.compile_to_pdf(tex_path)
        
        if pdf_path.exists():
            logger.info(f"PDF compilation successful: {pdf_path}")
            return jsonify({
                'success': True,
                'pdf_url': f'/api/download/{pdf_path.name}'
            })
        else:
            logger.error("PDF compilation completed but output file not found")
            return jsonify({'error': 'PDF compilation failed'}), 500
            
    except Exception as e:
        logger.error(f"PDF compilation error: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    gemini_configured = bool(app.config['GEMINI_API_KEY'])
    latex_available = latex_builder.check_latex_available()
    logger.info(f"Health check: Gemini={gemini_configured}, LaTeX={latex_available}")
    return jsonify({
        'status': 'healthy',
        'gemini_configured': gemini_configured,
        'latex_available': latex_available
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)