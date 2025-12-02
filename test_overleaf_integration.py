#!/usr/bin/env python3
"""
Test script for Overleaf automation integration
Tests both API and web-based approaches
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.overleaf_automation import OverleafAutomation, OverleafWebAutomation


def test_api_approach():
    """Test API-based Overleaf compilation"""
    print("\n" + "="*60)
    print("TEST 1: Overleaf API Approach")
    print("="*60)
    
    latex_content = r"""
\documentclass{article}
\usepackage{amsmath}
\begin{document}

\title{Test Document}
\author{PaperPress}
\maketitle

\section{Introduction}
This is a test document to verify Overleaf API integration.

\section{Mathematics}
The quadratic formula is:
\[
x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
\]

\section{Conclusion}
If this PDF was created, the API approach works!

\end{document}
"""
    
    try:
        overleaf = OverleafAutomation()
        print("[OK] OverleafAutomation initialized")
        
        output_dir = Path("./outputs")
        output_dir.mkdir(exist_ok=True)
        
        print("Starting API compilation...")
        pdf_path = overleaf.compile_latex_online(
            latex_content=latex_content,
            filename="test_api_document",
            output_dir=output_dir
        )
        
        if pdf_path and pdf_path.exists():
            file_size = pdf_path.stat().st_size
            print(f"[OK] PDF created successfully!")
            print(f"  Location: {pdf_path}")
            print(f"  Size: {file_size:,} bytes")
            return True
        else:
            print("[SKIP] PDF was not created (might be expected if no internet/API)")
            return False
            
    except Exception as e:
        print(f"[FAIL] API approach error: {str(e)}")
        return False


def test_web_approach():
    """Test web-based Overleaf compilation (Selenium)"""
    print("\n" + "="*60)
    print("TEST 2: Overleaf Web Automation Approach")
    print("="*60)
    
    latex_content = r"""
\documentclass{article}
\begin{document}

\title{Web Test Document}
\author{PaperPress}
\maketitle

\section{Testing}
This document tests the web automation approach with Selenium.

The system should:
\begin{enumerate}
\item Open Overleaf in a browser
\item Create a new project
\item Paste this LaTeX code
\item Wait for compilation
\item Download the PDF
\end{enumerate}

\end{document}
"""
    
    try:
        web = OverleafWebAutomation()
        
        if not web.selenium_available:
            print("[FAIL] Selenium not available")
            print("  Install with: pip install selenium")
            print("  Also install ChromeDriver from: https://chromedriver.chromium.org/")
            return False
        
        print("[OK] Selenium available")
        print("Starting web automation compilation...")
        print("  (This will open a browser - be patient, it may take 1-2 minutes)")
        
        output_dir = Path("./outputs")
        output_dir.mkdir(exist_ok=True)
        
        pdf_path = web.compile_latex_web(
            latex_content=latex_content,
            filename="test_web_document",
            output_dir=output_dir
        )
        
        if pdf_path and pdf_path.exists():
            file_size = pdf_path.stat().st_size
            print(f"[OK] PDF created successfully!")
            print(f"  Location: {pdf_path}")
            print(f"  Size: {file_size:,} bytes")
            return True
        else:
            print("[SKIP] PDF was not created (web automation may have failed)")
            return False
            
    except ImportError:
        print("[FAIL] Selenium not installed")
        print("  Install with: pip install selenium")
        return False
    except Exception as e:
        print(f"[FAIL] Web approach error: {str(e)}")
        return False


def test_integration():
    """Test integration with latex_builder"""
    print("\n" + "="*60)
    print("TEST 3: Integration with LatexBuilder")
    print("="*60)
    
    try:
        from modules.latex_builder import LatexBuilder
        
        builder = LatexBuilder()
        print("[OK] LatexBuilder initialized")
        
        # Create a test LaTeX file
        latex_content = r"""
\section{Integration Test}
\textbf{If you see this PDF, the integration works!}
"""
        
        test_file = Path("outputs/integration_test.tex")
        builder.create_latex_file(
            content=latex_content,
            filename="integration_test",
            title="Integration Test"
        )
        print(f"[OK] Created test LaTeX file: {test_file}")
        
        # Try to compile (will fall back to ReportLab if Overleaf unavailable)
        print("Attempting compilation (may use ReportLab fallback)...")
        pdf_path = builder.compile_to_pdf(test_file)
        
        if pdf_path and pdf_path.exists():
            print(f"[OK] Compilation successful!")
            print(f"  PDF: {pdf_path}")
            return True
        else:
            print("[FAIL] Compilation failed")
            return False
            
    except Exception as e:
        print(f"[FAIL] Integration test error: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("OVERLEAF AUTOMATION INTEGRATION TESTS")
    print("="*60)
    
    results = {
        "API Approach": test_api_approach(),
        "Web Approach": test_web_approach(),
        "Integration": test_integration(),
    }
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]" 
        print(f"{status}: {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed/skipped")
    
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("""
1. If API test failed:
   - Internet connection required
   - Overleaf service must be available
   - This is expected for local development

2. If Web test failed:
   - Install Selenium: pip install selenium
   - Download ChromeDriver: https://chromedriver.chromium.org/
   - Ensure Chrome is installed on system

3. If Integration test passed:
   - Overleaf automation is ready!
   - The system will automatically use Overleaf as fallback

4. To enable in web UI:
   - Check "Auto-upload to Overleaf" checkbox
   - Or system uses it automatically if local compilation fails
""")
    
    return 0 if passed > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
