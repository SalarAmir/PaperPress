from flask import Flask, render_template, request, jsonify, send_file
from config import Config
from modules.pdf_processor import PDFProcessor
from modules.ai_generator import AIGenerator
from modules.latex_builder import LatexBuilder
from utils.helpers import allowed_file, generate_filename
import os
import tempfile

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
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    options = {
        'note_type': request.form.get('note_type', 'detailed'),
        'include_questions': request.form.get('include_questions', 'true') == 'true',
        'compile_pdf': request.form.get('compile_pdf', 'false') == 'true'
    }
    
    if not file or file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only PDF files are allowed'}), 400
    
    try:
        # Generate unique filenames
        base_name = generate_filename(file.filename)
        
        # 1. Save uploaded file temporarily
        temp_path = app.config['UPLOAD_FOLDER'] / f"{base_name}_upload.pdf"
        file.save(temp_path)
        
        # 2. Extract text from PDF
        text = pdf_processor.extract_text(temp_path)
        
        if not text or len(text.strip()) < 100:
            return jsonify({'error': 'Insufficient text found in PDF'}), 400
        
        # 3. Generate study materials using AI
        latex_content = ai_generator.generate_study_materials(
            text=text,
            note_type=options['note_type'],
            include_questions=options['include_questions']
        )
        
        # 4. Build LaTeX document
        tex_path = latex_builder.create_latex_file(
            content=latex_content,
            filename=base_name,
            title=f"Study Notes: {file.filename}"
        )
        
        # 5. Optionally compile to PDF
        pdf_path = None
        if options['compile_pdf']:
            pdf_path = latex_builder.compile_to_pdf(tex_path)
        
        # Clean up temporary upload
        temp_path.unlink(missing_ok=True)
        
        # Prepare response
        response = {
            'success': True,
            'filename': base_name,
            'latex_url': f'/api/download/{base_name}.tex',
            'preview': latex_content[:1000]  # Preview first 1000 chars
        }
        
        if pdf_path and pdf_path.exists():
            response['pdf_url'] = f'/api/download/{base_name}.pdf'
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<filename>')
def download_file(filename):
    """Download generated files"""
    file_path = app.config['OUTPUT_FOLDER'] / filename
    
    if not file_path.exists():
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(
        file_path,
        as_attachment=True,
        download_name=filename
    )

@app.route('/api/compile/<filename>')
def compile_tex(filename):
    """Compile existing LaTeX file to PDF"""
    tex_path = app.config['OUTPUT_FOLDER'] / filename
    
    if not tex_path.exists():
        return jsonify({'error': 'LaTeX file not found'}), 404
    
    try:
        pdf_path = latex_builder.compile_to_pdf(tex_path)
        
        if pdf_path.exists():
            return jsonify({
                'success': True,
                'pdf_url': f'/api/download/{pdf_path.name}'
            })
        else:
            return jsonify({'error': 'PDF compilation failed'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'gemini_configured': bool(app.config['GEMINI_API_KEY']),
        'latex_available': latex_builder.check_latex_available()
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)