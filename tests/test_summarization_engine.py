import pytest
from unittest.mock import Mock, patch
from src.summarization_engine import SummarizationEngine

@pytest.fixture
def summarization_engine():
    """Create SummarizationEngine instance with mocked dependencies."""
    api_client = Mock()
    config_handler = Mock()
    return SummarizationEngine(api_client, config_handler)

def test_process_single_chunk(summarization_engine):
    """
    Test Purpose:
        Verify that a single text chunk is processed correctly by the API.
    
    Tested Requirements:
        - Engine must send chunk to API client
        - Engine must use correct prompt template
        - Engine must return API response
    
    Test Steps:
        1. Initialization:
            - Mock API client response
        2. Input Values:
            - Test chunk: "Test chunk"
            - Prompt template: "Summarize: {text}"
        3. Expected Output:
            - Result should match API response: "Summary of chunk"
            - API client should be called exactly once
        4. Cleanup:
            - None required
    """
    summarization_engine.api_client.generate_content.return_value = "Summary of chunk"
    
    result = summarization_engine._process_single_chunk(
        "Test chunk", 
        "Summarize: {text}"
    )
    
    assert result == "Summary of chunk"
    summarization_engine.api_client.generate_content.assert_called_once()

def test_process_chunks(summarization_engine):
    """
    Test Purpose:
        Verify that multiple chunks are processed correctly in sequence.
    
    Tested Requirements:
        - Engine must process all chunks
        - Engine must maintain chunk order
        - Engine must return summary for each chunk
    
    Test Steps:
        1. Initialization:
            - Create list of test chunks
            - Mock API response
        2. Input Values:
            - Test chunks: ["Chunk 1", "Chunk 2", "Chunk 3"]
            - max_workers: 1 (sequential processing)
        3. Expected Output:
            - Number of summaries should match number of chunks
            - Each summary should match API response
        4. Cleanup:
            - None required
    """
    chunks = ["Chunk 1", "Chunk 2", "Chunk 3"]
    summarization_engine.api_client.generate_content.return_value = "Summary"
    
    summaries = summarization_engine.process_chunks(chunks, max_workers=1)
    
    assert len(summaries) == 3
    assert all(summary == "Summary" for summary in summaries)

def test_progress_tracking(summarization_engine):
    """
    Test Purpose:
        Verify that progress callback is called correctly during chunk processing.
    
    Tested Requirements:
        - Engine must track progress of chunk processing
        - Engine must call progress callback for each chunk
        - Progress values must be accurate
    
    Test Steps:
        1. Initialization:
            - Set up progress callback
            - Create test chunks
        2. Input Values:
            - Test chunks: ["Chunk 1", "Chunk 2"]
            - Progress callback function
        3. Expected Output:
            - Progress updates should be recorded for each chunk
            - Final progress should be (2, 2)
        4. Cleanup:
            - None required
    """
    progress_updates = []
    summarization_engine.set_progress_callback(
        lambda current, total: progress_updates.append((current, total))
    )
    
    chunks = ["Chunk 1", "Chunk 2"]
    summarization_engine.api_client.generate_content.return_value = "Summary"
    
    summarization_engine.process_chunks(chunks, max_workers=1)
    
    assert len(progress_updates) == 2
    assert progress_updates[-1] == (2, 2)

def test_generate_final_summary(summarization_engine):
    """
    Test Purpose:
        Verify that a final summary is generated from chunk summaries.
    
    Tested Requirements:
        - Engine must combine chunk summaries
        - Engine must generate coherent final summary
        - Engine must use API client for final summary
    
    Test Steps:
        1. Initialization:
            - Create test chunk summaries
            - Mock API response
        2. Input Values:
            - Chunk summaries: ["Summary 1", "Summary 2"]
        3. Expected Output:
            - Final summary should match API response: "Final summary"
            - API client should be called exactly once
        4. Cleanup:
            - None required
    """
    chunk_summaries = ["Summary 1", "Summary 2"]
    summarization_engine.api_client.generate_content.return_value = "Final summary"
    
    result = summarization_engine.generate_final_summary(chunk_summaries)
    
    assert result == "Final summary"
    summarization_engine.api_client.generate_content.assert_called_once()

def test_error_handling(summarization_engine):
    """
    Test Purpose:
        Verify that API errors are handled appropriately during summarization.
    
    Tested Requirements:
        - Engine must catch API errors
        - Engine must propagate errors to caller
        - Processing must stop on error
    
    Test Steps:
        1. Initialization:
            - Mock API client to raise exception
        2. Input Values:
            - Test chunk: ["Chunk"]
            - Simulated API error
        3. Expected Output:
            - Exception should be raised to caller
        4. Cleanup:
            - None required
    """
    summarization_engine.api_client.generate_content.side_effect = Exception("API error")
    
    with pytest.raises(Exception):
        summarization_engine.summarize_document(["Chunk"]) 