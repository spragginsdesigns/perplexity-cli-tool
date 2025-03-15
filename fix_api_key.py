#!/usr/bin/env python
"""
Script to fix the Perplexity API key by removing any non-ASCII characters.
"""

import json
import os
import unicodedata
from pathlib import Path

def sanitize_api_key(api_key):
    """Sanitize the API key to ensure it's ASCII-compatible."""
    if not api_key:
        return ""

    # First try to normalize the Unicode
    api_key = unicodedata.normalize('NFKD', api_key)

    # Then filter out any remaining non-ASCII characters
    return ''.join(c for c in api_key if ord(c) < 128)

def main():
    """Fix the API key in the config file."""
    config_dir = Path.home() / ".config" / "perplexity-cli"
    config_file = config_dir / "config.json"

    if not config_file.exists():
        print(f"Config file not found: {config_file}")
        return

    try:
        # Try different encodings to read the file
        encodings = ['utf-8', 'latin-1', 'cp1252', 'ascii']
        config = None

        for encoding in encodings:
            try:
                with open(config_file, "rb") as f:
                    content = f.read()
                    # Try to decode with the current encoding
                    decoded = content.decode(encoding, errors='replace')
                    config = json.loads(decoded)
                    print(f"Successfully read config with {encoding} encoding")
                    break
            except Exception as e:
                print(f"Failed to read with {encoding}: {e}")
                continue

        if config is None:
            # If all encodings fail, try a binary approach
            with open(config_file, "rb") as f:
                content = f.read()
                # Replace any non-ASCII bytes with spaces
                cleaned = bytes([b if b < 128 else ord(' ') for b in content])
                try:
                    config = json.loads(cleaned.decode('ascii', errors='replace'))
                    print("Used binary cleaning approach to read config")
                except Exception as e:
                    print(f"Binary approach failed: {e}")
                    # Last resort: create a new config
                    config = {"api_key": ""}
                    print("Creating a new config file")

        # Check if there's an API key
        if "api_key" not in config or not config["api_key"]:
            print("No API key found in config file or it's empty.")
            new_key = input("Enter your Perplexity API key: ").strip()
            if new_key:
                config["api_key"] = new_key
                print("New API key added.")

        # Get the current API key
        current_key = config.get("api_key", "")
        if current_key:
            masked_key = f"{current_key[:5]}{'*' * (len(current_key) - 9)}{current_key[-4:]}" if len(current_key) > 9 else "***"
            print(f"Current API key: {masked_key}")

            # Sanitize the API key
            sanitized_key = sanitize_api_key(current_key)

            if sanitized_key != current_key:
                # Update the config with the sanitized key
                config["api_key"] = sanitized_key
                masked_sanitized = f"{sanitized_key[:5]}{'*' * (len(sanitized_key) - 9)}{sanitized_key[-4:]}" if len(sanitized_key) > 9 else "***"
                print(f"API key updated: {masked_sanitized}")
            else:
                print("API key is already ASCII-compatible. No changes needed.")

        # Write the updated config
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f)
        print("Config file updated successfully.")

    except Exception as e:
        print(f"Error fixing API key: {e}")
        print("Try manually creating a new config file with:")
        print(f"mkdir -p {config_dir}")
        print(f"echo '{{\"api_key\": \"YOUR_API_KEY_HERE\"}}' > {config_file}")

if __name__ == "__main__":
    main()