import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
from typing import Optional, Callable

class DocumentAnalyzerUI:
    """Main UI handler for the Document Analyzer application."""
    
    def __init__(self, storage_handler, document_processor, summarization_engine):
        """Initialize the UI with required components."""
        self.storage_handler = storage_handler
        self.document_processor = document_processor
        self.summarization_engine = summarization_engine
        
        self.window = tk.Tk()
        self.window.title("Document Analyzer")
        self.window.geometry("600x400")
        
        self.selected_file: Optional[Path] = None
        self.processing_thread: Optional[threading.Thread] = None
        
        self._init_ui()
        self._load_saved_api_key()
    
    def _init_ui(self):
        """Initialize UI components."""
        # API Key Section
        api_frame = ttk.LabelFrame(self.window, text="API Configuration", padding=10)
        api_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(api_frame, text="API Key:").pack(side=tk.LEFT)
        self.api_key_entry = ttk.Entry(api_frame, show="*", width=40)
        self.api_key_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            api_frame, 
            text="Save", 
            command=self._save_api_key
        ).pack(side=tk.LEFT, padx=5)
        
        # File Selection Section
        file_frame = ttk.LabelFrame(self.window, text="Document Selection", padding=10)
        file_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.file_label = ttk.Label(file_frame, text="No file selected")
        self.file_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(
            file_frame,
            text="Select File",
            command=self._select_file
        ).pack(side=tk.RIGHT)
        
        # Progress Section
        progress_frame = ttk.LabelFrame(self.window, text="Progress", padding=10)
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            length=400
        )
        self.progress_bar.pack(fill=tk.X)
        
        self.status_label = ttk.Label(progress_frame, text="Ready")
        self.status_label.pack()
        
        # Action Buttons
        button_frame = ttk.Frame(self.window, padding=10)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.analyze_button = ttk.Button(
            button_frame,
            text="Analyze Document",
            command=self._start_analysis,
            state=tk.DISABLED
        )
        self.analyze_button.pack(side=tk.RIGHT)
    
    def _load_saved_api_key(self):
        """Load saved API key from storage."""
        api_key = self.storage_handler.load_api_key()
        if api_key:
            self.api_key_entry.insert(0, api_key)
            self._validate_inputs()
    
    def _save_api_key(self):
        """Save API key to storage."""
        api_key = self.api_key_entry.get().strip()
        if api_key:
            self.storage_handler.save_api_key(api_key)
            messagebox.showinfo("Success", "API key saved successfully!")
            self._validate_inputs()
    
    def _select_file(self):
        """Handle file selection."""
        file_path = filedialog.askopenfilename(
            filetypes=[("Word Documents", "*.docx")]
        )
        if file_path:
            self.selected_file = Path(file_path)
            self.file_label.config(text=self.selected_file.name)
            self._validate_inputs()
    
    def _validate_inputs(self):
        """Validate inputs and enable/disable analyze button."""
        api_key = self.api_key_entry.get().strip()
        if api_key and self.selected_file:
            self.analyze_button.config(state=tk.NORMAL)
        else:
            self.analyze_button.config(state=tk.DISABLED)
    
    def _update_progress(self, current: int, total: int):
        """Update progress bar and status."""
        progress = (current / total) * 100
        self.progress_bar["value"] = progress
        self.status_label.config(
            text=f"Processing chunk {current} of {total}"
        )
        self.window.update_idletasks()
    
    def _start_analysis(self):
        """Start document analysis in a separate thread."""
        if self.processing_thread and self.processing_thread.is_alive():
            return
        
        self.analyze_button.config(state=tk.DISABLED)
        self.progress_bar["value"] = 0
        self.status_label.config(text="Starting analysis...")
        
        def analyze():
            try:
                # Process document
                document = self.document_processor.read_document(str(self.selected_file))
                text = self.document_processor.extract_text(document)
                chunks = self.document_processor.create_chunks(text)
                
                # Set up progress tracking
                self.summarization_engine.set_progress_callback(self._update_progress)
                
                # Generate summary
                summary = self.summarization_engine.summarize_document(chunks)
                
                # Show results
                self.window.after(0, self._show_results, summary)
                
            except Exception as e:
                self.window.after(0, self._show_error, str(e))
            finally:
                self.window.after(0, self._analysis_completed)
        
        self.processing_thread = threading.Thread(target=analyze)
        self.processing_thread.start()
    
    def _show_results(self, summary: str):
        """Show analysis results."""
        result_window = tk.Toplevel(self.window)
        result_window.title("Analysis Results")
        result_window.geometry("500x400")
        
        text_widget = tk.Text(result_window, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, summary)
        text_widget.config(state=tk.DISABLED)
    
    def _show_error(self, error_message: str):
        """Show error message."""
        messagebox.showerror("Error", f"Analysis failed: {error_message}")
    
    def _analysis_completed(self):
        """Reset UI after analysis completion."""
        self.analyze_button.config(state=tk.NORMAL)
        self.status_label.config(text="Analysis completed")
    
    def run(self):
        """Start the UI main loop."""
        self.window.mainloop() 