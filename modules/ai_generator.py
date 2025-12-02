import os
import logging
import google.generativeai as genai

logger = logging.getLogger(__name__)

class AIGenerator:
    """Handles AI content generation using Gemini (best free tier model)"""
    
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        genai.configure(api_key=api_key)
        
        self.model = self._get_best_model()
        logger.info(f"Using model: {self.model.model_name}")
    
    def _get_best_model(self):
        """Get the best available model for LaTeX generation"""
        # Models ordered by quality for LaTeX/structured output
        models_to_try = [
            'gemini-2.5-pro',         # Best quality - newest pro model
            'gemini-2.5-flash',       # Good alternative with better features
            'gemini-1.5-pro',         # Fallback pro model
            'gemini-1.5-flash',       # Fallback flash model
            'gemini-pro'              # Last resort
        ]
        
        print("=" * 60)
        print("MODEL SELECTION")
        print("=" * 60)
        
        logger.info("Attempting to find best available Gemini model...")
        
        for model_name in models_to_try:
            try:
                logger.debug(f"Trying model: {model_name}")
                print(f"  Attempting: {model_name}...")
                model = genai.GenerativeModel(model_name)
                logger.info(f"Successfully initialized model: {model_name}")
                print(f"  ✓ Successfully initialized: {model_name}")
                print("=" * 60)
                return model
            except Exception as e:
                logger.debug(f"Model {model_name} not available: {str(e)}")
                print(f"  ✗ Not available: {model_name}")
                continue
        
        logger.error("Could not find any available model. Using gemini-pro as fallback...")
        print("  ✗ Fallback to gemini-pro")
        print("=" * 60)
        return genai.GenerativeModel('gemini-pro')
    
    def generate_study_materials(self, text: str, note_type: str = 'detailed', 
                                include_questions: bool = True) -> str:
        """
        Generate study materials from extracted text using Gemini
        Returns: LaTeX formatted content
        """
        logger.info(f"Starting AI generation with note_type='{note_type}', include_questions={include_questions}")
        logger.debug(f"Input text length: {len(text)} characters")
        
        print("\n" + "=" * 60)
        print("AI GENERATION STARTED")
        print("=" * 60)
        print(f"Note Type: {note_type}")
        print(f"Include Questions: {include_questions}")
        print(f"Input Text Length: {len(text)} characters")
        
        # Truncate text if too long
        max_text_length = 15000
        if len(text) > max_text_length:
            logger.warning(f"Input text exceeds {max_text_length} chars. Truncating...")
            text = text[:max_text_length] + "\n\n[Content truncated due to length]"
            print(f"⚠ Input truncated to {max_text_length} characters")
        
        prompt = self._build_prompt(text, note_type, include_questions)
        logger.debug(f"Built prompt. Length: {len(prompt)} characters")
        print(f"Prompt Length: {len(prompt)} characters")
        
        try:
            logger.info("Sending request to Gemini API...")
            print("\n📤 Sending request to Gemini API...")
            
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.7,
                    'top_p': 0.8,
                    'top_k': 40,
                    'max_output_tokens': 4096,
                }
            )
            
            logger.info(f"Gemini response received")
            
            # Handle response safely
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts and len(candidate.content.parts) > 0:
                    raw_output = candidate.content.parts[0].text
                else:
                    raise Exception("Empty response from Gemini")
            else:
                raise Exception("No candidates in Gemini response")
            
            print(f"📥 Response received!")
            print(f"Raw Response Length: {len(raw_output)} characters")
            print("\n" + "-" * 60)
            print("RAW LATEX OUTPUT FROM AI:")
            print("-" * 60)
            print(raw_output)
            print("-" * 60)
            
            cleaned_response = self._clean_latex_response(raw_output)
            
            print("\n" + "-" * 60)
            print("CLEANED LATEX OUTPUT:")
            print("-" * 60)
            print(cleaned_response)
            print("-" * 60)
            print("=" * 60)
            print("AI GENERATION COMPLETED")
            print("=" * 60 + "\n")
            
            return cleaned_response
            
        except Exception as e:
            logger.error(f"AI generation failed: {str(e)}", exc_info=True)
            print(f"\n❌ AI GENERATION FAILED!")
            print(f"Error: {str(e)}")
            print("=" * 60 + "\n")
            raise Exception(f"AI generation failed: {str(e)}")
    
    def _build_prompt(self, text: str, note_type: str, include_questions: bool) -> str:
        """Build the prompt for the AI"""
        logger.debug(f"Building prompt for note_type='{note_type}'")
        
        prompt_templates = {
            'detailed': """IMPORTANT: Generate ONLY the content that goes INSIDE the document body (no \\documentclass, \\usepackage, \\begin{document}, or \\end{document} commands).

DOCUMENT STRUCTURE:

\\section{Main Topic}
Introduction and overview.

\\subsection{Key Concept 1}
Detailed explanation.

\\begin{definition}
Important definition for this concept.
\\end{definition}

\\begin{examtip}
Examiner tip or warning about common mistakes.
\\end{examtip}

Create comparison tables:
\\begin{center}
\\begin{tabular}{l l l}
\\toprule
\\textbf{Feature} & \\textbf{Property A} & \\textbf{Property B} \\\\
\\midrule
Data 1 & Value & Value \\\\
Data 2 & Value & Value \\\\
\\bottomrule
\\end{tabular}
\\end{center}

\\subsection{Key Concept 2}
More detailed content with \\textbf{bold} and \\textit{italic} text.

\\section{Practice Questions}

\\subsection{Conceptual Questions}
\\begin{enumerate}
\\item \\textbf{(3 Marks)} Question 1
\\item \\textbf{(4 Marks)} Question 2
\\item \\textbf{(3 Marks)} Question 3
\\item \\textbf{(4 Marks)} Question 4
\\item \\textbf{(5 Marks)} Question 5
\\end{enumerate}

\\subsection{Multiple Choice Questions}
\\begin{enumerate}
\\item Question 1
\\\\(a) Option A
\\\\(b) Option B
\\\\(c) Correct Answer
\\\\(d) Option D
\\\\\\textbf{Correct Answer: c)}

\\item Question 2
\\\\(a) Option
\\\\(b) Correct Answer
\\\\(c) Option
\\\\(d) Option
\\\\\\textbf{Correct Answer: b)}

\\item Question 3
\\\\(a) Option
\\\\(b) Option
\\\\(c) Correct Answer
\\\\(d) Option
\\\\\\textbf{Correct Answer: c)}

\\item Question 4
\\\\(a) Option
\\\\(b) Option
\\\\(c) Option
\\\\(d) Correct Answer
\\\\\\textbf{Correct Answer: d)}

\\item Question 5
\\\\(a) Correct Answer
\\\\(b) Option
\\\\(c) Option
\\\\(d) Option
\\\\\\textbf{Correct Answer: a)}
\\end{enumerate}

FORMATTING RULES:
- NO \\documentclass, \\usepackage, \\begin{document}, or \\end{document}
- Use \\textbf{} for bold, \\textit{} for italics
- Use \\definition and \\examtip for colored boxes
- Use \\toprule, \\midrule, \\bottomrule for tables
- All LaTeX properly closed and balanced
- Proper spacing between sections

OUTPUT ONLY LaTeX content. Begin with \\section and end with the MCQ section.""",
            
            'concise': """IMPORTANT: Generate ONLY content body (no \\documentclass or \\begin{document}).

\\section{Topic}
Brief introduction.

\\subsection{Key Concept}
Concise explanation.

\\begin{definition}
Essential definition.
\\end{definition}

\\begin{examtip}
Quick revision tip.
\\end{examtip}

\\begin{center}
\\begin{tabular}{l l}
\\toprule
\\textbf{Item} & \\textbf{Details} \\\\
\\midrule
Concept A & Details \\\\
Concept B & Details \\\\
\\bottomrule
\\end{tabular}
\\end{center}

\\section{Quick Practice}
3-5 quick test questions.

OUTPUT ONLY LaTeX content.""",
            
            'outline': """IMPORTANT: Generate ONLY content body (no \\documentclass or \\begin{document}).

\\section{Topic}

\\subsection{Concept 1}
\\begin{itemize}
\\item \\textbf{Key point 1}
\\item \\textbf{Key point 2}
\\end{itemize}

\\subsection{Concept 2}
\\begin{itemize}
\\item \\textbf{Key point 1}
\\item \\textbf{Key point 2}
\\end{itemize}

\\section{Summary}
\\begin{center}
\\begin{tabular}{l l l}
\\toprule
\\textbf{Concept} & \\textbf{Definition} & \\textbf{Example} \\\\
\\midrule
Concept A & Definition & Example \\\\
Concept B & Definition & Example \\\\
\\bottomrule
\\end{tabular}
\\end{center}

OUTPUT ONLY LaTeX content."""
        }
        
        if note_type not in prompt_templates:
            logger.warning(f"Unknown note_type '{note_type}'. Using default 'detailed'")
            note_type = 'detailed'
        
        template = prompt_templates[note_type]
        
        logger.debug(f"Template selected: {note_type}")
        
        try:
            prompt = f"""{template}

CONTENT TO ANALYZE:
{text}

BEGIN OUTPUT:"""
            logger.debug(f"Prompt built successfully. Length: {len(prompt)} characters")
            return prompt
        except Exception as e:
            logger.error(f"Error building prompt: {str(e)}", exc_info=True)
            raise
    
    def _clean_latex_response(self, text: str) -> str:
        """Clean and validate LaTeX response"""
        logger.debug("Cleaning LaTeX response...")
        
        # Remove markdown code blocks if present
        if '```latex' in text:
            logger.debug("Found ```latex code block. Extracting LaTeX content...")
            text = text.split('```latex')[1].split('```')[0]
        elif '```' in text:
            logger.debug("Found ``` code block. Extracting content...")
            text = text.split('```')[1].split('```')[0]
        
        # Remove any accidental \documentclass or \begin{document} commands
        if '\\documentclass' in text:
            logger.debug("Removing accidental \\documentclass command...")
            section_pos = text.find('\\section')
            if section_pos != -1:
                text = text[section_pos:]
            else:
                begin_pos = text.find('\\begin{document}')
                if begin_pos != -1:
                    text = text[begin_pos + 16:]
        
        # Remove any \end{document} commands
        if '\\end{document}' in text:
            logger.debug("Removing \\end{document} marker...")
            text = text.split('\\end{document}')[0]
        
        # Remove \begin{document} if it exists
        text = text.replace('\\begin{document}', '')
        
        # Ensure it starts with valid LaTeX
        text = text.strip()
        if not text.startswith('\\'):
            logger.debug("Response doesn't start with LaTeX command. Adding section header...")
            text = '\\section*{Content}\n' + text
        
        logger.debug(f"LaTeX response cleaned. Final length: {len(text)} characters")
        return text.strip()
