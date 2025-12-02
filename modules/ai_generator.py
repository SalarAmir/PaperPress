import google.generativeai as genai
from typing import Dict, Any
import os
import json
import logging

logger = logging.getLogger(__name__)

class AIGenerator:
    """Handles AI content generation using Gemini"""
    
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        genai.configure(api_key=api_key)
        
        # Try to find an available model
        self.model = self._get_available_model()
        logger.info(f"Using model: {self.model.model_name}")
    
    def _get_available_model(self):
        """Get an available model for content generation"""
        # List of models to try in order of preference
        models_to_try = [
            'gemini-2.0-flash',
            'gemini-1.5-flash',
            'gemini-1.5-pro',
            'gemini-pro'
        ]
        
        logger.info("Attempting to find available model...")
        
        for model_name in models_to_try:
            try:
                logger.debug(f"Trying model: {model_name}")
                model = genai.GenerativeModel(model_name)
                # Test if model works
                logger.info(f"Successfully initialized model: {model_name}")
                return model
            except Exception as e:
                logger.debug(f"Model {model_name} not available: {str(e)}")
                continue
        
        # Fallback: list available models and use the first one
        logger.warning("Preferred models not available. Listing all models...")
        try:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            if available_models:
                model_name = available_models[0].replace('models/', '')
                logger.info(f"Using first available model: {model_name}")
                return genai.GenerativeModel(model_name)
        except Exception as e:
            logger.error(f"Error listing models: {str(e)}")
        
        # Final fallback
        logger.error("Could not find any available model. Using gemini-pro as fallback...")
        return genai.GenerativeModel('gemini-pro')
    
    def generate_study_materials(self, text: str, note_type: str = 'detailed', 
                                include_questions: bool = True) -> str:
        """
        Generate study materials from extracted text
        Returns: LaTeX formatted content
        """
        logger.info(f"Starting AI generation with note_type='{note_type}', include_questions={include_questions}")
        logger.debug(f"Input text length: {len(text)} characters")
        
        # Truncate text if too long (Gemini has token limits)
        max_text_length = 10000  # Adjust based on your needs
        if len(text) > max_text_length:
            logger.warning(f"Input text exceeds {max_text_length} chars. Truncating...")
            text = text[:max_text_length] + "\n\n[Content truncated due to length]"
        
        prompt = self._build_prompt(text, note_type, include_questions)
        logger.debug(f"Built prompt. Length: {len(prompt)} characters")
        
        try:
            logger.info("Sending request to Gemini API...")
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.7,
                    'top_p': 0.8,
                    'top_k': 40,
                    'max_output_tokens': 2048,
                }
            )
            logger.info(f"Gemini response received. Response length: {len(response.text)} characters")
            
            return self._clean_latex_response(response.text)
            
        except Exception as e:
            logger.error(f"AI generation failed: {str(e)}", exc_info=True)
            raise Exception(f"AI generation failed: {str(e)}")
    
    def _build_prompt(self, text: str, note_type: str, include_questions: bool) -> str:
        """Build the prompt for the AI"""
        logger.debug(f"Building prompt for note_type='{note_type}'")
        
        prompt_templates = {
            'detailed': {
                'instructions': """You are an expert tutor and document designer. Generate university-level study notes content for LaTeX.

IMPORTANT: Generate ONLY the content that goes INSIDE the document (no \\documentclass, \\begin{document}, or \\end{document} commands).

CONTENT STRUCTURE:
- \\section{Topic Name} for major topics
- \\subsection{Subtopic Name} for subtopics  
- \\subsubsection{Details} for detailed sections
- \\textbf{key terms} for emphasis
- Use \\textit{italics} for secondary emphasis
- Create AT LEAST 2-3 tables with \\begin{tabular}...\\end{tabular}
- Use colored table cells: \\cellcolor{red!20}, \\cellcolor{blue!20}, \\cellcolor{green!20}
- Include \\textbf{Practical Example:} sections with real-world applications
- Create math equations using $...$ or $$...$$
- Use \\begin{enumerate} and \\begin{itemize} for lists

REQUIRED AT END:
\\section{Practice Questions}

\\subsection{Conceptual Questions (5 questions)}
\\begin{enumerate}
\\item [Question 1 - test deep understanding]
\\item [Question 2 - test deep understanding]
\\item [Question 3 - test deep understanding]
\\item [Question 4 - test deep understanding]
\\item [Question 5 - test deep understanding]
\\end{enumerate}

\\subsection{Multiple Choice Questions (5 MCQs with answers)}
\\begin{enumerate}
\\item [MCQ Question 1]
  \\begin{enumerate}
  \\item a) [Option A]
  \\item b) [Option B]
  \\item c) [Option C]
  \\item d) [Option D]
  \\end{enumerate}
  \\textbf{Answer: [letter]}

\\item [MCQ Question 2]
  \\begin{enumerate}
  \\item a) [Option A]
  \\item b) [Option B]
  \\item c) [Option C]
  \\item d) [Option D]
  \\end{enumerate}
  \\textbf{Answer: [letter]}

[Continue for MCQ 3-5 in same format]

\\end{enumerate}

FORMATTING RULES:
- Use proper LaTeX syntax (all backslashes must be literal \\)
- DO NOT include \\documentclass, \\usepackage, or \\begin/\\end{document}
- Create visually organized content with clear hierarchy
- Include at least 3 colored tables showing key information
- Make tables informative with headers and highlighted cells
- Keep content clear, organized, and university-level appropriate
- Ensure all LaTeX commands are properly closed

OUTPUT ONLY the raw LaTeX content for the document body. Start with \\section and end with the MCQ section.""",
                'questions': ""
            },
            'concise': {
                'instructions': """You are an expert tutor. Generate concise, well-structured LaTeX study notes content.

IMPORTANT: Generate ONLY content (no \\documentclass or \\begin/\\end{document}).

STRUCTURE:
- \\section{} for major topics
- \\subsection{} for key concepts  
- Use \\textbf{} for important terms
- Create 1-2 summary tables with \\cellcolor{} for highlighting
- Keep explanations brief but comprehensive
- Use lists for key points
- End with a summary section

OUTPUT ONLY the LaTeX body content.""",
                'questions': ""
            },
            'outline': {
                'instructions': """You are an expert tutor. Create a comprehensive hierarchical outline in LaTeX format.

IMPORTANT: Generate ONLY content (no \\documentclass or \\begin/\\end{document}).

STRUCTURE:
- \\section{} for main topics
- \\subsection{} for subtopics
- \\subsubsection{} for details
- Use \\begin{itemize}...\\end{itemize} for bullet points
- Create a reference table at the end with \\begin{tabular}
- Use colors in the table with \\cellcolor{}

Keep outline clear and hierarchical.

OUTPUT ONLY the LaTeX body content.""",
                'questions': ""
            }
        }
        
        if note_type not in prompt_templates:
            logger.warning(f"Unknown note_type '{note_type}'. Using default 'detailed'")
            note_type = 'detailed'
        
        template = prompt_templates[note_type]
        
        logger.debug(f"Template selected: {note_type}")
        
        try:
            prompt = f"""{template['instructions']}

CONTENT TO ANALYZE:
{text[:8000]}

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
        
        # Remove any accidental \documentclass or \begin{document} commands that AI might have generated
        if '\\documentclass' in text:
            logger.debug("Removing accidental \\documentclass command...")
            # Find the first \section command and start from there
            section_pos = text.find('\\section')
            if section_pos != -1:
                text = text[section_pos:]
            else:
                # If no section found, try to remove everything before \begin{document}
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