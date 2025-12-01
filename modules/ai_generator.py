import google.generativeai as genai
from typing import Dict, Any
import os
import json

class AIGenerator:
    """Handles AI content generation using Gemini"""
    
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def generate_study_materials(self, text: str, note_type: str = 'detailed', 
                                include_questions: bool = True) -> str:
        """
        Generate study materials from extracted text
        Returns: LaTeX formatted content
        """
        # Truncate text if too long (Gemini has token limits)
        max_text_length = 10000  # Adjust based on your needs
        if len(text) > max_text_length:
            text = text[:max_text_length] + "\n\n[Content truncated due to length]"
        
        prompt = self._build_prompt(text, note_type, include_questions)
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.7,
                    'top_p': 0.8,
                    'top_k': 40,
                    'max_output_tokens': 2048,
                }
            )
            
            return self._clean_latex_response(response.text)
            
        except Exception as e:
            raise Exception(f"AI generation failed: {str(e)}")
    
    def _build_prompt(self, text: str, note_type: str, include_questions: bool) -> str:
        """Build the prompt for the AI"""
        
        prompt_templates = {
            'detailed': {
                'instructions': """You are an expert academic assistant. Analyze the provided lecture slides and create comprehensive study materials.

REQUIREMENTS:
1. Create a section "\section*{Detailed Notes}" with:
   - Clear subsection organization
   - Key concepts explained thoroughly
   - Important definitions highlighted
   - Logical flow between ideas

2. {questions_section}

3. Formatting rules:
   - Use \textbf{bold} for key terms
   - Use \textit{italic} for emphasis
   - Use \begin{itemize} for lists
   - Use \begin{enumerate} for numbered items
   - Add \newpage between major sections if needed

OUTPUT ONLY valid LaTeX code that compiles with 'article' class.""",
                'questions': """Create a section "\section*{Comprehensive Questions}" with:
   - 5-10 questions testing deep understanding
   - Mix of conceptual and applied questions
   - Use \begin{enumerate} for numbering"""
            },
            'concise': {
                'instructions': """You are a study assistant. Create concise notes from lecture slides.

REQUIREMENTS:
1. Create a section "\section*{Key Points}" with:
   - Bullet point summaries
   - Most important concepts only
   - No lengthy explanations

2. {questions_section}

3. Keep formatting minimal but clear.

OUTPUT ONLY valid LaTeX code.""",
                'questions': """Create a section "\section*{Quick Review}" with:
   - 3-5 multiple choice or short answer questions
   - Use \begin{enumerate} for numbering"""
            },
            'outline': {
                'instructions': """Create a structured outline from the lecture slides.

REQUIREMENTS:
1. Create a hierarchical outline using:
   - \section{}, \subsection{}, \subsubsection{}
   - \begin{itemize} for bullet points

2. Focus on structure and organization.

OUTPUT ONLY valid LaTeX code.""",
                'questions': ""
            }
        }
        
        template = prompt_templates.get(note_type, prompt_templates['detailed'])
        questions_section = template['questions'] if include_questions else ""
        
        prompt = f"""{template['instructions'].format(questions_section=questions_section)}

CONTENT TO ANALYZE:
{text[:8000]}  # Limit content in prompt

BEGIN OUTPUT:"""
        
        return prompt
    
    def _clean_latex_response(self, text: str) -> str:
        """Clean and validate LaTeX response"""
        # Remove markdown code blocks if present
        if '```latex' in text:
            text = text.split('```latex')[1].split('```')[0]
        elif '```' in text:
            text = text.split('```')[1].split('```')[0]
        
        # Ensure it starts with valid LaTeX
        if not text.strip().startswith('\\'):
            text = '\\section*{Study Notes}\n' + text
        
        return text.strip()