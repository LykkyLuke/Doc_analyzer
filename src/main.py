import logging
import uuid
from pathlib import Path
from storage_handler import StorageHandler
from document_processor import DocumentProcessor
from api_client import GeminiAPIClient
from summarization_engine import SummarizationEngine
from ui_handler import DocumentAnalyzerUI
from logging_config import setup_logging, get_logger, set_request_id, log_config

def main():
    """Initialize and run the Document Analyzer application."""
    # Set up logging
    setup_logging()
    logger = get_logger(__name__)
    
    # Generate main process ID
    main_process_id = str(uuid.uuid4())
    set_request_id(main_process_id)
    
    logger.info("Starting Document Analyzer")
    logger.info(f"Main process ID: {main_process_id}")
    
    try:
        # Initialize components
        logger.info("Initializing components")
        storage_handler = StorageHandler()
        
        # Log configuration (excluding sensitive data)
        config = storage_handler.load_config()
        log_config(config, logger)
        
        # Create API client without initializing connection
        logger.info("Creating API client")
        api_client = GeminiAPIClient(storage_handler)
        
        # Initialize document processor
        logger.info("Initializing document processor")
        document_processor = DocumentProcessor(storage_handler)
        
        # Initialize summarization engine
        logger.info("Initializing summarization engine")
        summarization_engine = SummarizationEngine(api_client, storage_handler)
        
        # Create and run UI
        logger.info("Starting UI")
        ui = DocumentAnalyzerUI(
            storage_handler,
            document_processor,
            summarization_engine
        )
        ui.run()
        
    except Exception as e:
        logger.error(f"Application failed to start: {str(e)}", exc_info=True)
        raise
    finally:
        logger.info("Application shutdown complete")

if __name__ == "__main__":
    main() 