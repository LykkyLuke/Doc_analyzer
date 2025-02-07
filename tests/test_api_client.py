import pytest
from unittest.mock import Mock, patch
from src.api_client import GeminiAPIClient
from src.storage_handler import StorageHandler

@pytest.fixture
def api_client(temp_config):
    """Create GeminiAPIClient instance with test config."""
    config_handler = StorageHandler(temp_config)
    with patch('vertexai.init'), \
         patch('vertexai.generative_models.GenerativeModel'):
        return GeminiAPIClient(config_handler)

def test_initialization(api_client):
    """
    Test Purpose:
        Verify that the GeminiAPIClient initializes correctly with proper model settings.
    
    Tested Requirements:
        - Client must initialize with Gemini Pro model
        - Client must load model settings from configuration
        - Model instance must be created successfully
    
    Test Steps:
        1. Initialization:
            - Create API client with test configuration
        2. Input Values:
            - Default model settings from configuration
        3. Expected Output:
            - Model instance should not be None
            - Model name should be 'gemini-pro'
        4. Cleanup:
            - None required (handled by pytest fixture)
    """
    assert api_client.model is not None
    assert api_client.model_settings['model'] == 'gemini-pro'

@patch('vertexai.init')
def test_initialization_failure(mock_init):
    """
    Test Purpose:
        Verify that the client handles initialization failures gracefully.
    
    Tested Requirements:
        - Client must raise appropriate error on initialization failure
        - Error message must be descriptive
    
    Test Steps:
        1. Initialization:
            - Mock VertexAI initialization to raise exception
        2. Input Values:
            - Simulated initialization error
        3. Expected Output:
            - RuntimeError with message "Failed to initialize VertexAI client"
        4. Cleanup:
            - None required
    """
    mock_init.side_effect = Exception("Init failed")
    
    with pytest.raises(RuntimeError, match="Failed to initialize VertexAI client"):
        GeminiAPIClient(Mock())

def test_generate_content(api_client):
    """
    Test Purpose:
        Verify that the client can generate content using the Gemini model.
    
    Tested Requirements:
        - Client must send prompt to model
        - Client must return generated text response
        - Model's generate_content method must be called exactly once
    
    Test Steps:
        1. Initialization:
            - Set up mock response
        2. Input Values:
            - Test prompt: "Test prompt"
            - Mock response text: "Generated text"
        3. Expected Output:
            - Return value should match mock response text
            - generate_content should be called once
        4. Cleanup:
            - None required
    """
    mock_response = Mock()
    mock_response.text = "Generated text"
    api_client.model.generate_content.return_value = mock_response
    
    result = api_client.generate_content("Test prompt")
    assert result == "Generated text"
    api_client.model.generate_content.assert_called_once()

def test_stream_generate_content(api_client):
    """
    Test Purpose:
        Verify that the client can stream content generation and concatenate chunks.
    
    Tested Requirements:
        - Client must handle streaming response
        - Client must concatenate text chunks correctly
        - Final result must contain all generated content
    
    Test Steps:
        1. Initialization:
            - Set up mock chunks
        2. Input Values:
            - Test prompt: "Test prompt"
            - Mock chunks: ["Part 1", "Part 2"]
        3. Expected Output:
            - Combined text should be "Part 1Part 2"
        4. Cleanup:
            - None required
    """
    mock_chunk1 = Mock()
    mock_chunk1.text = "Part 1"
    mock_chunk2 = Mock()
    mock_chunk2.text = "Part 2"
    
    api_client.model.generate_content.return_value = [mock_chunk1, mock_chunk2]
    
    result = api_client.stream_generate_content("Test prompt")
    assert result == "Part 1Part 2"

def test_count_tokens(api_client):
    """
    Test Purpose:
        Verify that the client can accurately count tokens in input text.
    
    Tested Requirements:
        - Client must use model's token counting functionality
        - Client must return correct token count
    
    Test Steps:
        1. Initialization:
            - Set up mock token count response
        2. Input Values:
            - Test text: "Test text"
            - Mock token count: 10
        3. Expected Output:
            - Token count should be 10
        4. Cleanup:
            - None required
    """
    mock_count = Mock()
    mock_count.total_tokens = 10
    api_client.model.count_tokens.return_value = mock_count
    
    count = api_client.count_tokens("Test text")
    assert count == 10 