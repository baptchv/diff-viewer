import gradio as gr
import difflib
import re
from typing import List, Tuple
import html

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

def compare_files(file1, file2):
    """Compare two text files and show differences with word-level highlighting."""
    text1 = read_text_file(file1)
    text2 = read_text_file(file2)
    
    if not text1 and not text2:
        return "Both files are empty."
    
    highlighted_lines1, highlighted_lines2 = highlight_word_differences(text1, text2)
    
    css = """
    <style>
        .diff-container {
            display: flex;
            width: 100%;
            font-family: monospace;
            border: 1px solid #ccc;
            border-radius: 4px;
            overflow: hidden;
        }
        .diff-column {
            width: 50%;
            overflow-x: auto;
            padding: 10px;
            max-height: 600px;
            overflow-y: auto;
        }
        .diff-column:first-child {
            border-right: 1px solid #ddd;
        }
        .line {
            padding: 2px 5px;
            white-space: pre-wrap;
            margin: 2px 0;
            border-radius: 3px;
            min-height: 1.2em;
        }
        .changed {
            background-color: #ffffd7;
        }
        .deleted {
            background-color: #ffdddd;
        }
        .added {
            background-color: #ddffdd;
        }
        .equal {
            background-color: transparent;
        }
        .empty {
            background-color: #f8f8f8;
            color: #ccc;
        }
        .word-changed {
            background-color: #fff0a0;
            border-radius: 2px;
            padding: 1px 2px;
            border: 1px dashed #fd8;
        }
        .word-deleted {
            background-color: #ffbbbb;
            border-radius: 2px;
            padding: 1px 2px;
            text-decoration: line-through;
            border: 1px solid #faa;
        }
        .word-added {
            background-color: #bbffbb;
            border-radius: 2px;
            padding: 1px 2px;
            border: 1px solid #afa;
        }
        .stats {
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
            font-family: sans-serif;
            background: #f5f5f5;
            padding: 10px;
            border-radius: 4px;
        }
        .stat-item {
            padding: 5px 10px;
            border-radius: 4px;
            display: inline-block;
            margin-right: 10px;
            font-weight: bold;
            color: white;
        }
        .stat-add {
            background-color: #4c8;
        }
        .stat-del {
            background-color: #c68;
        }
        .stat-change {
            background-color: #cc8;
        }
        h3 {
            margin-top: 0;
            margin-bottom: 10px;
            padding-bottom: 5px;
            border-bottom: 1px solid #eee;
            font-family: sans-serif;
        }
        .line-number {
            color: #999;
            text-align: right;
            padding-right: 10px;
            user-select: none;
            font-size: 0.85em;
            width: 30px;
            display: inline-block;
        }
        .scroll-sync {
            display: flex;
            margin-bottom: 5px;
        }
        .button-toggle {
            background: #f0f0f0;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 8px 12px;
            cursor: pointer;
            font-size: 14px;
            display: inline-flex;
            align-items: center;
            transition: all 0.2s ease;
            font-weight: bold;
        }
        .button-toggle:hover {
            background: #e6e6e6;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .button-toggle.disabled {
            background: #f8f8f8;
            color: #999;
            border-color: #eee;
        }
        #sync-icon {
            margin-right: 8px;
            font-size: 16px;
        }
    </style>
    
    <script>
    // This inline JavaScript will be executed after each render
    // We'll use a custom solution that's compatible with Gradio's rendering approach
    
    // Define a global variable to control sync state
    window.diffSyncEnabled = true;
    
    // Initialize a periodic checker function to repeatedly attempt to set up sync
    // This ensures sync will be established even after Gradio's dynamic content updates
    function startSyncMonitor() {
        console.log("Starting diff sync monitor");
        
        // Clear any existing interval
        if (window.syncMonitorInterval) {
            clearInterval(window.syncMonitorInterval);
        }
        
        // Set up a recurring interval that will keep checking for the panels
        window.syncMonitorInterval = setInterval(function() {
            setupScrollSync();
        }, 1000); // Check every second
        
        // Also try to set up immediately
        setupScrollSync();
    }
    
    // Function that actually sets up the scroll synchronization
    function setupScrollSync() {
        const leftPanel = document.querySelector('.diff-container .diff-column:first-child');
        const rightPanel = document.querySelector('.diff-container .diff-column:last-child');
        const syncToggle = document.getElementById('sync-toggle');
        
        // If we can't find the panels, they might not be rendered yet
        if (!leftPanel || !rightPanel) {
            console.log("Panels not found yet, will retry");
            return;
        }
        
        // If we already set this up (check for our custom attribute), no need to do it again
        if (leftPanel.hasAttribute('data-sync-initialized')) {
            return;
        }
        
        console.log("Setting up scroll sync between panels");
        
        // Mark these panels as initialized
        leftPanel.setAttribute('data-sync-initialized', 'true');
        rightPanel.setAttribute('data-sync-initialized', 'true');
        
        // Create syncing functions with throttling to avoid infinite loops
        let leftScrolling = false;
        let rightScrolling = false;
        
        leftPanel.addEventListener('scroll', function() {
            if (!window.diffSyncEnabled || rightScrolling) return;
            
            leftScrolling = true;
            rightPanel.scrollTop = leftPanel.scrollTop;
            rightPanel.scrollLeft = leftPanel.scrollLeft;
            
            // Release lock after a short delay
            setTimeout(function() {
                leftScrolling = false;
            }, 10);
        });
        
        rightPanel.addEventListener('scroll', function() {
            if (!window.diffSyncEnabled || leftScrolling) return;
            
            rightScrolling = true;
            leftPanel.scrollTop = rightPanel.scrollTop;
            leftPanel.scrollLeft = rightPanel.scrollLeft;
            
            // Release lock after a short delay
            setTimeout(function() {
                rightScrolling = false;
            }, 10);
        });
        
        // Set up toggle button
        if (syncToggle) {
            syncToggle.onclick = function(e) {
                // Prevent any default form submission
                e.preventDefault();
                e.stopPropagation();
                
                // Toggle sync state
                window.diffSyncEnabled = !window.diffSyncEnabled;
                
                // Update button appearance
                const syncText = document.getElementById('sync-text');
                const syncIcon = document.getElementById('sync-icon');
                
                if (window.diffSyncEnabled) {
                    syncText.textContent = 'Scroll Sync: ON';
                    syncIcon.textContent = '🔄';
                    syncToggle.classList.remove('disabled');
                } else {
                    syncText.textContent = 'Scroll Sync: OFF';
                    syncIcon.textContent = '⛔';
                    syncToggle.classList.add('disabled');
                }
                
                return false;
            };
        }
        
        console.log("Scroll sync initialized successfully");
        
        // If we got here, we can stop the interval since sync is set up
        if (window.syncMonitorInterval) {
            clearInterval(window.syncMonitorInterval);
            window.syncMonitorInterval = null;
        }
    }
    
    // Set up event listeners for Gradio's dynamic content loading
    document.addEventListener('DOMContentLoaded', function() {
        startSyncMonitor();
        
        // Watch for changes to the DOM that might indicate Gradio has updated the content
        const observer = new MutationObserver(function(mutations) {
            for (const mutation of mutations) {
                if (mutation.type === 'childList') {
                    // If new diff container was added, restart the sync monitor
                    const diffContainer = document.querySelector('.diff-container');
                    if (diffContainer && !diffContainer.querySelector('[data-sync-initialized]')) {
                        startSyncMonitor();
                    }
                }
            }
        });
        
        // Start observing
        observer.observe(document.body, { childList: true, subtree: true });
    });
    
    // Also set up on load, in case DOMContentLoaded already fired
    window.addEventListener('load', startSyncMonitor);
    
    // Add one more fallback - try to set up sync after a delay
    setTimeout(startSyncMonitor, 1000);
    </script>
    """
    
    # Calculate statistics
    add_count = sum(1 for line in highlighted_lines2 if 'added' in line)
    del_count = sum(1 for line in highlighted_lines1 if 'deleted' in line)
    change_count = sum(1 for line in highlighted_lines1 if 'word-changed' in line)
    
    stats = f"""
    <div class="stats">
        <div>
            <span class="stat-item stat-add">+{add_count}</span>
            <span class="stat-item stat-del">-{del_count}</span>
            <span class="stat-item stat-change">~{change_count}</span>
        </div>
        <div class="scroll-sync">
            <button id="sync-toggle" class="button-toggle">
                <span id="sync-icon">🔄</span> 
                <span id="sync-text">Scroll Sync: ON</span>
            </button>
        </div>
    </div>
    """
    
    # Add line numbers
    numbered_lines1 = []
    numbered_lines2 = []
    for i, line in enumerate(highlighted_lines1):
        if '<div class="line' in line:
            line = line.replace('<div class="line', f'<div class="line-number">{i+1}</div><div class="line')
        numbered_lines1.append(line)
    
    for i, line in enumerate(highlighted_lines2):
        if '<div class="line' in line:
            line = line.replace('<div class="line', f'<div class="line-number">{i+1}</div><div class="line')
        numbered_lines2.append(line)
    
    html_output = f"""
    {css}
    {stats}
    <div class="diff-container">
        <div class="diff-column">
            <h3>Original Text</h3>
            {"".join(numbered_lines1)}
        </div>
        <div class="diff-column">
            <h3>Modified Text</h3>
            {"".join(numbered_lines2)}
        </div>
    </div>
    """
    
    return html_output

