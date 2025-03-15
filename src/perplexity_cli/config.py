"""Configuration management for Perplexity CLI."""

from pathlib import Path
import json
import os
import unicodedata
from pydantic import BaseModel

class Config(BaseModel):
    """Configuration model for Perplexity CLI."""
    api_key: str = ""

CONFIG_DIR = Path.home() / ".config" / "perplexity-cli"
CONFIG_FILE = CONFIG_DIR / "config.json"

def load_config() -> Config:
    """Load configuration from file or environment variables."""
    # First check environment variables
    env_api_key = os.environ.get("PERPLEXITY_API_KEY")

    if env_api_key:
        # Sanitize the API key to ensure it's ASCII-compatible
        env_api_key = sanitize_api_key(env_api_key)
        return Config(api_key=env_api_key)

    # Then check config file
    if not CONFIG_FILE.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        config = Config()
        save_config(config)
        return config

    try:
        # Try different encodings to read the file
        encodings = ['utf-8', 'latin-1', 'cp1252', 'ascii']
        config_data = None

        for encoding in encodings:
            try:
                with open(CONFIG_FILE, "rb") as f:
                    content = f.read()
                    # Try to decode with the current encoding
                    decoded = content.decode(encoding, errors='replace')
                    config_data = json.loads(decoded)
                    break
            except Exception:
                continue

        if config_data is None:
            # If all encodings fail, try a binary approach
            with open(CONFIG_FILE, "rb") as f:
                content = f.read()
                # Replace any non-ASCII bytes with spaces
                cleaned = bytes([b if b < 128 else ord(' ') for b in content])
                try:
                    config_data = json.loads(cleaned.decode('ascii', errors='replace'))
                except Exception:
                    # Last resort: create a new config
                    return Config()

        # Sanitize the API key if it exists
        if "api_key" in config_data and config_data["api_key"]:
            config_data["api_key"] = sanitize_api_key(config_data["api_key"])

        return Config.model_validate(config_data)
    except Exception as e:
        print(f"Warning: Could not load config: {e}")
        return Config()

def save_config(config: Config) -> None:
    """Save configuration to file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    # Sanitize the API key before saving
    if config.api_key:
        config.api_key = sanitize_api_key(config.api_key)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write(config.model_dump_json())

def sanitize_api_key(api_key: str) -> str:
    """Sanitize the API key to ensure it's ASCII-compatible.

    This removes any non-ASCII characters that might cause encoding issues.
    """
    if not api_key:
        return ""

    # First try to normalize the Unicode
    api_key = unicodedata.normalize('NFKD', api_key)

    # Then filter out any remaining non-ASCII characters
    return ''.join(c for c in api_key if ord(c) < 128)