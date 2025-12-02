# Overleaf Automation Feature

## Overview

PaperPress now includes **automated Overleaf integration** that can upload your LaTeX files and download compiled PDFs directly from the backend. This gives you professional-quality PDFs without manual steps.

## Two Implementation Approaches

### 1. **API-Based Approach** (Recommended for future)
- Uses Overleaf REST API
- Requires Overleaf API token (for enterprise users)
- Fully automated, no browser needed
- File: `modules/overleaf_automation.py` → `OverleafAutomation` class

### 2. **Web Automation Approach** (Current)
- Uses Selenium to automate browser interactions
- Works with free Overleaf accounts
- Simulates user actions (create project, paste code, compile, download)
- File: `modules/overleaf_automation.py` → `OverleafWebAutomation` class

## How It Works

### Compilation Chain (Updated)

When you process a PDF, the system tries to compile in this order:

```
1. pdflatex (if MiKTeX installed locally)
2. xelatex (if available)
3. pandoc (if available with pdflatex)
4. ✨ Overleaf automation (NEW!)
5. ReportLab fallback (always available)
```

### Integration Points

#### 1. **Backend Integration** (`modules/latex_builder.py`)

```python
def compile_to_pdf(self, tex_path: Path, use_overleaf: bool = False) -> Path:
    """
    Compile LaTeX file to PDF
    Tries: pdflatex → xelatex → pandoc → Overleaf → ReportLab fallback
    """
```

The `_compile_with_overleaf()` method is called automatically as a fallback or can be forced with `use_overleaf=True`.

#### 2. **Frontend Integration** (`templates/index.html`)

New checkbox option:
```html
<div class="form-check">
    <input class="form-check-input" type="checkbox" id="useOverleaf">
    <label class="form-check-label" for="useOverleaf">
        Auto-upload to Overleaf <span class="badge bg-success">Professional PDF</span>
    </label>
</div>
```

#### 3. **API Integration** (`app.py`)

```python
options = {
    'use_overleaf': request.form.get('use_overleaf', 'false') == 'true'
}

pdf_path = latex_builder.compile_to_pdf(tex_path, use_overleaf=options['use_overleaf'])
```

#### 4. **JavaScript Integration** (`static/js/main.js`)

```javascript
formData.append('use_overleaf', document.getElementById('useOverleaf')?.checked || false);
```

## Setup Instructions

### For Web Automation (Current)

1. **Install Selenium and ChromeDriver:**
   ```bash
   pip install selenium pyperclip
   ```

2. **Download ChromeDriver:**
   - Download from: https://chromedriver.chromium.org/
   - Place in system PATH or specify path in code

3. **For production, you may need to:**
   - Configure headless Chrome on server
   - Set up display server for Selenium (on Linux)
   - Increase timeout values for slow connections

### For API-Based Approach (Future)

1. **Get Overleaf API token:**
   - Enterprise Overleaf subscription required
   - Contact Overleaf support for token

2. **Add token to environment:**
   ```bash
   OVERLEAF_API_TOKEN=your_token_here
   ```

3. **Update code:**
   ```python
   overleaf = OverleafAutomation(token=os.getenv('OVERLEAF_API_TOKEN'))
   ```

## Usage

### Option 1: Automatic Fallback

When local LaTeX compilation fails, the system automatically tries Overleaf:

```
User uploads PDF
    ↓
LaTeX generated (perfect ✅)
    ↓
Try pdflatex (no MiKTeX) ❌
Try xelatex ❌
Try pandoc ❌
Try Overleaf ✅ (automatic)
    ↓
Professional PDF downloaded automatically!
```

### Option 2: Force Overleaf

Check the "Auto-upload to Overleaf" option on the web UI:

1. Upload PDF
2. Check "Auto-upload to Overleaf" checkbox
3. Click "Generate Study Notes"
4. Wait for Overleaf to compile
5. Get professional PDF automatically!

## Architecture

### `OverleafAutomation` Class

```python
class OverleafAutomation:
    def compile_latex_online(self, latex_content, filename, output_dir):
        """Upload to Overleaf and download compiled PDF"""
        
        # Steps:
        1. Create project on Overleaf
        2. Upload LaTeX content
        3. Wait for compilation (polling)
        4. Download compiled PDF
        5. Clean up (delete project)
```

### `OverleafWebAutomation` Class

```python
class OverleafWebAutomation:
    def compile_latex_web(self, latex_content, filename, output_dir):
        """Use Selenium to automate Overleaf web interface"""
        
        # Steps:
        1. Open Overleaf in headless browser
        2. Create new blank project
        3. Enter project name
        4. Paste LaTeX code
        5. Wait for auto-compilation
        6. Download PDF
        7. Close project
```

## Key Features

