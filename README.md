# 📚 PaperPress - AI Study Note Generator

> Transform lecture PDFs into professionally formatted study materials in seconds!

## 🎯 What is PaperPress?

PaperPress is an intelligent PDF-to-study-notes converter that:

1. **📥 Uploads** your lecture/textbook PDFs
2. **🤖 Analyzes** content using Google Gemini AI
3. **📝 Generates** structured study notes with:
   - Key definitions (highlighted in colored boxes)
   - Examiner tips and important notes
   - Comprehension questions
   - Multiple choice questions
   - Professional tables and formatting
4. **📄 Creates** publication-ready LaTeX and PDF files
5. **⬇️ Downloads** both `.tex` and `.pdf` versions

## ✨ Features

- ✅ **AI-Powered Content Generation** - Gemini 2.5 Pro
- ✅ **Professional LaTeX Templates** - Exam-style formatting
- ✅ **Colored Custom Boxes** - Definition, tips, important notes
- ✅ **Smart Questions** - Auto-generated comprehension & MCQs
- ✅ **Multiple Export Formats** - `.tex` and `.pdf`
- ✅ **Drag-and-Drop Upload** - Easy web interface
- ✅ **Real-time Processing** - See your notes immediately
- ✅ **Offline-Capable** - PDF rendering works without internet

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Gemini API key (free)
- ~500MB disk space

### Installation

```bash
# 1. Clone or download repository
cd PaperPress

# 2. Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate      # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
# Create .env file with:
GEMINI_API_KEY=your_api_key_here
FLASK_ENV=development

# 5. Run the application
python -m flask run

# 6. Open browser
# Go to http://127.0.0.1:5000
```

## 📖 Usage

### Basic Workflow

1. **Open** http://127.0.0.1:5000 in your browser
2. **Drag and drop** a PDF or click to browse
3. **Choose** note type:
   - **Detailed**: Comprehensive notes + questions
   - **Concise**: Quick summary
   - **Outline**: Structured hierarchy
4. **Select** options:
   - Include comprehension questions? ✓
   - Include MCQs? ✓
5. **Click "Process"** and wait 30-60 seconds
6. **Download**:
   - `.tex` - LaTeX source (perfect, editable)
   - `.pdf` - Study material (ready to read)

## 🎨 PDF Quality

### Current Output (ReportLab)
✅ Readable and functional  
✅ Good for quick study notes  
⚠️ Basic formatting (80% quality)

### Professional Output (with MiKTeX)
✅ Identical to Overleaf  
✅ Colored boxes and formatting  
✅ Professional typography  
✅ Perfect for printing/sharing

## 🔧 PDF Compilation Methods

PaperPress tries these methods in order:

1. **pdflatex** (native LaTeX) ← Install MiKTeX to enable
2. **xelatex** (Unicode LaTeX)
3. **pandoc** (universal converter)
4. **ReportLab** (Python PDF lib) ← Currently used fallback

### Upgrade to Professional PDFs

**Option A: Install MiKTeX** (5 minutes) ⭐ RECOMMENDED
```
1. Download: https://miktex.org/download
2. Run installer
3. Accept defaults
4. Restart PaperPress
5. PDFs now professional quality!
```

**Option B: Use Overleaf** (free, online)
```
1. Download .tex file from PaperPress
2. Go to https://www.overleaf.com
3. Create new project and upload .tex
4. Click Recompile
5. Download professional PDF!
```

See `MIKTEX_SETUP.md` for detailed instructions.

## 📚 Output Example

### Input PDF
Chapter from "Introduction to Software Engineering"

### Generated Study Notes Include

**Key Definition Box**
```
SOFTWARE ENGINEERING is defined as a process of analyzing 
user requirements and then designing, building, and testing 
a software application...
```

**Examiner Tip Box**
```
💡 Be careful with cost estimation!
An estimate that is too high decreases chances of winning 
a contract. Too low may cause losing money...
```

**Tables**
```
┌─────────────┬──────────────────┬────────────────┐
│   Feature   │ Direct Costs     │ Indirect Costs │
├─────────────┼──────────────────┼────────────────┤
│ Definition  │ Costs directly   │ Firm overhead  │
│ Examples    │ Personnel, etc   │ Rent, admin    │
└─────────────┴──────────────────┴────────────────┘
```

**Questions**
```
CONCEPTUAL QUESTIONS
1. (3 Marks) Differentiate between "Software" and "Program"
2. (4 Marks) Explain the main drawback of Waterfall model

MULTIPLE CHOICE
1. Which type of software makes source code available?
   (a) Freeware  (b) Shareware  (c) Open-source  (d) Proprietary
```

## 🏗️ Architecture

