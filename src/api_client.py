from typing import Optional, List
import google.generativeai as genai
import time
from logging_config import get_logger
import uuid
from threading import Lock

class GeminiAPIClient:
    """Handles communication with Google's Gemini API directly."""
    
    def __init__(self, config_handler):
        """Initialize the API client with configuration."""
        self.logger = get_logger(__name__)
        self.logger.info("Initializing GeminiAPIClient")
        
        self.config = config_handler
        config = self.config.load_config()
        
        # Configure the API
        genai.configure(api_key=config['api_key'])
        
        self.model_settings = config.get('model_settings', {
            'model': 'gemini-pro',
            'temperature': 0.7,
            'max_output_tokens': 2048,
            'top_p': 0.8,
            'top_k': 40,
            'rate_limit': {
                'requests_per_minute': 15,
                'minimum_delay': 4
            }
        })
        
        # Rate limiting setup
        self.rate_limit = self.model_settings.get('rate_limit', {
            'requests_per_minute': 15,
            'minimum_delay': 4
        })
        self.last_request_time = 0
        self.request_lock = Lock()
        
        self.logger.debug(f"Model settings loaded: {self.model_settings}")
        self.model = genai.GenerativeModel(self.model_settings['model'])
    
    def _wait_for_rate_limit(self):
        """Wait if necessary to comply with rate limits."""
        with self.request_lock:
            current_time = time.time()
            time_since_last_request = current_time - self.last_request_time
            
            if time_since_last_request < self.rate_limit['minimum_delay']:
                wait_time = self.rate_limit['minimum_delay'] - time_since_last_request
                self.logger.debug(f"Rate limit: waiting for {wait_time:.2f} seconds")
                time.sleep(wait_time)
            
            self.last_request_time = time.time()
    
    def generate_content(self, prompt: str) -> Optional[str]:
        """Generate content using Gemini model."""
        request_id = str(uuid.uuid4())
        self.logger.info(f"Starting content generation (request_id: {request_id})")
        self.logger.debug(f"Prompt (request_id: {request_id}): {prompt[:100]}...")
        
        generation_config = {
            'temperature': self.model_settings['temperature'],
            'max_output_tokens': self.model_settings['max_output_tokens'],
            'top_p': self.model_settings['top_p'],
            'top_k': self.model_settings['top_k']
        }
        
        retries = 3
        for attempt in range(retries):
            try:
                self.logger.debug(f"Attempt {attempt + 1}/{retries} (request_id: {request_id})")
                
                # Apply rate limiting
                self._wait_for_rate_limit()
                
                start_time = time.time()
                response = self.model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                end_time = time.time()
                duration = end_time - start_time
                
                self.logger.info(f"Content generated successfully (request_id: {request_id}, duration: {duration:.2f}s)")
                
                if response.text:
                    self.logger.debug(f"Response (request_id: {request_id}): {response.text[:100]}...")
                    return response.text
                return None
                
            except Exception as e:
                if attempt == retries - 1:
                    self.logger.error(
                        f"Failed to generate content after {retries} attempts "
                        f"(request_id: {request_id}): {str(e)}",
                        exc_info=True
                    )
                    raise
                self.logger.warning(
                    f"Attempt {attempt + 1} failed (request_id: {request_id}): {str(e)}. "
                    f"Retrying in {2 ** attempt} seconds..."
                )
                time.sleep(2 ** attempt)  # Exponential backoff
    
    def stream_generate_content(self, prompt: str) -> Optional[str]:
        """Generate content using streaming response."""
        request_id = str(uuid.uuid4())
        self.logger.info(f"Starting streaming content generation (request_id: {request_id})")
        self.logger.debug(f"Prompt (request_id: {request_id}): {prompt[:100]}...")
        
        try:
            start_time = time.time()
            response = self.model.generate_content(
                prompt,
                stream=True,
                generation_config=self.model_settings
            )
            
            chunks = []
            chunk_count = 0
            for chunk in response:
                if chunk.text:
                    chunks.append(chunk.text)
                    chunk_count += 1
                    self.logger.debug(f"Received chunk {chunk_count} (request_id: {request_id})")
            
            result = "".join(chunks)
            end_time = time.time()
            duration = end_time - start_time
            
            self.logger.info(
                f"Streaming content generated successfully "
                f"(request_id: {request_id}, chunks: {chunk_count}, duration: {duration:.2f}s)"
            )
            self.logger.debug(f"Final response (request_id: {request_id}): {result[:100]}...")
            
            return result
        except Exception as e:
            self.logger.error(
                f"Failed to stream content (request_id: {request_id}): {str(e)}",
                exc_info=True
            )
            raise
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in the input text."""
        try:
            self.logger.debug(f"Counting tokens for text: {text[:100]}...")
            response = self.model.count_tokens(text)
            token_count = response.total_tokens
            self.logger.debug(f"Token count: {token_count}")
            return token_count
        except Exception as e:
            self.logger.error(f"Failed to count tokens: {str(e)}", exc_info=True)
            return 0 