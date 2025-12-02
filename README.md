🧠 PaperPress: AI-Powered Study Note Generator
Transform university lecture slides into beautifully formatted study notes and comprehension questions with one click. PaperPress is an intelligent desktop application that automates the tedious work of note-taking, giving you more time to actually learn.

https://img.shields.io/badge/python-3.8%252B-blue
https://img.shields.io/badge/backend-Flask-green
https://img.shields.io/badge/AI-Google%2520Gemini%2520API-6E42CC
https://img.shields.io/badge/License-MIT-yellow.svg

🎯 What Problem Does This Solve?
"I have hundreds of PDF slides, but no structured notes to study from."

If you're a student drowning in lecture slides, you know the struggle. Manually converting presentations into study materials is time-consuming. PaperPress automates this entire workflow:

Upload your lecture slides (PDF format)

AI analyzes the content and extracts key concepts

Automatically generates detailed LaTeX-formatted notes

Creates comprehension questions to test your understanding

Compiles everything into a professional PDF

✨ Features
Feature	Description
📁 Smart PDF Processing	Extracts text from digital PDFs (scanned PDFs coming soon)
🤖 AI-Powered Analysis	Uses Google's Gemini AI to identify key concepts and generate questions
📝 LaTeX Output	Produces publication-quality notes with proper formatting
❓ Comprehension Questions	Generates 5-10 deep understanding questions per document
🌐 Web Interface	Clean, intuitive UI for easy file upload and management
⚡ Local Processing	Your data stays on your machine - no cloud processing required
🚀 Quick Start
Prerequisites
Python 3.8 or higher

Google Gemini API key (free tier available)

Git

Installation
Clone the repository

bash
git clone https://github.com/YOUR_USERNAME/PaperPress.git
cd PaperPress
Set up a virtual environment and install dependencies

bash
# Create virtual environment
python -m venv .venv

# Activate it (Windows)
.venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt
Configure your environment

bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Gemini API key
# Get one from: https://makersuite.google.com/app/apkey
Run the application

bash
python app.py
Open your browser to http://localhost:5000

📖 How It Works
Here's the magic behind PaperPress:










Detailed Workflow
Document Processing: The system extracts clean text from your PDF slides using PyPDF2

AI Analysis: Google's Gemini AI analyzes the content to identify:

Key concepts and definitions

Important relationships between ideas

Areas that typically require clarification

Content Generation: The AI creates two structured sections:

Detailed Notes: Comprehensive summaries with proper hierarchical organization

Comprehension Questions: Thought-provoking questions that test understanding

Formatting: Everything is formatted in LaTeX for professional typesetting

Output: You receive both the LaTeX source and a compiled PDF

🗂️ Project Structure
text
PaperPress/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── .env.example         # Environment template
├── .gitignore           # Git ignore rules
├── uploads/             # Temporary uploaded files
├── outputs/             # Generated LaTeX/PDF files
├── static/              # CSS, JavaScript, images
│   ├── css/style.css
│   └── js/main.js
├── templates/           # HTML templates
│   └── index.html
├── modules/             # Core application logic
│   ├── pdf_processor.py
│   ├── ai_generator.py
│   └── latex_builder.py
└── utils/               # Helper functions
    └── helpers.py
🔧 Configuration
Getting a Gemini API Key
Visit Google AI Studio

Sign in with your Google account

Click "Create API Key"

Copy the key and add it to your .env file:

text
GEMINI_API_KEY=your_api_key_here
LaTeX Installation (Optional for PDF compilation)
For direct PDF compilation, you'll need a LaTeX distribution:

Windows: MiKTeX

Mac: MacTeX

Linux: sudo apt install texlive-latex-extra

Without LaTeX, you can still download the .tex file and compile it on Overleaf.

🖥️ Usage
Basic Usage
Start the application: python app.py

Open http://localhost:5000 in your browser

Drag and drop your PDF lecture slides

Select your preferred note style

Click "Generate Study Notes"

Download your LaTeX file or compiled PDF

Example Output
PaperPress generates LaTeX code like this:

latex
\section*{Detailed Notes}
\subsection*{Key Concept 1: Machine Learning}
\textbf{Definition}: Machine learning is a subset of artificial intelligence that...

\subsection*{Key Concept 2: Neural Networks}
Neural networks are inspired by biological neurons...

\section*{Comprehension Questions}
\begin{enumerate}
    \item What are the three main types of machine learning?
    \item Explain how gradient descent optimizes model parameters.
\end{enumerate}
🤝 Contributing
Found a bug or have a feature request? Contributions are welcome!

Fork the repository

Create a feature branch: git checkout -b feature/amazing-feature

Commit your changes: git commit -m 'Add amazing feature'

Push to the branch: git push origin feature/amazing-feature

Open a Pull Request

Development Setup
bash
# Install development dependencies
pip install -r requirements.txt

# Run in development mode
python app.py

# The app will reload automatically on code changes
📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments
Google Gemini AI for the powerful language model

Flask for the web framework

PyPDF2 for PDF text extraction

All the students who inspired this tool to make studying more efficient

📊 Roadmap
Batch Processing: Handle multiple PDFs at once

Template Customization: Choose from different note formats

OCR Integration: Support for scanned/image-based PDFs

Export Formats: Markdown, DOCX, and HTML output

Topic Summarization: Generate course-wide summaries from multiple lectures

Spaced Repetition Integration: Export to Anki or other flashcard apps
