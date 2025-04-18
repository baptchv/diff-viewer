import gradio as gr
from src.comparison import compare_files, compare_texts

def create_ui():
    """Create the Gradio UI for the diff viewer."""
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