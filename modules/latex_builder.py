import subprocess
from pathlib import Path
import shutil
import tempfile
import os
from typing import Optional
import logging
import re
from modules.overleaf_automation import OverleafAutomation

logger = logging.getLogger(__name__)

class LatexBuilder:
    """Handles LaTeX document creation and compilation"""
    
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path('outputs')
        self.output_dir.mkdir(exist_ok=True)
        
        # LaTeX document template - use $TITLE$ and $CONTENT$ placeholders to avoid conflicts with LaTeX braces
        self.latex_template = r"""\documentclass[a4paper,12pt]{article}
\usepackage[utf8]{inputenc}
\usepackage{geometry}
\geometry{margin=1in}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{graphicx}
\usepackage{xcolor}
\usepackage{tcolorbox}
\usepackage{float}
\usepackage{booktabs}
\usepackage{enumitem}
\usepackage{hyperref}
\usepackage{array}
\usepackage{parskip}

% Define professional colors
\definecolor{edexcelBlue}{RGB}{0, 56, 101}
\definecolor{tipGreen}{RGB}{0, 100, 0}
\definecolor{keywordBlue}{RGB}{41, 128, 185}
\definecolor{accentOrange}{RGB}{255, 107, 53}
\definecolor{darkText}{RGB}{44, 62, 80}

% Custom box for Examiner Tips
\newtcolorbox{examtip}{
    colback=tipGreen!10!white,
    colframe=tipGreen,
    title=\textbf{Examiner Tip!},
    fonttitle=\bfseries,
    arc=4pt,
    boxrule=1.5pt
}

% Custom box for Key Definitions
\newtcolorbox{definition}{
    colback=edexcelBlue!10!white,
    colframe=edexcelBlue,
    title=\textbf{Key Definition},
    fonttitle=\bfseries,
    arc=4pt,
    boxrule=1.5pt
}

% Custom box for Important Notes
\newtcolorbox{importnote}{
    colback=accentOrange!10!white,
    colframe=accentOrange,
    title=\textbf{Important Note},
    fonttitle=\bfseries,
    arc=4pt,
    boxrule=1.5pt
}

% List formatting
\setlist[enumerate]{itemsep=6pt, topsep=8pt, leftmargin=*}
\setlist[itemize]{itemsep=4pt, topsep=6pt, leftmargin=*}

% Custom commands
\newcommand{\keyword}[1]{\textbf{\textcolor{keywordBlue}{#1}}}
\newcommand{\important}[1]{\textbf{\textcolor{accentOrange}{#1}}}
\newcommand{\formula}[1]{\fbox{$\displaystyle #1$}}

% Hyperlink colors
\hypersetup{colorlinks=true, linkcolor=edexcelBlue, urlcolor=keywordBlue}

\title{\textbf{$TITLE$}}
\author{Revision Notes}
\date{}

\begin{document}

\maketitle

$CONTENT$

\end{document}"""
    
    def create_latex_file(self, content: str, filename: str, title: str = "Study Notes") -> Path:
        """
        Create a complete LaTeX file from content
        Returns: Path to created .tex file
        """
        logger.info(f"Creating LaTeX file: {filename}")
        
        # Ensure filename has .tex extension
        if not filename.endswith('.tex'):
            filename += '.tex'
        
        tex_path = self.output_dir / filename
        
        # Replace placeholders in template using string replace instead of .format()
        latex_doc = self.latex_template.replace('$TITLE$', title)
        latex_doc = latex_doc.replace('$CONTENT$', content)
        
        logger.debug(f"Template variables replaced. Document length: {len(latex_doc)} characters")
        
        # Write to file
        with open(tex_path, 'w', encoding='utf-8') as f:
            f.write(latex_doc)
        
        logger.info(f"LaTeX file created successfully: {tex_path}")
        return tex_path
    
    def compile_to_pdf(self, tex_path: Path, use_overleaf: bool = False) -> Path:
        """
        Compile LaTeX file to PDF
        PRIMARY OPTION: Overleaf → Local LaTeX → ReportLab fallback
        
        Args:
            tex_path: Path to .tex file
            use_overleaf: Force Overleaf compilation (default True for best quality)
        
        For best results: Uses Overleaf for professional compilation
        Local LaTeX: pdflatex, xelatex, pandoc (if available)
        Fallback: ReportLab (always works, good quality)
        """
        logger.info(f"Starting PDF compilation from: {tex_path}")
        
        if not tex_path.exists():
            logger.error(f"LaTeX file not found: {tex_path}")
            raise FileNotFoundError(f"LaTeX file not found: {tex_path}")
        
        # PRIMARY: Try Overleaf first (best quality, most reliable for web)
        logger.info("TRY 1: Overleaf automated compilation (PRIMARY)...")
        try:
            pdf_path = self._compile_with_overleaf(tex_path)
            if pdf_path and pdf_path.exists():
                logger.info(f"SUCCESS: Overleaf compilation worked! {pdf_path}")
                return pdf_path
        except Exception as e:
            logger.warning(f"Overleaf compilation failed: {str(e)}")
        
        # SECONDARY: Try local pdflatex if available
        if self.check_latex_available():
            logger.info("TRY 2: Local pdflatex compiler (if MiKTeX installed)...")
            try:
                return self._compile_with_pdflatex(tex_path)
            except Exception as e:
                logger.warning(f"pdflatex compilation failed: {str(e)}")
        
        # TRY 3: Try xelatex
        logger.info("TRY 3: xelatex...")
        try:
            return self._compile_with_xelatex(tex_path)
        except Exception as e:
            logger.warning(f"xelatex compilation failed: {str(e)}")
        
        # TRY 4: Try pandoc
        logger.info("TRY 4: pandoc...")
        try:
            return self._compile_with_pandoc(tex_path)
        except Exception as e:
            logger.warning(f"Pandoc compilation failed: {str(e)}")
        
        # FALLBACK: ReportLab (always works)
        logger.warning("All online and local compilers failed. Using ReportLab fallback...")
        logger.info("ReportLab provides good quality PDF (70%).")
        logger.info("For 100% professional quality, install MiKTeX or use Overleaf!")
        return self._compile_with_reportlab(tex_path)
    
    def _compile_with_online_service(self, tex_path: Path) -> Path:
        """
        Compile LaTeX to PDF using online service (TectiteCloud/LatexOnline API)
        This is the best solution for Windows systems with no local LaTeX install
        """
        logger.info("Using online LaTeX compilation service...")
        
        try:
            import requests
        except ImportError:
            logger.warning("requests module not available for online compilation")
            raise RuntimeError("requests module required for online LaTeX compilation")
        
        try:
            # Read the LaTeX file
            with open(tex_path, 'r', encoding='utf-8') as f:
                latex_content = f.read()
            
            logger.debug("Sending LaTeX to online compilation service...")
            
            # Use LatexOnline.cc API (free, no registration)
            # This service compiles LaTeX and returns PDF
            url = "https://latexonline.cc/compile"
            
            files = {
                'file_0': ('main.tex', latex_content)
            }
            
            response = requests.post(url, files=files, timeout=30)
            
            if response.status_code == 200:
                # API returns PDF binary data
                pdf_name = tex_path.stem + '.pdf'
                pdf_path = self.output_dir / pdf_name
                
                with open(pdf_path, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"✓ PDF compiled successfully with online service: {pdf_path}")
                return pdf_path
            else:
                logger.error(f"Online service returned status {response.status_code}")
                logger.debug(f"Response: {response.text}")
                raise RuntimeError(f"Online LaTeX compilation failed with status {response.status_code}")
                
        except requests.exceptions.Timeout:
            logger.warning("Online LaTeX service timeout")
            raise RuntimeError("Online LaTeX service timeout (30s limit)")
        except requests.exceptions.ConnectionError:
            logger.warning("Could not connect to online LaTeX service")
            raise RuntimeError("Could not connect to online LaTeX service (no internet or service down)")
        except Exception as e:
            logger.warning(f"Online service error: {str(e)}")
            raise RuntimeError(f"Online LaTeX compilation failed: {str(e)}")
    
    def _compile_with_xelatex(self, tex_path: Path) -> Path:
        """Compile LaTeX to PDF using xelatex (better Unicode support)"""
        logger.info(f"Compiling with xelatex: {tex_path}")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_tex = Path(temp_dir) / tex_path.name
            shutil.copy(tex_path, temp_tex)
            
            # Run xelatex twice for references
            for i in range(2):
                logger.debug(f"Running xelatex (run {i+1}/2)...")
                result = subprocess.run(
                    [
                        'xelatex',
                        '-interaction=nonstopmode',
                        '-output-directory', temp_dir,
                        str(temp_tex)
                    ],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    logger.error(f"XeLaTeX compilation error (run {i+1}):")
                    logger.error(f"STDERR: {result.stderr}")
                    if i == 0:
                        raise RuntimeError(f"XeLaTeX compilation failed:\n{result.stderr}")
                else:
                    logger.debug(f"XeLaTeX run {i+1} completed successfully")
            
            pdf_name = tex_path.stem + '.pdf'
            pdf_path = self.output_dir / pdf_name
            temp_pdf = Path(temp_dir) / pdf_name
            
            if temp_pdf.exists():
                logger.debug(f"Moving {temp_pdf} to {pdf_path}")
                shutil.move(temp_pdf, pdf_path)
                logger.info(f"PDF compiled with xelatex: {pdf_path}")
                return pdf_path
            else:
                raise RuntimeError("PDF was not generated by xelatex")
    
    def _compile_with_pandoc(self, tex_path: Path) -> Path:
        """Compile LaTeX to PDF using pandoc"""
        logger.info(f"Compiling with pandoc: {tex_path}")
        
        try:
            import pypandoc
        except ImportError:
            logger.warning("pypandoc not available")
            raise RuntimeError("Pandoc not installed. Install with: pip install pypandoc")
        
        try:
            pdf_name = tex_path.stem + '.pdf'
            pdf_path = self.output_dir / pdf_name
            
            logger.debug(f"Converting LaTeX to PDF via pandoc...")
            
            # Read LaTeX content
            with open(tex_path, 'r', encoding='utf-8') as f:
                latex_content = f.read()
            
            # Use pandoc to convert LaTeX to PDF
            output = pypandoc.convert_text(
                latex_content,
                'pdf',
                format='latex',
                outputfile=str(pdf_path),
                extra_args=[
                    '--pdf-engine=pdflatex',
                    '-V', 'geometry:margin=1in',
                    '-V', 'colorlinks=true',
                    '-V', 'urlcolor=blue'
                ]
            )
            
            if pdf_path.exists():
                logger.info(f"PDF compiled with pandoc: {pdf_path}")
                return pdf_path
            else:
                raise RuntimeError("Pandoc did not generate PDF")
                
        except Exception as e:
            logger.error(f"Pandoc compilation failed: {str(e)}")
            raise RuntimeError(f"Pandoc compilation failed: {str(e)}")
    
        """Compile LaTeX to PDF using pdflatex"""
        logger.info(f"Compiling with pdflatex: {tex_path}")
        
        # Create temporary directory for compilation
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_tex = Path(temp_dir) / tex_path.name
            
            # Copy .tex file to temp directory
            logger.debug(f"Copying {tex_path} to {temp_tex}")
            shutil.copy(tex_path, temp_tex)
            
            # Run pdflatex (multiple runs for references)
            for i in range(2):  # Run twice for proper references
                logger.debug(f"Running pdflatex (run {i+1}/2)...")
                result = subprocess.run(
                    [
                        'pdflatex',
                        '-interaction=nonstopmode',
                        '-output-directory', temp_dir,
                        str(temp_tex)
                    ],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    logger.error(f"LaTeX compilation error (run {i+1}):")
                    logger.error(f"STDOUT: {result.stdout}")
                    logger.error(f"STDERR: {result.stderr}")
                    if i == 0:  # Only raise on first run failure
                        raise RuntimeError(f"LaTeX compilation failed:\n{result.stderr}")
                else:
                    logger.debug(f"LaTeX run {i+1} completed successfully")
            
            # Define PDF path
            pdf_name = tex_path.stem + '.pdf'
            pdf_path = self.output_dir / pdf_name
            
            # Move PDF to output directory
            temp_pdf = Path(temp_dir) / pdf_name
            if temp_pdf.exists():
                logger.debug(f"Moving {temp_pdf} to {pdf_path}")
                shutil.move(temp_pdf, pdf_path)
                
                # Clean up auxiliary files
                for aux_file in Path(temp_dir).glob(f"{tex_path.stem}.*"):
                    if aux_file.suffix not in ['.pdf', '.tex']:
                        logger.debug(f"Cleaning up: {aux_file}")
                        aux_file.unlink(missing_ok=True)
                
                logger.info(f"PDF compiled successfully: {pdf_path}")
                return pdf_path
            else:
                logger.error("PDF was not generated despite successful compilation")
                raise RuntimeError("PDF was not generated")
    
    def _compile_with_overleaf(self, tex_path: Path) -> Optional[Path]:
        """
        Compile LaTeX to PDF using automated Overleaf integration
        
        This method attempts to:
        1. Upload LaTeX to Overleaf programmatically
        2. Wait for compilation
        3. Download the compiled PDF
        4. Clean up the project
        """
        logger.info("Starting automated Overleaf compilation...")
        
        try:
            # Read the LaTeX content
            with open(tex_path, 'r', encoding='utf-8') as f:
                latex_content = f.read()
            
            filename = tex_path.stem
            
            # Try online LaTeX compilation services
            logger.debug("Attempting online LaTeX compilation...")
            overleaf = OverleafAutomation()
            pdf_path = overleaf.compile_latex_online(
                latex_content=latex_content,
                filename=filename,
                output_dir=self.output_dir
            )
            
            if pdf_path and pdf_path.exists():
                logger.info(f"Successfully compiled with online LaTeX service: {pdf_path}")
                return pdf_path
            
            logger.warning("Online LaTeX compilation did not produce a PDF")
            return None
            
        except Exception as e:
            logger.error(f"Online LaTeX compilation error: {str(e)}")
            return None
    
    def _compile_with_reportlab(self, tex_path: Path) -> Path:
        """Fallback: Convert LaTeX to professional PDF using ReportLab with colors and styling"""
        logger.info("Using ReportLab to generate professional PDF from LaTeX content")
        
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib.colors import HexColor, Color
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
                KeepTogether
            )
            from reportlab.lib import colors
            from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
        except ImportError:
            logger.error("ReportLab not installed.")
            raise RuntimeError("ReportLab not available. Install with: pip install reportlab")
        
        try:
            # Read LaTeX file
            with open(tex_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract title
            title = "Study Notes"
            title_match = re.search(r'\\title\{([^}]+)\}', content)
            if title_match:
                title = title_match.group(1).strip()
            
            # Extract document body
            body_match = re.search(r'\\begin\{document\}(.*?)\\end\{document\}', content, re.DOTALL)
            if body_match:
                body = body_match.group(1)
            else:
                body = content
            
            # Remove maketitle and tableofcontents
            body = re.sub(r'\\maketitle\s*', '', body)
            body = re.sub(r'\\tableofcontents\s*', '', body)
            
            # Create PDF
            pdf_name = tex_path.stem + '.pdf'
            pdf_path = self.output_dir / pdf_name
            
            logger.debug(f"Creating professional PDF: {pdf_path}")
            doc = SimpleDocTemplate(
                str(pdf_path),
                pagesize=letter,
                topMargin=0.6*inch,
                bottomMargin=0.6*inch,
                leftMargin=0.75*inch,
                rightMargin=0.75*inch
            )
            story = []
            styles = getSampleStyleSheet()
            
            # Define professional color palette
            color_title = HexColor('#1a3a52')  # Dark blue
            color_section = HexColor('#0066cc')  # Bright blue
            color_subsection = HexColor('#2d5a8c')  # Medium blue
            color_accent = HexColor('#ff6b35')  # Orange accent
            color_text = HexColor('#2c3e50')  # Dark gray-blue
            
            # Define custom styles with professional appearance
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=32,
                textColor=color_title,
                spaceAfter=30,
                spaceBefore=0,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold',
                borderColor=color_section,
                borderWidth=2,
                borderPadding=15,
                borderRadius=5
            )
            
            section_style = ParagraphStyle(
                'SectionHead',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.white,
                backColor=color_section,
                spaceAfter=14,
                spaceBefore=20,
                fontName='Helvetica-Bold',
                leftIndent=10,
                rightIndent=10,
                topPadding=8,
                bottomPadding=8
            )
            
            subsection_style = ParagraphStyle(
                'SubsectionHead',
                parent=styles['Heading3'],
                fontSize=13,
                textColor=color_subsection,
                spaceAfter=10,
                spaceBefore=14,
                fontName='Helvetica-Bold',
                leftIndent=18,
                borderLeft=4,
                borderLeftColor=color_accent
            )
            
            body_style = ParagraphStyle(
                'BodyText',
                parent=styles['Normal'],
                fontSize=11,
                alignment=TA_JUSTIFY,
                spaceAfter=12,
                leading=15,
                leftIndent=0,
                textColor=color_text
            )
            
            list_style = ParagraphStyle(
                'ListText',
                parent=styles['Normal'],
                fontSize=10.5,
                spaceAfter=8,
                leftIndent=36,
                leading=13,
                textColor=color_text
            )
            
            question_style = ParagraphStyle(
                'QuestionText',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=6,
                leftIndent=36,
                leading=12,
                textColor=color_subsection,
                fontName='Helvetica-Bold'
            )
            
            # Add title with styling
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Parse LaTeX content
            lines = body.split('\n')
            i = 0
            
            while i < len(lines):
                line = lines[i].strip()
                
                # Skip empty lines but add spacing
                if not line:
                    if len(story) > 0 and not isinstance(story[-1], Spacer):
                        story.append(Spacer(1, 8))
                    i += 1
                    continue
                
                # Page break
                if line == '\\newpage':
                    story.append(PageBreak())
                    i += 1
                    continue
                
                # Section headers with background color
                section_match = re.match(r'\\section(?:\*)?\{([^}]+)\}', line)
                if section_match:
                    section_title = section_match.group(1)
                    # Create a colored box for section
                    section_para = Paragraph(f"<b>{section_title}</b>", section_style)
                    story.append(section_para)
                    story.append(Spacer(1, 8))
                    i += 1
                    continue
                
                # Subsection headers with left border
                subsection_match = re.match(r'\\subsection(?:\*)?\{([^}]+)\}', line)
                if subsection_match:
                    subsection_title = subsection_match.group(1)
                    story.append(Paragraph(subsection_title, subsection_style))
                    story.append(Spacer(1, 6))
                    i += 1
                    continue
                
                # Handle tabular environments (tables)
                if '\\begin{tabular}' in line:
                    logger.debug("Found tabular environment, parsing table...")
                    table_content, end_idx = self._parse_latex_table(lines, i)
                    if table_content:
                        story.append(Spacer(1, 12))
                        story.append(table_content)
                        story.append(Spacer(1, 12))
                    i = end_idx + 1
                    continue
                
                # Handle itemize lists
                if '\\begin{itemize}' in line:
                    logger.debug("Found itemize environment")
                    i += 1
                    while i < len(lines):
                        item_line = lines[i].strip()
                        if '\\end{itemize}' in item_line:
                            i += 1
                            break
                        if item_line.startswith('\\item'):
                            item_text = item_line.replace('\\item', '').strip()
                            item_text = self._format_latex_text(item_text)
                            # Use colored bullet points
                            item_text = f"<color name='#0066cc'>●</color> {item_text}"
                            story.append(Paragraph(item_text, list_style))
                        i += 1
                    story.append(Spacer(1, 8))
                    continue
                
                # Handle enumerate lists
                if '\\begin{enumerate}' in line:
                    logger.debug("Found enumerate environment")
                    item_num = 1
                    i += 1
                    while i < len(lines):
                        item_line = lines[i].strip()
                        if '\\end{enumerate}' in item_line:
                            i += 1
                            break
                        if item_line.startswith('\\item'):
                            item_text = item_line.replace('\\item', '').strip()
                            item_text = self._format_latex_text(item_text)
                            
                            # Check if this is a question (for MCQs/practice questions)
                            if 'answer' in item_text.lower() or 'option' in item_text.lower() or 'mcq' in item_text.lower():
                                item_text = f"<b>{item_num}.</b> {item_text}"
                                story.append(Paragraph(item_text, question_style))
                            else:
                                item_text = f"<b>{item_num}.</b> {item_text}"
                                story.append(Paragraph(item_text, list_style))
                            item_num += 1
                        i += 1
                    story.append(Spacer(1, 8))
                    continue
                
                # Regular paragraph with LaTeX formatting
                if line and not line.startswith('\\'):
                    # Process LaTeX formatting commands
                    formatted_text = self._format_latex_text(line)
                    story.append(Paragraph(formatted_text, body_style))
                    i += 1
                    continue
                
                i += 1
            
            # Build PDF
            logger.debug("Building PDF document...")
            doc.build(story)
            
            logger.info(f"Professional PDF generated with ReportLab: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}", exc_info=True)
            raise RuntimeError(f"PDF generation failed: {str(e)}")
    
    def _parse_latex_table(self, lines: list, start_idx: int) -> tuple:
        """Parse LaTeX tabular environment and convert to ReportLab Table with professional styling"""
        try:
            from reportlab.platypus import Table, TableStyle
            from reportlab.lib import colors
            from reportlab.lib.colors import HexColor
        except ImportError:
            return None, start_idx
        
        # Find table structure
        table_data = []
        col_format = None
        i = start_idx
        
        # Find column format
        tabular_match = re.search(r'\\begin\{tabular\}\{([^}]+)\}', lines[i])
        if tabular_match:
            col_format = tabular_match.group(1)
        
        i += 1
        current_row = []
        
        while i < len(lines):
            line = lines[i].strip()
            
            if '\\end{tabular}' in line:
                if current_row:
                    table_data.append(current_row)
                break
            
            # Split by & for columns
            if line and not line.startswith('%'):
                parts = re.split(r'&', line)
                row = []
                for part in parts:
                    part = part.strip()
                    part = re.sub(r'\\hline', '', part)
                    part = re.sub(r'\\\\', '', part)
                    part = part.replace('\\textbf{', '<b>').replace('}', '</b>')
                    part = part.replace('\\textit{', '<i>').replace('</i>', '</i>')
                    part = re.sub(r'\\cellcolor\{[^}]+\}', '', part)
                    if part:
                        row.append(part)
                
                if row:
                    if '\\\\' in line or i == len(lines) - 1:
                        # End of row
                        current_row.extend(row)
                        table_data.append(current_row)
                        current_row = []
                    else:
                        current_row.extend(row)
            
            i += 1
        
        if not table_data:
            return None, i
        
        # Determine number of columns
        num_cols = max(len(row) for row in table_data) if table_data else 1
        
        # Create ReportLab table
        try:
            table = Table(table_data, colWidths=[1.3*inch] * num_cols if table_data else [])
            
            # Professional color scheme for tables
            header_bg = HexColor('#0066cc')  # Blue
            alt_row_color1 = HexColor('#f0f5ff')  # Light blue
            alt_row_color2 = HexColor('#ffffff')  # White
            border_color = HexColor('#2d5a8c')  # Dark blue
            
            # Style table
            style_commands = [
                ('BACKGROUND', (0, 0), (-1, 0), header_bg),  # Header background
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # Header text
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                # Alternating row colors
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [alt_row_color2, alt_row_color1]),
                ('TEXTCOLOR', (0, 1), (-1, -1), HexColor('#2c3e50')),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10.5),
                # Grid styling
                ('GRID', (0, 0), (-1, -1), 1.5, border_color),
                ('PADDING', (0, 0), (-1, -1), 10),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ]
            
            table.setStyle(TableStyle(style_commands))
            return table, i
            
        except Exception as e:
            logger.warning(f"Could not create table: {str(e)}")
            return None, i
    
    def _format_latex_text(self, text: str) -> str:
        """Convert LaTeX formatting to ReportLab/HTML formatting"""
        # Handle bold
        text = re.sub(r'\\textbf\{([^}]+)\}', r'<b>\1</b>', text)
        # Handle italics
        text = re.sub(r'\\textit\{([^}]+)\}', r'<i>\1</i>', text)
        # Handle colored text (simplified - just extract text)
        text = re.sub(r'\\textcolor\{[^}]+\}\{([^}]+)\}', r'\1', text)
        # Remove other LaTeX commands but keep content
        text = re.sub(r'\\[a-zA-Z]+\{', '', text)
        text = text.replace('}', '')
        text = re.sub(r'\\[a-zA-Z]+', '', text)
        # Remove extra spaces and math delimiters
        text = text.replace('$', '')
        text = ' '.join(text.split())
        
        return text if text else ''
    
    def check_latex_available(self) -> bool:
        """Check if LaTeX compiler is available"""
        try:
            result = subprocess.run(
                ['pdflatex', '--version'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def get_available_compilers(self) -> list:
        """Get list of available LaTeX compilers"""
        compilers = ['pdflatex', 'xelatex', 'lualatex']
        available = []
        
        for compiler in compilers:
            try:
                subprocess.run([compiler, '--version'], 
                             capture_output=True, 
                             check=False)
                available.append(compiler)
            except (subprocess.SubprocessError, FileNotFoundError):
                pass
        
        return available