def compare_texts(text1, text2):
    """Compare two text strings directly."""
    if not text1 and not text2:
        return "Both texts are empty."
    
    highlighted_lines1, highlighted_lines2 = highlight_word_differences(text1, text2)
    
    css = """
    <style>
        .diff-container {
            display: flex;
            width: 100%;
            font-family: monospace;
            border: 1px solid #ccc;
            border-radius: 4px;
            overflow: hidden;
        }
        .diff-column {
            width: 50%;
            overflow-x: auto;
            padding: 10px;
            max-height: 600px;
            overflow-y: auto;
        }
        .diff-column:first-child {
            border-right: 1px solid #ddd;
        }
        .line {
            padding: 2px 5px;
            white-space: pre-wrap;
            margin: 2px 0;
            border-radius: 3px;
            min-height: 1.2em;
        }
        .changed {
            background-color: #ffffd7;
        }
        .deleted {
            background-color: #ffdddd;
        }
        .added {
            background-color: #ddffdd;
        }
        .equal {
            background-color: transparent;
        }
        .empty {
            background-color: #f8f8f8;
            color: #ccc;
        }
        .word-changed {
            background-color: #fff0a0;
            border-radius: 2px;
            padding: 1px 2px;
            border: 1px dashed #fd8;
        }
        .word-deleted {
            background-color: #ffbbbb;
            border-radius: 2px;
            padding: 1px 2px;
            text-decoration: line-through;
            border: 1px solid #faa;
        }
        .word-added {
            background-color: #bbffbb;
            border-radius: 2px;
            padding: 1px 2px;
            border: 1px solid #afa;
        }
        .stats {
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
            font-family: sans-serif;
            background: #f5f5f5;
            padding: 10px;
            border-radius: 4px;
        }
        .stat-item {
            padding: 5px 10px;
            border-radius: 4px;
            display: inline-block;
            margin-right: 10px;
            font-weight: bold;
            color: white;
        }
        .stat-add {
            background-color: #4c8;
        }
        .stat-del {
            background-color: #c68;
        }
        .stat-change {
            background-color: #cc8;
        }
        h3 {
            margin-top: 0;
            margin-bottom: 10px;
            padding-bottom: 5px;
            border-bottom: 1px solid #eee;
            font-family: sans-serif;
        }
        .line-number {
            color: #999;
            text-align: right;
            padding-right: 10px;
            user-select: none;
            font-size: 0.85em;
            width: 30px;
            display: inline-block;
        }
        .scroll-sync {
            display: flex;
            margin-bottom: 5px;
        }
        .button-toggle {
            background: #f0f0f0;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 8px 12px;
            cursor: pointer;
            font-size: 14px;
            display: inline-flex;
            align-items: center;
            transition: all 0.2s ease;
            font-weight: bold;
        }
        .button-toggle:hover {
            background: #e6e6e6;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .button-toggle.disabled {
            background: #f8f8f8;
            color: #999;
            border-color: #eee;
        }
        #sync-icon {
            margin-right: 8px;
            font-size: 16px;
        }
    </style>
    
    <script>
    // Same script as in compare_files
    // Define a global variable to control sync state
    window.diffSyncEnabled = true;
    
    function startSyncMonitor() {
        console.log("Starting diff sync monitor");
        
        if (window.syncMonitorInterval) {
            clearInterval(window.syncMonitorInterval);
        }
        
        window.syncMonitorInterval = setInterval(function() {
            setupScrollSync();
        }, 1000);
        
        setupScrollSync();
    }
    
    function setupScrollSync() {
        const leftPanel = document.querySelector('.diff-container .diff-column:first-child');
        const rightPanel = document.querySelector('.diff-container .diff-column:last-child');
        const syncToggle = document.getElementById('sync-toggle');
        
        if (!leftPanel || !rightPanel) {
            console.log("Panels not found yet, will retry");
            return;
        }
        
        if (leftPanel.hasAttribute('data-sync-initialized')) {
            return;
        }
        
        console.log("Setting up scroll sync between panels");
        
        leftPanel.setAttribute('data-sync-initialized', 'true');
        rightPanel.setAttribute('data-sync-initialized', 'true');
        
        let leftScrolling = false;
        let rightScrolling = false;
        
        leftPanel.addEventListener('scroll', function() {
            if (!window.diffSyncEnabled || rightScrolling) return;
            
            leftScrolling = true;
            rightPanel.scrollTop = leftPanel.scrollTop;
            rightPanel.scrollLeft = leftPanel.scrollLeft;
            
            setTimeout(function() {
                leftScrolling = false;
            }, 10);
        });
        
        rightPanel.addEventListener('scroll', function() {
            if (!window.diffSyncEnabled || leftScrolling) return;
            
            rightScrolling = true;
            leftPanel.scrollTop = rightPanel.scrollTop;
            leftPanel.scrollLeft = rightPanel.scrollLeft;
            
            setTimeout(function() {
                rightScrolling = false;
            }, 10);
        });
        
        if (syncToggle) {
            syncToggle.onclick = function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                window.diffSyncEnabled = !window.diffSyncEnabled;
                
                const syncText = document.getElementById('sync-text');
                const syncIcon = document.getElementById('sync-icon');
                
                if (window.diffSyncEnabled) {
                    syncText.textContent = 'Scroll Sync: ON';
                    syncIcon.textContent = '🔄';
                    syncToggle.classList.remove('disabled');
                } else {
                    syncText.textContent = 'Scroll Sync: OFF';
                    syncIcon.textContent = '⛔';
                    syncToggle.classList.add('disabled');
                }
                
                return false;
            };
        }
        
        console.log("Scroll sync initialized successfully");
        
        if (window.syncMonitorInterval) {
            clearInterval(window.syncMonitorInterval);
            window.syncMonitorInterval = null;
        }
    }
    
    document.addEventListener('DOMContentLoaded', function() {
        startSyncMonitor();
        
        const observer = new MutationObserver(function(mutations) {
            for (const mutation of mutations) {
                if (mutation.type === 'childList') {
                    const diffContainer = document.querySelector('.diff-container');
                    if (diffContainer && !diffContainer.querySelector('[data-sync-initialized]')) {
                        startSyncMonitor();
                    }
                }
            }
        });
        
        observer.observe(document.body, { childList: true, subtree: true });
    });
    
    window.addEventListener('load', startSyncMonitor);
    
    setTimeout(startSyncMonitor, 1000);
    </script>
    """
    
    # Calculate statistics
    add_count = sum(1 for line in highlighted_lines2 if 'added' in line)
    del_count = sum(1 for line in highlighted_lines1 if 'deleted' in line)
    change_count = sum(1 for line in highlighted_lines1 if 'word-changed' in line)
    
    stats = f"""
    <div class="stats">
        <div>
            <span class="stat-item stat-add">+{add_count}</span>
            <span class="stat-item stat-del">-{del_count}</span>
            <span class="stat-item stat-change">~{change_count}</span>
        </div>
        <div class="scroll-sync">
            <button id="sync-toggle" class="button-toggle">
                <span id="sync-icon">🔄</span> 
                <span id="sync-text">Scroll Sync: ON</span>
            </button>
        </div>
    </div>
    """
    
    # Add line numbers
    numbered_lines1 = []
    numbered_lines2 = []
    for i, line in enumerate(highlighted_lines1):
        if '<div class="line' in line:
            line = line.replace('<div class="line', f'<div class="line-number">{i+1}</div><div class="line')
        numbered_lines1.append(line)
    
    for i, line in enumerate(highlighted_lines2):
        if '<div class="line' in line:
            line = line.replace('<div class="line', f'<div class="line-number">{i+1}</div><div class="line')
        numbered_lines2.append(line)
    
    html_output = f"""
    {css}
    {stats}
    <div class="diff-container">
        <div class="diff-column">
            <h3>Original Text</h3>
            {"".join(numbered_lines1)}
        </div>
        <div class="diff-column">
            <h3>Modified Text</h3>
            {"".join(numbered_lines2)}
        </div>
    </div>
    """
    
    return html_output

