import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime
import json
from typing import Optional

class RequestIdFilter(logging.Filter):
    """Filter that adds request_id to all log records."""
    def __init__(self, request_id: Optional[str] = None):
        super().__init__()
        self.request_id = request_id or "main"

    def filter(self, record):
        if not hasattr(record, 'request_id'):
            record.request_id = self.request_id
        return True

def setup_logging(log_dir: str = "logs", log_level: int = logging.INFO) -> None:
    """Configure application-wide logging with file and console output."""
    # Create logs directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Generate log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = log_path / f"document_analyzer_{timestamp}.log"
    error_log_file = log_path / f"document_analyzer_error_{timestamp}.log"

    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - [%(request_id)s] - %(name)s - %(levelname)s - %(message)s',
        defaults={'request_id': 'main'}
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )

    # File handler for all logs
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(detailed_formatter)
    file_handler.setLevel(log_level)

    # File handler for error logs
    error_file_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    error_file_handler.setFormatter(detailed_formatter)
    error_file_handler.setLevel(logging.ERROR)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(log_level)

    # Get root logger and configure it
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add our handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_file_handler)
    root_logger.addHandler(console_handler)

    # Add request ID filter to root logger
    root_logger.addFilter(RequestIdFilter())

def log_config(config: dict, logger: logging.Logger) -> None:
    """Log configuration settings (excluding sensitive data)."""
    safe_config = config.copy()
    if 'api_key' in safe_config:
        safe_config['api_key'] = '***'
    logger.info(f"Configuration loaded: {json.dumps(safe_config, indent=2)}")

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name."""
    return logging.getLogger(name)

def set_request_id(request_id: str) -> None:
    """Set the request ID for the current context."""
    root_logger = logging.getLogger()
    for filter_ in root_logger.filters:
        if isinstance(filter_, RequestIdFilter):
            filter_.request_id = request_id
            break 