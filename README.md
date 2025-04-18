# Text Diff Viewer

A powerful web-based tool for comparing text files or direct text input with word-level difference highlighting.

## Features

- **Word-Level Difference Detection**: Identifies and highlights specific words that differ between two texts
- **Side-by-Side Comparison**: Clear visual presentation of differences
- **Synchronized Scrolling**: Both panels scroll together (can be toggled)
- **Line Numbers**: Easy reference with line numbering
- **Statistics**: Shows counts of additions, deletions, and changes
- **Flexible Input**: Support for both file uploads and direct text entry
- **Responsive Design**: Works on desktop and mobile devices

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/diff-viewer.git
cd diff-viewer

# Install dependencies
pip install -r requirements.txt
```

## Usage

Run the application:

```bash
python app.py
```

Then open your browser to the URL shown in the terminal (typically http://127.0.0.1:7860).

### File Comparison
1. Upload two text files
2. Click "Compare Files"
3. View the differences highlighted in the output

### Direct Text Comparison
1. Paste text into the "Original Text" area
2. Paste modified text into the "Modified Text" area
3. Click "Compare Texts"
4. View the differences highlighted in the output

## How it Works

The application uses Python's `difflib` module to detect differences between texts at both the line and word level. The differences are then displayed with color coding:

- **Green**: Added content
- **Red**: Deleted content
- **Yellow**: Changed content

## Screenshot

![Diff Viewer Screenshot](screenshot.png)

## License

MIT License