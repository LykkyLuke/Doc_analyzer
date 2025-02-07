from typing import List, Optional, Callable
from queue import Queue
import threading
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from logging_config import get_logger
import uuid
import time

class SummarizationEngine:
    """Handles document summarization using chunk processing and aggregation."""
    
    def __init__(self, api_client, config_handler):
        """Initialize the summarization engine."""
        self.logger = get_logger(__name__)
        self.logger.info("Initializing SummarizationEngine")
        
        self.api_client = api_client
        self.config = config_handler
        self.chunk_queue = Queue()
        self.progress_callback = None
        self.total_chunks = 0
        self.processed_chunks = 0
        
        self.logger.debug("SummarizationEngine initialized successfully")
    
    def set_progress_callback(self, callback: Callable[[int, int], None]) -> None:
        """Set callback for progress updates."""
        self.logger.debug("Setting progress callback")
        self.progress_callback = callback
    
    def _update_progress(self) -> None:
        """Update progress through callback if set."""
        self.processed_chunks += 1
        if self.progress_callback:
            self.progress_callback(self.processed_chunks, self.total_chunks)
            self.logger.debug(f"Progress updated: {self.processed_chunks}/{self.total_chunks}")
    
    def process_chunks(self, chunks: List[str], max_workers: int = 2) -> List[str]:
        """Process multiple chunks concurrently.
        
        Using max_workers=2 to stay well within rate limits while maintaining some parallelism.
        Each worker will respect the rate limit independently through the API client.
        """
        request_id = str(uuid.uuid4())
        self.logger.info(f"Starting chunk processing (request_id: {request_id})")
        self.logger.debug(f"Number of chunks: {len(chunks)}, max_workers: {max_workers}")
        
        self.total_chunks = len(chunks)
        self.processed_chunks = 0
        chunk_summaries = []
        
        prompt_template = """
        Please provide a concise summary of the following text, capturing the main points and key information:
        
        {text}
        
        Summary (be thorough but concise):
        """
        
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Process chunks in batches to better control rate limiting
            batch_size = 5  # Process 5 chunks at a time
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                self.logger.debug(f"Processing batch {i//batch_size + 1} of {(len(chunks) + batch_size - 1)//batch_size}")
                
                future_to_chunk = {
                    executor.submit(
                        self._process_single_chunk, 
                        chunk, 
                        prompt_template,
                        request_id
                    ): idx for idx, chunk in enumerate(batch, start=i)
                }
                
                for future in as_completed(future_to_chunk):
                    try:
                        summary = future.result()
                        if summary:
                            chunk_summaries.append((future_to_chunk[future], summary))
                        self._update_progress()
                    except Exception as e:
                        self.logger.error(
                            f"Error processing chunk (request_id: {request_id}): {str(e)}",
                            exc_info=True
                        )
                        raise
        
        end_time = time.time()
        duration = end_time - start_time
        self.logger.info(
            f"Chunk processing completed (request_id: {request_id}, "
            f"duration: {duration:.2f}s)"
        )
        
        # Sort summaries by original chunk order
        return [summary for _, summary in sorted(chunk_summaries)]
    
    def _process_single_chunk(self, chunk: str, prompt_template: str, request_id: str) -> Optional[str]:
        """Process a single chunk and return its summary."""
        chunk_id = str(uuid.uuid4())
        self.logger.debug(
            f"Processing chunk (request_id: {request_id}, chunk_id: {chunk_id}), "
            f"size: {len(chunk)} characters"
        )
        
        try:
            prompt = prompt_template.format(text=chunk)
            start_time = time.time()
            summary = self.api_client.generate_content(prompt)
            end_time = time.time()
            
            if summary:
                self.logger.debug(
                    f"Chunk processed successfully (request_id: {request_id}, "
                    f"chunk_id: {chunk_id}, duration: {end_time - start_time:.2f}s)"
                )
            return summary
        except Exception as e:
            self.logger.error(
                f"Failed to process chunk (request_id: {request_id}, "
                f"chunk_id: {chunk_id}): {str(e)}",
                exc_info=True
            )
            return None
    
    def generate_final_summary(self, chunk_summaries: List[str]) -> str:
        """Generate final summary from chunk summaries."""
        request_id = str(uuid.uuid4())
        self.logger.info(f"Generating final summary (request_id: {request_id})")
        self.logger.debug(f"Number of chunk summaries: {len(chunk_summaries)}")
        
        combined_summaries = "\n\n".join(chunk_summaries)
        
        final_prompt = """
        Please create a coherent and concise final summary from these section summaries:
        
        {summaries}
        
        Final Summary:
        """.format(summaries=combined_summaries)
        
        try:
            start_time = time.time()
            summary = self.api_client.generate_content(final_prompt)
            end_time = time.time()
            
            self.logger.info(
                f"Final summary generated successfully (request_id: {request_id}, "
                f"duration: {end_time - start_time:.2f}s)"
            )
            return summary
        except Exception as e:
            self.logger.error(
                f"Failed to generate final summary (request_id: {request_id}): {str(e)}",
                exc_info=True
            )
            raise
    
    def summarize_document(self, chunks: List[str]) -> str:
        """Summarize a document by processing chunks and generating a final summary."""
        request_id = str(uuid.uuid4())
        self.logger.info(f"Starting document summarization (request_id: {request_id})")
        
        try:
            # Process chunks and get summaries
            self.logger.debug(f"Processing {len(chunks)} chunks (request_id: {request_id})")
            chunk_summaries = self.process_chunks(chunks)
            if not chunk_summaries:
                error_msg = "Failed to process document chunks"
                self.logger.error(f"{error_msg} (request_id: {request_id})")
                return f"Failed to generate summary: {error_msg}"
            
            # Generate final summary
            self.logger.debug(f"Generating final summary from {len(chunk_summaries)} chunk summaries (request_id: {request_id})")
            final_summary = self.generate_final_summary(chunk_summaries)
            if not final_summary:
                error_msg = "Error in final summarization"
                self.logger.error(f"{error_msg} (request_id: {request_id})")
                return f"Failed to generate summary: {error_msg}"
            
            self.logger.info(f"Document summarization completed successfully (request_id: {request_id})")
            return final_summary
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(
                f"Failed to summarize document (request_id: {request_id}): {error_msg}",
                exc_info=True
            )
            return f"Failed to generate summary: {error_msg}" 