#!/usr/bin/env python
"""
Direct Python entry point for Perplexity CLI.
This can be run with Python directly.
"""

import sys
import os

# Ensure UTF-8 encoding
os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.platform == "win32":
    os.environ["PYTHONLEGACYWINDOWSSTDIO"] = "0"

# Add the src directory to the Python path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Reconfigure stdout/stderr for UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

try:
    # Import and run the CLI
    from src.perplexity_cli.cli import app

    if __name__ == "__main__":
        app()
except ImportError as e:
    print(f"Error importing CLI module: {e}")
    print("\nMake sure you have the required dependencies installed:")
    print("  pip install typer rich httpx pydantic")
    print("\nIf you're in a virtual environment without pip, you can install it with:")
    print("  python -m ensurepip")
    print("  python -m pip install --upgrade pip")
    sys.exit(1)