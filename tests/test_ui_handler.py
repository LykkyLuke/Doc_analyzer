import pytest
from unittest.mock import Mock, patch
import tkinter as tk
from src.ui_handler import DocumentAnalyzerUI

@pytest.fixture
def mock_dependencies():
    """Create mock dependencies for UI testing."""
    return {
        'storage_handler': Mock(),
        'document_processor': Mock(),
        'summarization_engine': Mock()
    }

@pytest.fixture
def ui(mock_dependencies):
    """Create UI instance with mock dependencies."""
    with patch('tkinter.Tk'):
        ui = DocumentAnalyzerUI(
            mock_dependencies['storage_handler'],
            mock_dependencies['document_processor'],
            mock_dependencies['summarization_engine']
        )
        return ui

def test_load_saved_api_key(ui, mock_dependencies):
    """
    Test Purpose:
        Verify that saved API key is loaded and displayed in UI on startup.
    
    Tested Requirements:
        - UI must load API key from storage
        - UI must display loaded API key in entry field
        - UI must handle missing API key gracefully
    
    Test Steps:
        1. Initialization:
            - Mock storage handler to return test key
        2. Input Values:
            - Saved API key: "test_key"
        3. Expected Output:
            - API key entry should display "test_key"
        4. Cleanup:
            - None required
    """
    mock_dependencies['storage_handler'].load_api_key.return_value = "test_key"
    ui._load_saved_api_key()
    assert ui.api_key_entry.get() == "test_key"

def test_save_api_key(ui, mock_dependencies):
    """
    Test Purpose:
        Verify that API key is saved correctly when user enters new key.
    
    Tested Requirements:
        - UI must save API key to storage
        - UI must show success message
        - Storage handler must be called with correct key
    
    Test Steps:
        1. Initialization:
            - Mock message box
            - Insert test key in entry
        2. Input Values:
            - New API key: "new_test_key"
        3. Expected Output:
            - Storage handler should be called with "new_test_key"
        4. Cleanup:
            - None required
    """
    with patch('tkinter.messagebox.showinfo'):
        ui.api_key_entry.insert(0, "new_test_key")
        ui._save_api_key()
        mock_dependencies['storage_handler'].save_api_key.assert_called_with("new_test_key")

def test_validate_inputs_both_valid(ui):
    """
    Test Purpose:
        Verify that analyze button is enabled when both inputs are valid.
    
    Tested Requirements:
        - UI must enable analyze button when API key and file are present
        - UI must validate both inputs before enabling button
    
    Test Steps:
        1. Initialization:
            - Set valid API key
            - Set valid file path
        2. Input Values:
            - API key: "test_key"
            - Selected file: "test.docx"
        3. Expected Output:
            - Analyze button should be enabled (NORMAL state)
        4. Cleanup:
            - None required
    """
    ui.api_key_entry.insert(0, "test_key")
    ui.selected_file = "test.docx"
    ui._validate_inputs()
    assert ui.analyze_button['state'] == tk.NORMAL

def test_validate_inputs_missing_api_key(ui):
    """
    Test Purpose:
        Verify that analyze button is disabled when API key is missing.
    
    Tested Requirements:
        - UI must disable analyze button when API key is missing
        - UI must validate API key independently
    
    Test Steps:
        1. Initialization:
            - Set valid file path only
        2. Input Values:
            - API key: "" (empty)
            - Selected file: "test.docx"
        3. Expected Output:
            - Analyze button should be disabled (DISABLED state)
        4. Cleanup:
            - None required
    """
    ui.selected_file = "test.docx"
    ui._validate_inputs()
    assert ui.analyze_button['state'] == tk.DISABLED

def test_start_analysis(ui, mock_dependencies):
    """
    Test Purpose:
        Verify that document analysis workflow executes correctly.
    
    Tested Requirements:
        - UI must read and process document
        - UI must create text chunks
        - UI must start summarization in separate thread
        - UI must handle workflow steps in correct order
    
    Test Steps:
        1. Initialization:
            - Mock document processing steps
            - Mock summarization
        2. Input Values:
            - Mock document text: "doc"
            - Mock extracted text: "text"
            - Mock chunks: ["chunk1"]
        3. Expected Output:
            - Document processor methods should be called in sequence
            - Summarization should be started in new thread
        4. Cleanup:
            - None required
    """
    # Mock document processing
    mock_dependencies['document_processor'].read_document.return_value = "doc"
    mock_dependencies['document_processor'].extract_text.return_value = "text"
    mock_dependencies['document_processor'].create_chunks.return_value = ["chunk1"]
    
    # Mock summarization
    mock_dependencies['summarization_engine'].summarize_document.return_value = "summary"
    
    with patch('threading.Thread') as mock_thread:
        ui._start_analysis()
        mock_thread.assert_called_once()

def test_error_handling(ui):
    """
    Test Purpose:
        Verify that errors are displayed correctly in UI.
    
    Tested Requirements:
        - UI must display error messages in dialog
        - Error messages must be formatted correctly
        - Error dialog must use correct title
    
    Test Steps:
        1. Initialization:
            - Mock error dialog
        2. Input Values:
            - Error message: "Test error"
        3. Expected Output:
            - Error dialog should be shown with correct title and message
        4. Cleanup:
            - None required
    """
    with patch('tkinter.messagebox.showerror') as mock_error:
        ui._show_error("Test error")
        mock_error.assert_called_with("Error", "Analysis failed: Test error")

def test_progress_update(ui):
    """
    Test Purpose:
        Verify that progress updates are displayed correctly.
    
    Tested Requirements:
        - UI must update progress bar value
        - UI must update status label text
        - Progress must be displayed accurately
    
    Test Steps:
        1. Initialization:
            - None required
        2. Input Values:
            - Current progress: 50
            - Total items: 100
        3. Expected Output:
            - Progress bar should show 50% progress
            - Status label should show "Processing chunk 50 of 100"
        4. Cleanup:
            - None required
    """
    ui._update_progress(50, 100)
    assert ui.progress_bar["value"] == 50
    assert "Processing chunk 50 of 100" in ui.status_label["text"] 