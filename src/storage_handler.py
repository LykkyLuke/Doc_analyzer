import json
import os
from pathlib import Path
from typing import Optional
from logging_config import get_logger

class StorageHandler:
    """Handles storage and retrieval of API keys and configuration."""
    
    def __init__(self, config_path: str = "config/config.json"):
        """Initialize the storage handler with config file path."""
        self.logger = get_logger(__name__)
        self.config_path = Path(config_path)
        self.logger.info(f"Initializing StorageHandler with config path: {config_path}")
        self._ensure_config_directory()
    
    def _ensure_config_directory(self) -> None:
        """Create config directory if it doesn't exist."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Ensured config directory exists: {self.config_path.parent}")
        except Exception as e:
            self.logger.error(f"Failed to create config directory: {str(e)}", exc_info=True)
            raise
    
    def save_api_key(self, api_key: str) -> None:
        """Save API key to config file."""
        self.logger.info("Saving API key to config file")
        try:
            config = self.load_config()
            config["api_key"] = api_key
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            self.logger.debug("API key saved successfully")
        except Exception as e:
            self.logger.error(f"Failed to save API key: {str(e)}", exc_info=True)
            raise
    
    def load_api_key(self) -> Optional[str]:
        """Load API key from config file."""
        self.logger.info("Loading API key from config file")
        config = self.load_config()
        api_key = config.get("api_key")
        self.logger.debug(f"API key {'found' if api_key else 'not found'} in config")
        return api_key
    
    def load_config(self) -> dict:
        """Load entire config file."""
        self.logger.debug(f"Loading config from: {self.config_path}")
        if not self.config_path.exists():
            self.logger.warning(f"Config file not found at: {self.config_path}")
            return {}
            
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.logger.debug("Config file loaded successfully")
                return config
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse config file: {str(e)}", exc_info=True)
            return {}
        except Exception as e:
            self.logger.error(f"Unexpected error loading config: {str(e)}", exc_info=True)
            raise
