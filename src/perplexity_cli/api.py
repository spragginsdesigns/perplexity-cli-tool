"""Perplexity API integration for the CLI tool."""

import httpx
from typing import Dict, Any, Optional
import json
import sys
import unicodedata
from .config import load_config

PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"

async def query_perplexity(
    question: str,
    model: str = "mistral-7b-instruct"
) -> Dict[Any, Any]:
    """Query the Perplexity API with the given question.

    Args:
        question: The question to ask Perplexity
        model: The model to use for the query (default: mistral-7b-instruct)

    Returns:
        The JSON response from the API

    Raises:
        ValueError: If the API key is not configured
        httpx.HTTPStatusError: If the API request fails
    """
    config = load_config()

    if not config.api_key:
        raise ValueError(
            "Perplexity API key not configured. Run 'pplx configure' to set it up "
            "or set the PERPLEXITY_API_KEY environment variable."
        )

    headers = {
        "Authorization": f"Bearer {config.api_key}",
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json; charset=utf-8"
    }

    # Ensure question is properly encoded
    try:
        # Ensure the question is properly encoded as UTF-8
        if isinstance(question, str):
            # Normalize Unicode characters and ensure proper UTF-8 encoding
            question = unicodedata.normalize('NFC', question)
    except Exception as e:
        # If encoding fails, log the error and continue with the original question
        print(f"Warning: Encoding issue with question: {e}", file=sys.stderr)

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": question}]
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                PERPLEXITY_API_URL,
                headers=headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()

            # Get the response JSON
            response_json = response.json()

            # Process the response content to ensure it's properly encoded
            if "choices" in response_json and response_json["choices"] and "message" in response_json["choices"][0]:
                content = response_json["choices"][0]["message"].get("content", "")
                if content:
                    # Normalize Unicode characters
                    try:
                        content = unicodedata.normalize('NFKC', content)
                        # Replace the content with the normalized version
                        response_json["choices"][0]["message"]["content"] = content
                    except Exception:
                        # If normalization fails, continue with the original content
                        pass

            return response_json
        except UnicodeDecodeError as e:
            # Handle Unicode decoding errors
            raise ValueError(f"Unicode error in API response: {str(e)}. Try a different question.")
        except httpx.HTTPStatusError as e:
            # Provide more detailed error information
            error_msg = f"API request failed with status {e.response.status_code}"
            try:
                error_data = e.response.json()
                if "error" in error_data:
                    error_msg += f": {error_data['error']}"
            except Exception:
                pass
            raise ValueError(error_msg)