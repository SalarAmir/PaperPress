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
        
        // Download buttons - let them work as normal links (no need for event listeners)
        
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
        formData.append('use_overleaf', document.getElementById('useOverleaf')?.checked || false);
        
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
        
        // Display helpful tips if provided
        if (result.tips) {
            this.showTips(result.tips);
        }
        
        // Store current filename for later compilation
        this.currentJobId = result.filename;
    }
    
    showTips(tips) {
        // Create tips element if not exists
        const tipsId = 'generationTips';
        let tipsElement = document.getElementById(tipsId);
        
        if (!tipsElement) {
            tipsElement = document.createElement('div');
            tipsElement.id = tipsId;
            // Insert after results section or at the end
            const resultsSection = this.elements.resultsSection;
            if (resultsSection && resultsSection.nextSibling) {
                resultsSection.parentNode.insertBefore(tipsElement, resultsSection.nextSibling);
            } else {
                document.querySelector('.container-main').appendChild(tipsElement);
            }
        }
        
        // Build tips HTML
        let html = '<div class="card mt-4 border-info">';
        html += '<div class="card-header bg-info text-white"><i class="fas fa-lightbulb me-2"></i><strong>💡 Tips for Best Results</strong></div>';
        html += '<div class="card-body">';
        
        if (tips.latex_quality) {
            html += `<p class="mb-2"><strong>LaTeX Quality:</strong> <span class="badge bg-success">${tips.latex_quality}</span></p>`;
        }
        
        if (tips.pdf_quality) {
            html += `<p class="mb-3"><strong>PDF Quality:</strong> <span class="badge bg-warning text-dark">${tips.pdf_quality}</span></p>`;
        }
        
        if (tips.for_professional_output) {
            html += `<h6 class="mt-3 mb-2">For Professional PDF Output:</h6>`;
            html += `<p class="text-muted small">${tips.for_professional_output}</p>`;
        }
        
        if (tips.overleaf_steps && tips.overleaf_steps.length > 0) {
            html += '<h6 class="mt-3 mb-2">How to use Overleaf (Free):</h6>';
            html += '<ol class="small">';
            tips.overleaf_steps.forEach(step => {
                html += `<li>${step}</li>`;
            });
            html += '</ol>';
            html += '<p class="small mt-2"><a href="https://www.overleaf.com" target="_blank" class="btn btn-sm btn-info">Go to Overleaf →</a></p>';
        }
        
        html += '</div></div>';
        
        tipsElement.innerHTML = html;
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