def create_ui():
    with gr.Blocks(title="Diff Viewer", theme=gr.themes.Soft()) as app:
        gr.Markdown("# Text Difference Viewer")
        
        with gr.Tabs():
            with gr.TabItem("File Comparison"):
                gr.Markdown("Upload two text files to compare and see word-level differences highlighted.")
                
                with gr.Row():
                    file1_input = gr.File(label="Original Text File", file_types=["text"])
                    file2_input = gr.File(label="Modified Text File", file_types=["text"])
                
                compare_btn = gr.Button("Compare Files", variant="primary")
                file_diff_output = gr.HTML(label="Differences")
                
                compare_btn.click(
                    fn=compare_files,
                    inputs=[file1_input, file2_input],
                    outputs=file_diff_output
                )
            
            with gr.TabItem("Direct Text Comparison"):
                gr.Markdown("Paste text directly into the text areas to compare.")
                
                with gr.Row():
                    text1_input = gr.Textbox(label="Original Text", lines=10, placeholder="Paste original text here...")
                    text2_input = gr.Textbox(label="Modified Text", lines=10, placeholder="Paste modified text here...")
                
                compare_text_btn = gr.Button("Compare Texts", variant="primary")
                text_diff_output = gr.HTML(label="Differences")
                
                compare_text_btn.click(
                    fn=compare_texts,
                    inputs=[text1_input, text2_input],
                    outputs=text_diff_output
                )
        
        gr.Markdown("""
        ## Features
        - Word-level difference highlighting
        - Synchronized scrolling between panels (can be toggled)
        - Line numbers for easy reference
        - Statistics showing additions, deletions, and changes
        - Support for both file uploads and direct text entry
        """)
        
    return app

if __name__ == "__main__":
    app = create_ui()
    app.launch()