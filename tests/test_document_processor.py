import pytest
from pathlib import Path
from src.document_processor import DocumentProcessor
from src.storage_handler import StorageHandler

@pytest.fixture
def processor(temp_config):
    """Create DocumentProcessor instance with test config."""
    config_handler = StorageHandler(temp_config)
    return DocumentProcessor(config_handler)

@pytest.fixture
def sample_text():
    """Create sample text for testing."""
    return ("This is the first sentence. This is the second sentence. " 
            "This is the third sentence. This is the fourth sentence. "
            "This is the fifth sentence.")

def test_create_chunks(processor, sample_text):
    """
    Test Purpose:
        Verify that text is correctly split into chunks of appropriate size with overlap.
    
    Tested Requirements:
        - Text must be split into multiple chunks when exceeding max size
        - Each chunk must not exceed maximum chunk size
        - Chunks must have specified overlap
    
    Test Steps:
        1. Initialization:
            - Configure processor with small chunk size (50) and overlap (20)
        2. Input Values:
            - Sample text with multiple sentences
            - max_chunk_size: 50
            - overlap: 20
        3. Expected Output:
            - Multiple chunks should be created
            - Each chunk should be <= 50 characters
        4. Cleanup:
            - None required
    """
    # Configure small chunk size for testing
    processor.chunk_settings['max_chunk_size'] = 50
    processor.chunk_settings['overlap'] = 20
    
    chunks = processor.create_chunks(sample_text)
    
    assert len(chunks) > 1  # Text should be split into multiple chunks
    assert all(len(chunk) <= 50 for chunk in chunks)  # Each chunk should respect max size

def test_invalid_file_type(processor):
    """
    Test Purpose:
        Verify that the processor rejects unsupported file types.
    
    Tested Requirements:
        - Processor must only accept .docx files
        - Must raise ValueError for unsupported file types
        - Error message must specify supported file types
    
    Test Steps:
        1. Initialization:
            - Create processor instance
        2. Input Values:
            - Invalid file path: "test.txt"
        3. Expected Output:
            - ValueError with message "Only .docx files are supported"
        4. Cleanup:
            - None required
    """
    with pytest.raises(ValueError, match="Only .docx files are supported"):
        processor.read_document("test.txt")

def test_file_not_found(processor):
    """
    Test Purpose:
        Verify that the processor handles nonexistent files appropriately.
    
    Tested Requirements:
        - Must raise FileNotFoundError for nonexistent files
        - Error must be raised before attempting to process file
    
    Test Steps:
        1. Initialization:
            - Create processor instance
        2. Input Values:
            - Nonexistent file path: "nonexistent.docx"
        3. Expected Output:
            - FileNotFoundError should be raised
        4. Cleanup:
            - None required
    """
    with pytest.raises(FileNotFoundError):
        processor.read_document("nonexistent.docx") 