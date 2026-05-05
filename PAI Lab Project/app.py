from flask import Flask, render_template, request
from textblob import TextBlob
from difflib import SequenceMatcher
import re
import requests
from spellchecker import SpellChecker

app = Flask(__name__)


def highlight_changes(original: str, corrected: str) -> str:
    """Return HTML for corrected text with changed words wrapped in <mark> tags."""
    orig_words = original.split()
    corr_words = corrected.split()                                          #Split both sentences into words
    s = SequenceMatcher(None, orig_words, corr_words)
    parts = []
    for tag, i1, i2, j1, j2 in s.get_opcodes():
        if tag == 'equal':
            parts.append(' '.join(corr_words[j1:j2]))
        elif tag in ('replace', 'insert'):
            if j1 < j2:
                parts.append('<mark>' + ' '.join(corr_words[j1:j2]) + '</mark>')
    return ' '.join([p for p in parts if p])                                      


@app.route('/')
def index():
    return render_template('index.html')                               #When user opens website → show index.html


@app.route('/correct', methods=['POST'])
def correct():
    text = request.form.get('text', '')                                   #This runs when user submits text.
    if not text.strip():
        return render_template('index.html', error="Please enter some text.")

    corrected = None                                                       #Get text from form
    corrected_html = None
    tool_message = None

    def lt_check(inp: str):
        url = 'https://api.languagetool.org/v2/check'                          #online grammar checker
        resp = requests.post(url, data={'text': inp, 'language': 'en-US'}, timeout=10)
        resp.raise_for_status()
        return resp.json()                                          #Get result

    def apply_lt_corrections(orig: str, matches: list) -> str:
        repls = []
        for m in matches:                                               #wrong words with correct ones
            if m.get('replacements'):
                repls.append((m['offset'], m['length'], m['replacements'][0]['value']))
        repls.sort(key=lambda x: x[0])                                #Store correction positions
        parts = []
        cursor = 0
        for off, length, repl in repls:
            if off < cursor:
                continue
            parts.append(orig[cursor:off])
            parts.append(repl)                                #Build corrected sentence
            cursor = off + length
        parts.append(orig[cursor:])
        return ''.join(parts)

    def apply_lt_highlight(orig: str, matches: list) -> str:
        repls = []
        for m in matches:                                            #Same as above but adds <mark> to highlight
            if m.get('replacements'):
                repls.append((m['offset'], m['length'], m['replacements'][0]['value']))
        repls.sort(key=lambda x: x[0])
        parts = []
        cursor = 0
        for off, length, repl in repls:
            if off < cursor:
                continue
            parts.append(orig[cursor:off])
            parts.append(f"<mark>{repl}</mark>")
            cursor = off + length
        parts.append(orig[cursor:])
        return ''.join(parts)
    try:
        resp = lt_check(text)
        matches = resp.get('matches', [])
        if matches:
            corrected = apply_lt_corrections(text, matches)
            corrected_html = apply_lt_highlight(text, matches)
        else:
            corrected = text
            corrected_html = text
    except Exception as e:
        tool_message = f"LanguageTool API unavailable: {e}. Falling back to local pipeline."

        try:
            spell = SpellChecker()                           #Fix each word

            def spell_fix_text(s: str) -> str:
                parts = re.split(r'(\W+)', s)
                for i, part in enumerate(parts):
                    if re.match(r'^\w+$', part):                               #Split text (words + symbols)
                        orig = part
                        lower = orig.lower()
                        suggestion = spell.correction(lower)
                        if suggestion and suggestion.lower() != lower:                   #Get correct spelling
                            if orig[0].isupper():
                                suggestion = suggestion.capitalize()
                            parts[i] = suggestion
                return ''.join(parts)

            pre_spelled = spell_fix_text(text)
            corrected = str(TextBlob(pre_spelled).correct())                               #First fix spelling → then grammar
        except Exception as e2:
            tool_message = (tool_message or '') + f" Spell-check fallback used: {e2}. Using TextBlob only."
            corrected = str(TextBlob(text).correct())                    #only TextBlob

    try:
        corrected_html = highlight_changes(text, corrected)             #Highlight differences
    except Exception:
        corrected_html = corrected

    return render_template('index.html', original=text, corrected=corrected, corrected_html=corrected_html, tool_message=tool_message)


if __name__ == '__main__':
    app.run(debug=True)