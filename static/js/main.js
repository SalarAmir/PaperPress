class StudyNoteApp {
    constructor() {
        this.currentFile = null;
        this.currentJobId = null;
        this.apiBaseUrl = window.location.origin;
        
        this.initElements();
        this.bindEvents();
        this.checkHealth();
    }
    
    initElements() {
        this.elements = {
            uploadArea: document.getElementById('uploadArea'),
            fileInput: document.getElementById('fileInput'),
            processBtn: document.getElementById('processBtn'),
            resultsSection: document.getElementById('results'),
            loadingSection: document.getElementById('loading'),
            statusElement: document.getElementById('status'),
            previewContent: document.getElementById('previewContent'),
            downloadLatexBtn: document.getElementById('downloadLatexBtn'),
            downloadPdfBtn: document.getElementById('downloadPdfBtn'),
            compileBtn: document.getElementById('compileBtn'),
            noteType: document.getElementById('noteType'),
            includeQuestions: document.getElementById('includeQuestions'),
            compileDirectly: document.getElementById('compileDirectly'),
            apiStatus: document.getElementById('apiStatus'),
            fileInfo: document.getElementById('fileInfo'),
            progressBar: document.getElementById('progressBar'),
            fileName: document.getElementById('fileName'),
            fileSize: document.getElementById('fileSize'),
            filePages: document.getElementById('filePages')
        };
    }
    
    bindEvents() {
        // File input events
        this.elements.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        this.elements.uploadArea.addEventListener('click', () => this.elements.fileInput.click());
        
        // Drag and drop
        this.setupDragAndDrop();
        
        // Process button
        this.elements.processBtn.addEventListener('click', () => this.processFile());
        
        // Download buttons
        this.elements.downloadLatexBtn?.addEventListener('click', (e) => {
            e.preventDefault();
            this.downloadFile('latex');
        });
        
        this.elements.downloadPdfBtn?.addEventListener('click', (e) => {
            e.preventDefault();
            this.downloadFile('pdf');
        });
        
        this.elements.compileBtn?.addEventListener('click', () => this.compileExisting());
    }
    
    setupDragAndDrop() {
        const uploadArea = this.elements.uploadArea;
        
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, this.preventDefaults, false);
        });
        
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => this.highlightArea(true), false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => this.highlightArea(false), false);
        });
        
        uploadArea.addEventListener('drop', (e) => this.handleDrop(e), false);
    }
    
    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    highlightArea(highlight) {
        this.elements.uploadArea.classList.toggle('dragover', highlight);
    }
    
    handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            this.handleFiles(files[0]);
        }
    }
    
    handleFileSelect(e) {
        if (e.target.files.length > 0) {
            this.handleFiles(e.target.files[0]);
        }
    }
    
    async handleFiles(file) {
        this.currentFile = file;
        
        // Update UI
        this.elements.processBtn.disabled = false;
        this.elements.fileName.textContent = file.name;
        this.elements.fileSize.textContent = this.formatFileSize(file.size);
        
        // Show file info
        this.elements.fileInfo.classList.remove('d-none');
        
        // Update progress bar for visual feedback
        this.updateProgress(10);
        
        this.showStatus('File ready for processing', 'success');
    }
    
    async processFile() {
        if (!this.currentFile) return;
        
        const formData = new FormData();
        formData.append('file', this.currentFile);
        formData.append('note_type', this.elements.noteType.value);
        formData.append('include_questions', this.elements.includeQuestions.checked);
        formData.append('compile_pdf', this.elements.compileDirectly.checked);
        
        this.showLoading(true);
        this.hideResults();
        this.updateProgress(30);
        
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/process`, {
                method: 'POST',
                body: formData
            });
            
            this.updateProgress(70);
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                this.updateProgress(100);
                this.handleSuccess(result);
            } else {
                this.showStatus(`Error: ${result.error || 'Unknown error'}`, 'danger');
            }
        } catch (error) {
            this.showStatus(`Network error: ${error.message}`, 'danger');
        } finally {
            this.showLoading(false);
            setTimeout(() => this.updateProgress(0), 1000);
        }
    }
    
    handleSuccess(result) {
        // Update preview
        this.elements.previewContent.textContent = result.preview;
        
        // Update download links
        if (result.latex_url) {
            this.elements.downloadLatexBtn.href = result.latex_url;
            this.elements.downloadLatexBtn.classList.remove('d-none');
        }
        
        if (result.pdf_url) {
            this.elements.downloadPdfBtn.href = result.pdf_url;
            this.elements.downloadPdfBtn.classList.remove('d-none');
            this.elements.compileBtn.classList.add('d-none');
        } else {
            this.elements.compileBtn.classList.remove('d-none');
        }
        
        // Show results section
        this.showResults();
        
        // Show success message
        this.showStatus('Study notes generated successfully!', 'success');
        
        // Store current filename for later compilation
        this.currentJobId = result.filename;
    }
    
    async compileExisting() {
        if (!this.currentJobId) return;
        
        this.showStatus('Compiling LaTeX to PDF...', 'info');
        
        try {
            const response = await fetch(
                `${this.apiBaseUrl}/api/compile/${this.currentJobId}.tex`
            );
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                // Update PDF download link
                this.elements.downloadPdfBtn.href = result.pdf_url;
                this.elements.downloadPdfBtn.classList.remove('d-none');
                this.elements.compileBtn.classList.add('d-none');
                
                this.showStatus('PDF compiled successfully!', 'success');
            } else {
                this.showStatus(`Compilation failed: ${result.error}`, 'danger');
            }
        } catch (error) {
            this.showStatus(`Compilation error: ${error.message}`, 'danger');
        }
    }
    
    async checkHealth() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/health`);
            const result = await response.json();
            
            if (response.ok) {
                this.elements.apiStatus.className = 'status-badge status-online';
                this.elements.apiStatus.textContent = 'API Online';
                
                if (result.latex_available) {
                    this.elements.compileDirectly.disabled = false;
                }
            } else {
                this.elements.apiStatus.className = 'status-badge status-offline';
                this.elements.apiStatus.textContent = 'API Offline';
            }
        } catch (error) {
            this.elements.apiStatus.className = 'status-badge status-offline';
            this.elements.apiStatus.textContent = 'API Offline';
        }
    }
    
    downloadFile(type) {
        // Links are already set up, just let them work
        return true;
    }
    
    showLoading(show) {
        this.elements.loadingSection.classList.toggle('d-none', !show);
        this.elements.processBtn.disabled = show;
    }
    
    showResults() {
        this.elements.resultsSection.classList.remove('d-none');
        this.elements.resultsSection.classList.add('slide-in');
    }
    
    hideResults() {
        this.elements.resultsSection.classList.add('d-none');
    }
    
    showStatus(message, type) {
        const statusEl = this.elements.statusElement;
        
        statusEl.textContent = message;
        statusEl.className = `alert alert-${type} alert-dismissible fade show`;
        statusEl.classList.remove('d-none');
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            statusEl.classList.add('d-none');
        }, 5000);
    }
    
    updateProgress(percent) {
        this.elements.progressBar.style.width = `${percent}%`;
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new StudyNoteApp();
});