```
PaperPress/
├── app.py                 # Flask server & routes
├── config.py             # Configuration
├── requirements.txt      # Dependencies
│
├── modules/
│   ├── pdf_processor.py   # PDF text extraction (PyPDF2)
│   ├── ai_generator.py    # AI content generation (Gemini)
│   └── latex_builder.py   # LaTeX & PDF compilation
│
├── utils/
│   └── helpers.py        # Utility functions
│
├── static/
│   ├── css/style.css     # Styling
│   └── js/main.js        # Frontend logic
│
└── templates/
    └── index.html        # Web interface
```

## 📋 Documentation

- **`ENHANCEMENT_SUMMARY.md`** - What was improved (v2.0)
- **`MIKTEX_SETUP.md`** - How to install MiKTeX for professional PDFs
- **`INSTALLATION_GUIDE.md`** - Complete installation guide
- **`PDF_COMPILATION_STATUS.md`** - Technical status report
- **`LATEX_IMPROVEMENTS.md`** - LaTeX template details

## 🔑 API Keys

### Get Free Gemini API Key

1. Go to **https://aistudio.google.com/apikey**
2. Click **"Create API key"**
3. Accept terms
4. Copy the key
5. Add to `.env`:
   ```
   GEMINI_API_KEY=your_key_here
   ```

**Free tier**: 
- 50 requests/day
- 60 requests/minute
- Fast processing

## 🛠️ Troubleshooting

### PDF doesn't process
- Check terminal for error messages
- Ensure PDF has actual text (not scanned image)
- Try with a smaller PDF first

### PDFs are low quality
- **Current**: ReportLab is being used (normal!)
- **Solution**: Install MiKTeX (see `MIKTEX_SETUP.md`)
- **Alternative**: Use Overleaf for professional output

### API limit exceeded
- Wait until next day
- Or get a paid Gemini API plan

### Flask won't start
- Check Python version: `python --version` (need 3.8+)
- Check dependencies: `pip list`
- Check port 5000 is free: `netstat -ano | findstr :5000`

## 📊 Supported Content

✅ **Works great with:**
- University lecture notes
- Textbook chapters
- Research papers
- Technical documentation
- Course materials

❌ **Limited support for:**
- Scanned images (not OCR'd)
- Complex diagrams
- Tables as images
- Handwritten notes

## 🤝 Contributing

Found a bug? Have ideas? 
- Check the issue tracker
- Create descriptive bug reports
- Include terminal output and PDF file

## 📄 License

[Add your license here]

## 🙋 FAQ

**Q: Is Gemini API free?**  
A: Yes! Free tier includes 50 requests/day. Perfect for students!

**Q: Can I use it offline?**  
A: Partially. PDF processing needs internet (Gemini API), but once notes are generated, PDFs can be viewed offline.

**Q: What PDF formats work?**  
A: Text-based PDFs. Scanned images won't work without OCR.

**Q: Can I edit the generated LaTeX?**  
A: Yes! Download the `.tex` file and edit in any text editor, then recompile.

**Q: How accurate are the generated notes?**  
A: Gemini AI generates contextually accurate summaries based on your PDF content. Quality depends on input PDF clarity.

**Q: Can I use other LaTeX compilers?**  
A: Yes! The app supports pdflatex, xelatex, and pandoc. MiKTeX (Windows) is easiest.

**Q: How long does processing take?**  
A: Typically 30-60 seconds per PDF, depending on:
- PDF size
- Internet speed
- Gemini API response time

## 📞 Support

### For Issues:
1. Check the Troubleshooting section
2. Review the documentation files
3. Check terminal output for error messages

### For Feature Requests:
- Describe what you'd like to improve
- Include examples if possible

## 🚀 Future Enhancements

Planned features:
- [ ] OCR support for scanned PDFs
- [ ] Custom LaTeX templates
- [ ] Batch processing
- [ ] Claude/GPT-4 model support
- [ ] Web version (no installation)
- [ ] Mobile app
- [ ] Collaborative editing

## 📈 Performance

Typical processing:
- **Small PDF** (5 pages): 30-40 seconds
- **Medium PDF** (20 pages): 40-60 seconds
- **Large PDF** (50+ pages): 60-120 seconds

Limited by: Gemini API response time (mostly)

## 🎓 Educational Use

Perfect for:
- 👨‍🎓 Students creating study materials
- 👨‍🏫 Teachers generating revision notes
- 📚 Building personal knowledge bases
- 📖 Quick summaries of chapters
- ✏️ Practice question generation

## ✅ Quality Checklist

- [x] PDF text extraction
- [x] AI content generation
- [x] LaTeX file generation
- [x] PDF rendering
- [x] Web interface
- [x] File downloads
- [x] Error handling
- [x] User guidance
- [x] Installation docs
- [x] Troubleshooting guide

## 🎯 Next Steps

1. **Install**: Follow the Quick Start above
2. **Setup API Key**: Get free Gemini key
3. **Test**: Upload a test PDF
4. **Optimize**: Install MiKTeX for professional PDFs (optional)
5. **Share**: Use with classmates/colleagues!

---

**Happy studying!** 📚✨

For detailed guides, see the documentation files included.

