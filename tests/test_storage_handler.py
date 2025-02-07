import pytest
from pathlib import Path
from src.storage_handler import StorageHandler

@pytest.fixture
def temp_config(tmp_path):
    """Create temporary config file for testing."""
    config_path = tmp_path / "config" / "config.json"
    return str(config_path)

def test_save_and_load_api_key(temp_config):
    """
    Test Purpose:
        Verify that API keys can be saved to and loaded from the configuration file.
    
    Tested Requirements:
        - API key must be saved to config file
        - API key must be retrievable from config file
        - Saved and loaded keys must match exactly
    
    Test Steps:
        1. Initialization:
            - Create StorageHandler with temporary config path
        2. Input Values:
            - Test API key: "test_api_key_123"
        3. Expected Output:
            - Loaded key should match saved key exactly
        4. Cleanup:
            - Temporary config file is cleaned up by pytest
    """
    handler = StorageHandler(temp_config)
    test_key = "test_api_key_123"
    
    # Save API key
    handler.save_api_key(test_key)
    
    # Load and verify
    loaded_key = handler.load_api_key()
    assert loaded_key == test_key

def test_load_nonexistent_config(temp_config):
    """
    Test Purpose:
        Verify that attempting to load from a nonexistent config file returns None.
    
    Tested Requirements:
        - Handler must handle missing config file gracefully
        - Handler must return None when config file doesn't exist
    
    Test Steps:
        1. Initialization:
            - Create StorageHandler with nonexistent config path
        2. Input Values:
            - Nonexistent config file path
        3. Expected Output:
            - load_api_key() should return None
        4. Cleanup:
            - None required
    """
    handler = StorageHandler(temp_config)
    assert handler.load_api_key() is None

def test_config_directory_creation(temp_config):
    """
    Test Purpose:
        Verify that the config directory is created if it doesn't exist.
    
    Tested Requirements:
        - Handler must create config directory if missing
        - Created directory must have correct path
    
    Test Steps:
        1. Initialization:
            - Create StorageHandler with path in nonexistent directory
        2. Input Values:
            - Config path in nonexistent directory
        3. Expected Output:
            - Config directory should exist after handler initialization
        4. Cleanup:
            - Temporary directory is cleaned up by pytest
    """
    handler = StorageHandler(temp_config)
    assert Path(temp_config).parent.exists() 