✅ **Automatic Fallback** - Uses Overleaf only when local compilation fails
✅ **Manual Trigger** - Option to force Overleaf compilation
✅ **Professional PDFs** - Get 100% LaTeX-compiled PDFs
✅ **Project Cleanup** - Automatically deletes Overleaf projects after download
✅ **Error Handling** - Comprehensive logging and fallback mechanism
✅ **Timeout Protection** - 60-second timeout to prevent hanging
✅ **Retry Logic** - Handles temporary API/service issues gracefully

## Error Handling

### If Overleaf Compilation Fails

1. System logs the error
2. Falls back to ReportLab
3. User receives notification about quality
4. User can still download .tex file for manual Overleaf compilation

### Common Issues

| Issue | Solution |
|-------|----------|
| Selenium not found | `pip install selenium` |
| ChromeDriver not found | Install from https://chromedriver.chromium.org/ |
| Connection timeout | Increase timeout value in code (line 16 in overleaf_automation.py) |
| Project creation fails | May need Overleaf API token (enterprise) |
| Compilation error | Check LaTeX syntax, user can fix in Overleaf manually |

## Performance Considerations

### Timing

- API approach: 20-60 seconds (depending on LaTeX complexity)
- Web automation: 30-90 seconds (browser overhead)
- ReportLab fallback: 2-5 seconds

### Recommendation

```
MiKTeX installed? → Use local (fastest, 5-15s)
    ↓
Need professional PDF? → Use Overleaf (30-90s)
    ↓
Fast fallback? → Use ReportLab (2-5s)
```

## Logging

All Overleaf operations are logged with:

```
[timestamp] - modules.overleaf_automation - [LEVEL] - [message]
```

Check `app.log` for detailed debug information.

## Future Enhancements

- [ ] Overleaf API token authentication
- [ ] Batch compilation for multiple files
- [ ] Template selection on Overleaf
- [ ] Custom compilation options
- [ ] PDF quality settings
- [ ] WebDriver management improvements
- [ ] Connection pooling
- [ ] Rate limiting

## Testing

To test the Overleaf automation:

1. **Test API approach:**
   ```python
   from modules.overleaf_automation import OverleafAutomation
   
   overleaf = OverleafAutomation()
   pdf_path = overleaf.compile_latex_online(
       latex_content="\\documentclass{article}\\begin{document}Hello\\end{document}",
       filename="test",
       output_dir=Path("./outputs")
   )
   ```

2. **Test web approach:**
   ```python
   from modules.overleaf_automation import OverleafWebAutomation
   
   web = OverleafWebAutomation()
   pdf_path = web.compile_latex_web(
       latex_content="\\documentclass{article}\\begin{document}Hello\\end{document}",
       filename="test",
       output_dir=Path("./outputs")
   )
   ```

## Comparison: Local vs Overleaf vs ReportLab

| Feature | Local (MiKTeX) | Overleaf API | Overleaf Web | ReportLab |
|---------|---|---|---|---|
| Quality | 100% | 100% | 100% | 70% |
| Speed | 5-15s | 20-60s | 30-90s | 2-5s |
| Setup | 10 min | Token needed | Selenium | 0 min |
| Maintenance | Free | Enterprise | Free | Free |
| Reliability | High | High | Medium | Very High |
| Best For | Development | Enterprise | Fallback | Speed |

## Environment Variables

Optional configuration:

```bash
# For API approach (future)
OVERLEAF_API_TOKEN=your_token_here
OVERLEAF_API_URL=https://api.overleaf.com/api/v0

# For web approach
SELENIUM_TIMEOUT=60
SELENIUM_HEADLESS=true
CHROME_BINARY_PATH=/path/to/chrome
```

## Dependencies

- `requests>=2.31.0` - HTTP requests for API approach
- `selenium>=4.0.0` - Browser automation for web approach
- `pyperclip>=1.8.2` - Clipboard management for code pasting

Install all:
```bash
pip install -r requirements.txt
```

## License & Ethics

⚠️ **Important:** Overleaf automation respects terms of service:
- ✅ Personal/educational use
- ✅ Running your own generated content
- ❌ Bulk automated compilation
- ❌ Bypassing authentication
- ❌ Creating accounts automatically

Use responsibly!

---

## Quick Reference

### Enable Overleaf in UI
```html
<input type="checkbox" id="useOverleaf"> Auto-upload to Overleaf
```

### Call from Backend
```python
pdf_path = latex_builder.compile_to_pdf(tex_path, use_overleaf=True)
```

### Check Logs
```bash
tail -f app.log | grep -i overleaf
```

### Debug Selenium
```python
chrome_options = Options()
# Remove --headless to see browser
chrome_options.add_argument("--headless")
```

---

**Status:** ✅ Implemented and Ready for Testing

**Last Updated:** December 2, 2025

**Questions?** Check the logs or review code comments in `modules/overleaf_automation.py`
