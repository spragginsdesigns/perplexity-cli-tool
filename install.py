#!/usr/bin/env python
"""
Installation script for Perplexity CLI.
This script installs the CLI tool globally so it can be used from anywhere.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import importlib.util

def check_module_installed(module_name):
    """Check if a Python module is installed."""
    return importlib.util.find_spec(module_name) is not None

def main():
    """Install the Perplexity CLI tool."""
    print("Installing Perplexity CLI...")

    # Get the current directory
    current_dir = Path(__file__).parent.absolute()

    # Check if we're in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

    if in_venv:
        print("Running in a virtual environment.")
    else:
        print("Not running in a virtual environment. Installing globally.")

    # Check if pip is available
    pip_available = check_module_installed("pip")

    if not pip_available:
        print("Warning: pip is not installed in this environment.")
        print("Attempting alternative installation method...")

        # Create a direct executable script instead
        try:
            # Create the pplx.py script in the current directory if it doesn't exist
            pplx_script = current_dir / "pplx.py"
            if not pplx_script.exists():
                with open(pplx_script, "w", encoding="utf-8") as f:
                    f.write('''#!/usr/bin/env python
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

# Import and run the CLI
from src.perplexity_cli.cli import app

if __name__ == "__main__":
    app()
''')
                print(f"Created direct Python script: {pplx_script}")

            # Create a batch file for Windows
            if sys.platform == "win32":
                # Create in the current directory
                batch_file = current_dir / "pplx.bat"
                with open(batch_file, "w") as f:
                    f.write(f'@echo off\r\n"{sys.executable}" "{pplx_script}" %*\r\n')

                print(f"Created batch file: {batch_file}")
                print("You can use this batch file directly from the current directory.")
                print("To use it from anywhere, add this directory to your PATH environment variable.")

            # Create a shell script for Unix-like systems
            else:
                shell_script = current_dir / "pplx"
                with open(shell_script, "w") as f:
                    f.write(f'#!/bin/sh\n"{sys.executable}" "{pplx_script}" "$@"\n')

                # Make it executable
                os.chmod(shell_script, 0o755)

                print(f"Created shell script: {shell_script}")
                print("You can use this script directly from the current directory.")
                print("To use it from anywhere, add this directory to your PATH environment variable.")

            print("\nAlternative installation complete!")
            print(f"You can run the tool with: python {pplx_script} ask \"Hello, world!\"")
            return
        except Exception as e:
            print(f"Error creating alternative installation: {e}")
            print("Please install pip in your environment and try again.")
            return

    # Install the package using pip
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], check=True)
        print("Package installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing package: {e}")
        print("\nTrying alternative installation method...")

        # Try to install required dependencies
        try:
            print("Installing required dependencies...")
            subprocess.run([
                sys.executable, "-m", "pip", "install",
                "typer>=0.9.0", "rich>=13.0.0", "httpx>=0.24.0", "pydantic>=2.0.0"
            ], check=True)
            print("Dependencies installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies: {e}")
            print("Please install the required dependencies manually:")
            print("  pip install typer rich httpx pydantic")

        # Create a direct executable script
        try:
            # Create the pplx.py script
            pplx_script = current_dir / "pplx.py"
            if not pplx_script.exists():
                with open(pplx_script, "w", encoding="utf-8") as f:
                    f.write('''#!/usr/bin/env python
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

# Import and run the CLI
from src.perplexity_cli.cli import app

if __name__ == "__main__":
    app()
''')

            print(f"Created direct Python script: {pplx_script}")
            print(f"You can run the tool with: python {pplx_script} ask \"Hello, world!\"")
            return
        except Exception as e:
            print(f"Error creating direct Python script: {e}")
            return

    # Create a batch file for Windows
    if sys.platform == "win32":
        try:
            # Get the Scripts directory
            scripts_dir = Path(sys.prefix) / "Scripts"
            scripts_dir.mkdir(exist_ok=True)

            # Create the batch file
            batch_file = scripts_dir / "pplx.bat"
            with open(batch_file, "w") as f:
                f.write(f'@echo off\r\n"{sys.executable}" "{current_dir / "pplx.py"}" %*\r\n')

            print(f"Created batch file: {batch_file}")
            print("You can now use 'pplx' from anywhere.")
        except Exception as e:
            print(f"Error creating batch file: {e}")
            print("You can still use the tool with: python pplx.py ask \"Hello, world!\"")

    # Create a symlink for Unix-like systems
    else:
        try:
            # Get the bin directory
            bin_dir = Path(sys.prefix) / "bin"
            bin_dir.mkdir(exist_ok=True)

            # Create the symlink
            symlink = bin_dir / "pplx"
            if symlink.exists():
                symlink.unlink()

            # Create a wrapper script
            with open(symlink, "w") as f:
                f.write(f'#!/bin/sh\n"{sys.executable}" "{current_dir / "pplx.py"}" "$@"\n')

            # Make it executable
            os.chmod(symlink, 0o755)

            print(f"Created executable script: {symlink}")
            print("You can now use 'pplx' from anywhere.")
        except Exception as e:
            print(f"Error creating symlink: {e}")
            print("You can still use the tool with: python pplx.py ask \"Hello, world!\"")

    print("\nInstallation complete!")
    print("Try running 'pplx ask \"Hello, world!\"'")
    print("If that doesn't work, you can always use: python pplx.py ask \"Hello, world!\"")

if __name__ == "__main__":
    main()