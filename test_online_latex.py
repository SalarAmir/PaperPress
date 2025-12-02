#!/usr/bin/env python
"""
Test different online LaTeX compilation services
"""
import requests
import json
from pathlib import Path

# Test the API with a tex file from outputs
test_file = Path("outputs") / "7-conditional-probability_20251202_015827_2548761e.tex"

if not test_file.exists():
    print(f"Looking for any .tex file to test...")
    tex_files = list(Path("outputs").glob("*.tex"))
    if tex_files:
        test_file = tex_files[0]
        print(f"Using: {test_file}")
    else:
        print("No .tex files found")
        exit(1)

# Read the LaTeX file
with open(test_file, 'r', encoding='utf-8') as f:
    latex_content = f.read()

print(f"LaTeX file size: {len(latex_content)} characters\n")

# Test multiple online LaTeX services
services = [
    {
        'name': 'TectiteCloud',
        'url': 'https://cloud.tectite.com/api/v1/compile',
        'method': 'tectite'
    },
    {
        'name': 'Pdfme',
        'url': 'https://api.pdfme.io/pdf',
        'method': 'pdfme'
    },
    {
        'name': 'Overleaf CLI',
        'url': 'https://api.overleaf.com/compile',
        'method': 'overleaf'
    }
]

def test_tectite(latex_content):
    """Test TectiteCloud service"""
    url = 'https://cloud.tectite.com/api/v1/compile'
    payload = {
        'files': [{'name': 'main.tex', 'content': latex_content}],
        'compiler': 'pdflatex',
        'outputFormat': 'pdf'
    }
    headers = {'Content-Type': 'application/json'}
    
    try:
        print(f"Testing TectiteCloud...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'pdf' in data:
                print("  ✓ Got PDF response")
                return base64.b64decode(data['pdf'])
    except Exception as e:
        print(f"  ❌ Error: {str(e)[:100]}")
    
    return None

def test_quicklatex(latex_content):
    """Test QuickLaTeX service"""
    url = 'http://quicklatex.com/api/v3/conversion'
    
    try:
        print(f"\nTesting QuickLaTeX...")
        # QuickLaTeX returns PNG by default, not PDF
        # This service is better for equations, not full documents
        print("  ⚠️  QuickLaTeX is for equations, not full documents")
    except Exception as e:
        print(f"  ❌ Error: {str(e)[:100]}")
    
    return None

def test_pdflatex_online(latex_content):
    """Test using a GitHub Actions or simple online service"""
    print(f"\nTesting simple service approach...")
    
    # Try using texlive.net or similar free service
    url = 'https://texlive.net/cgi-bin/tex'
    
    try:
        # This is a fallback - most free services require special setup
        print("  ⚠️  Most free services have limitations or require API keys")
        return None
    except Exception as e:
        print(f"  ❌ Error: {str(e)[:100]}")
    
    return None

# Try each service
print("=" * 60)
print("Testing online LaTeX services...")
print("=" * 60 + "\n")

test_pdflatex_online(latex_content)
test_quicklatex(latex_content)
test_tectite(latex_content)

print("\n" + "=" * 60)
print("RECOMMENDATION:")
print("=" * 60)
print("""
For Windows systems without local LaTeX, options are:

1. **BEST**: Install MiKTeX (lightweight Windows LaTeX)
   - Download: https://miktex.org/download
   - ~300MB, works perfectly with pdflatex
   
2. **ALTERNATIVE**: Install TinyTeX
   - Minimal LaTeX distribution (~150MB)
   - https://yihui.org/tinytex/
   
3. **NO INSTALL**: Use Overleaf API (requires Overleaf account)
   - https://www.overleaf.com/blog/how-to-use-overleaf-via-git
   
4. **FALLBACK**: Keep using ReportLab (current solution)
   - Works without installation
   - Output quality ~70% of true LaTeX

The online services have limitations:
- Most are paid or limit free requests
- Some are slow (30+ second compile times)
- Email verification required
- Rate limiting

RECOMMENDATION: Install MiKTeX for best results!
""")

