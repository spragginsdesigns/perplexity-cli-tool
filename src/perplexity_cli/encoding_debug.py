"""Utility module for debugging encoding issues."""

import sys
import locale
import os

def print_encoding_info():
    """Print information about the current encoding settings."""
    print("=== Python Encoding Information ===")
    print(f"Default Encoding: {sys.getdefaultencoding()}")
    print(f"Filesystem Encoding: {sys.getfilesystemencoding()}")
    print(f"Locale Encoding: {locale.getpreferredencoding()}")
    print(f"Stdout Encoding: {sys.stdout.encoding}")
    print(f"Stderr Encoding: {sys.stderr.encoding}")
    print(f"PYTHONIOENCODING: {os.environ.get('PYTHONIOENCODING', 'Not set')}")
    print(f"PYTHONLEGACYWINDOWSSTDIO: {os.environ.get('PYTHONLEGACYWINDOWSSTDIO', 'Not set')}")
    print("=== Test Unicode Characters ===")
    test_chars = "àáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ"
    print(f"Test Characters: {test_chars}")
    print("=== End of Encoding Information ===")

if __name__ == "__main__":
    print_encoding_info()