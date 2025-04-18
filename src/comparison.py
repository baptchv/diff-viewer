from src.diff_utils import read_text_file, highlight_word_differences, add_line_numbers
from src.html_renderer import render_diff_html

def compare_files(file1, file2):
    """Compare two text files and show differences with word-level highlighting."""
    text1 = read_text_file(file1)
    text2 = read_text_file(file2)
    
    return compare_text_content(text1, text2)

def compare_texts(text1, text2):
    """Compare two text strings directly."""
    return compare_text_content(text1, text2)

def compare_text_content(text1, text2):
    """Common function to compare text content regardless of source."""
    if not text1 and not text2:
        return "Both texts are empty."
    
    # Get highlighted lines with word-level differences
    highlighted_lines1, highlighted_lines2 = highlight_word_differences(text1, text2)
    
    # Add line numbers
    numbered_lines1 = add_line_numbers(highlighted_lines1)
    numbered_lines2 = add_line_numbers(highlighted_lines2)
    
    # Render the HTML output
    return render_diff_html(numbered_lines1, numbered_lines2)