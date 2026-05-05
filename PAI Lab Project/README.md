# AI-Powered Grammar Correction Tool

This is a web-based application that analyzes user-input text, detects grammatical errors, and provides corrected sentence suggestions using Natural Language Processing with TextBlob.

## Features

- Text input interface for multi-line text
- Grammar and spelling correction using TextBlob
- Display of original and corrected text
- Simple, responsive UI

## Setup

1. Ensure Python 3.7+ is installed.
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python app.py`
4. Open your browser to `http://127.0.0.1:5000`

Optional (better grammar results): LanguageTool requires Java. To enable advanced grammar checks, install Java (JRE/JDK) and restart the app. Without Java the app will fall back to TextBlob's spelling corrections only.

On Windows you can install a JRE and then restart the app. After installing Java, LanguageTool will download its language models automatically on first run.

## Usage

1. Enter your text in the textarea.
2. Click "Check Grammar" to get the corrected version.
3. View the original and corrected text below.

## Technology Stack

- Backend: Python with Flask
- NLP: TextBlob
- Frontend: HTML, CSS, JavaScript