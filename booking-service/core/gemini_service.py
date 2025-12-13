"""Gemini LLM service for processing HTML content."""

import os
import json
import logging
from typing import Optional, Union, Dict, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Get Gemini API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

try:
    import google.generativeai as genai
    
    # Configure Gemini API
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
    else:
        logger.warning("GEMINI_API_KEY not found in environment variables. Gemini service will not be available.")
except ImportError:
    logger.warning("google-generativeai package not installed. Install it with: pip install google-generativeai")
    genai = None


class GeminiService:
    """Service for interacting with Google's Gemini LLM."""
    
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        """
        Initialize Gemini service.
        
        Args:
            model_name: Name of the Gemini model to use (default: gemini-1.5-flash)
        """
        if genai is None:
            raise ImportError("google-generativeai package is not installed. Install it with: pip install google-generativeai")
        
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set in environment variables")
        
        self.model_name = model_name
        try:
            self.model = genai.GenerativeModel(model_name)
            logger.info(f"Initialized Gemini model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {str(e)}")
            raise
    
    def process_html(
        self,
        html_content: str,
        prompt: Optional[str] = None,
        max_output_tokens: int = 8192,
        temperature: float = 0.7,
        parse_json: bool = True,
    ) -> Union[str, Dict, List]:
        """
        Process HTML content using Gemini LLM.
        
        Args:
            html_content: The HTML content to process
            prompt: Optional custom prompt. If not provided, uses a default prompt
            max_output_tokens: Maximum number of tokens in the response
            temperature: Sampling temperature (0.0 to 1.0)
            parse_json: If True, attempts to parse JSON from the response
        
        Returns:
            str, dict, or list: The LLM's response (parsed as JSON if parse_json=True)
        """
        if not html_content:
            raise ValueError("HTML content cannot be empty")
        
        try:
            # Generate content
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_output_tokens,
            }
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            response_text = response.text
            
            # If parse_json is True, try to extract and parse JSON
            if parse_json:
                try:
                    parsed = self._extract_json_from_response(response_text)
                    return parsed
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"Failed to parse JSON from Gemini response: {str(e)}")
                    # Return raw text if parsing fails
                    return response_text
            
            return response_text
        
        except Exception as e:
            logger.error(f"Error processing HTML with Gemini: {str(e)}")
            raise
    
    def _extract_json_from_response(self, response_text: str) -> Union[Dict, List]:
        """
        Extract and parse JSON from Gemini response, handling markdown code blocks.
        
        Args:
            response_text: The raw response text from Gemini
        
        Returns:
            dict or list: Parsed JSON object
        """
        text = response_text.strip()
        
        # Remove markdown code blocks if present
        if text.startswith("```"):
            # Find the closing ```
            lines = text.split("\n")
            # Remove first line (```json or ```)
            if len(lines) > 1:
                lines = lines[1:]
            # Remove last line if it's ```
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines).strip()
        
        # Try to find JSON array or object
        # Look for first { or [
        start_idx = -1
        for i, char in enumerate(text):
            if char in ['{', '[']:
                start_idx = i
                break
        
        if start_idx != -1:
            text = text[start_idx:]
            # Find matching closing bracket
            bracket_stack = []
            end_idx = -1
            for i, char in enumerate(text):
                if char in ['{', '[']:
                    bracket_stack.append(char)
                elif char in ['}', ']']:
                    if bracket_stack:
                        bracket_stack.pop()
                        if not bracket_stack:
                            end_idx = i + 1
                            break
            
            if end_idx != -1:
                text = text[:end_idx]
        
        # Parse JSON
        return json.loads(text)
    


def get_gemini_service(model_name: str = "gemini-1.5-flash") -> Optional[GeminiService]:
    """
    Get or create a Gemini service instance.
    
    Args:
        model_name: Name of the Gemini model to use
    
    Returns:
        GeminiService instance or None if not available
    """
    try:
        return GeminiService(model_name=model_name)
    except (ImportError, ValueError) as e:
        logger.warning(f"Gemini service not available: {str(e)}")
        return None

