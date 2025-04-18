from typing import List

def get_css_styles():
    """Return the CSS styles for the diff viewer."""
    return """
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
    """

def get_sync_script():
    """Return the JavaScript for scroll synchronization."""
    return """
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

def create_stats_html(highlighted_lines1: List[str], highlighted_lines2: List[str]):
    """Create the HTML for the statistics section."""
    add_count = sum(1 for line in highlighted_lines2 if 'added' in line)
    del_count = sum(1 for line in highlighted_lines1 if 'deleted' in line)
    change_count = sum(1 for line in highlighted_lines1 if 'word-changed' in line)
    
    return f"""
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

def render_diff_html(highlighted_lines1: List[str], highlighted_lines2: List[str]):
    """Render the complete HTML for the diff viewer."""
    css = get_css_styles()
    js = get_sync_script()
    stats = create_stats_html(highlighted_lines1, highlighted_lines2)
    
    return f"""
    {css}
    {js}
    {stats}
    <div class="diff-container">
        <div class="diff-column">
            <h3>Original Text</h3>
            {"".join(highlighted_lines1)}
        </div>
        <div class="diff-column">
            <h3>Modified Text</h3>
            {"".join(highlighted_lines2)}
        </div>
    </div>
    """