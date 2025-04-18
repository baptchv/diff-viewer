import difflib
import re
import html
from typing import List, Tuple

def read_text_file(file_path):
    """Read text from a file."""
    if file_path is None:
        return ""
    try:
        with open(file_path.name, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def highlight_word_differences(text1: str, text2: str) -> Tuple[List[str], List[str]]:
    """Generate line-by-line comparison with word-level differences highlighted."""
    lines1 = text1.splitlines() if text1 else []
    lines2 = text2.splitlines() if text2 else []
    
    # Process each line to highlight word differences
    highlighted_lines1 = []
    highlighted_lines2 = []
    
    # Line sequence matcher
    line_matcher = difflib.SequenceMatcher(None, lines1, lines2)
    
    for op, i1, i2, j1, j2 in line_matcher.get_opcodes():
        if op == 'equal':
            # For identical lines, just add them as is
            for i in range(i1, i2):
                highlighted_lines1.append(f'<div class="line equal">{html.escape(lines1[i])}</div>')
            for j in range(j1, j2):
                highlighted_lines2.append(f'<div class="line equal">{html.escape(lines2[j])}</div>')
                
        elif op == 'replace':
            # For replaced content, compare word by word
            for i, j in zip(range(i1, i2), range(j1, j2)):
                if i < len(lines1) and j < len(lines2):
                    # Do word-level diff for these two lines
                    line1_highlighted, line2_highlighted = word_diff_markup(lines1[i], lines2[j])
                    highlighted_lines1.append(f'<div class="line">{line1_highlighted}</div>')
                    highlighted_lines2.append(f'<div class="line">{line2_highlighted}</div>')
            
            # Handle any remaining lines if the blocks are not equal size
            for i in range(i1 + (j2 - j1), i2):
                if i < len(lines1):
                    highlighted_lines1.append(f'<div class="line deleted">{html.escape(lines1[i])}</div>')
                    highlighted_lines2.append('<div class="line empty">&nbsp;</div>')
                    
            for j in range(j1 + (i2 - i1), j2):
                if j < len(lines2):
                    highlighted_lines1.append('<div class="line empty">&nbsp;</div>')
                    highlighted_lines2.append(f'<div class="line added">{html.escape(lines2[j])}</div>')
                
        elif op == 'delete':
            # Content in text1 that's not in text2
            for i in range(i1, i2):
                highlighted_lines1.append(f'<div class="line deleted">{html.escape(lines1[i])}</div>')
            # Add empty lines to text2 to maintain alignment
            for _ in range(i2 - i1):
                highlighted_lines2.append('<div class="line empty">&nbsp;</div>')
                
        elif op == 'insert':
            # Content in text2 that's not in text1
            # Add empty lines to text1 to maintain alignment
            for _ in range(j2 - j1):
                highlighted_lines1.append('<div class="line empty">&nbsp;</div>')
            for j in range(j1, j2):
                highlighted_lines2.append(f'<div class="line added">{html.escape(lines2[j])}</div>')
    
    return highlighted_lines1, highlighted_lines2

def word_diff_markup(old_line: str, new_line: str) -> Tuple[str, str]:
    """Highlight word-level differences between two lines of text."""
    if not old_line and not new_line:
        return old_line, new_line
    
    # Split into words, keeping spaces
    def tokenize(text):
        # This pattern will split on word boundaries but keep delimiters
        return re.findall(r'\w+|\s+|[^\w\s]', text)
    
    old_words = tokenize(old_line)
    new_words = tokenize(new_line)
    
    matcher = difflib.SequenceMatcher(None, old_words, new_words)
    
    old_marked = []
    new_marked = []
    
    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        if op == 'equal':
            old_marked.extend([html.escape(w) for w in old_words[i1:i2]])
            new_marked.extend([html.escape(w) for w in new_words[j1:j2]])
        elif op == 'replace':
            old_marked.append(f'<span class="word-changed">{"".join(html.escape(w) for w in old_words[i1:i2])}</span>')
            new_marked.append(f'<span class="word-changed">{"".join(html.escape(w) for w in new_words[j1:j2])}</span>')
        elif op == 'delete':
            old_marked.append(f'<span class="word-deleted">{"".join(html.escape(w) for w in old_words[i1:i2])}</span>')
        elif op == 'insert':
            new_marked.append(f'<span class="word-added">{"".join(html.escape(w) for w in new_words[j1:j2])}</span>')
    
    return ''.join(old_marked), ''.join(new_marked)

def add_line_numbers(highlighted_lines):
    """Add line numbers to highlighted lines."""
    numbered_lines = []
    for i, line in enumerate(highlighted_lines):
        if '<div class="line' in line:
            line = line.replace('<div class="line', f'<div class="line-number">{i+1}</div><div class="line')
        numbered_lines.append(line)
    return numbered_lines