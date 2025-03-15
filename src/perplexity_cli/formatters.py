"""Output formatting for Perplexity CLI responses."""

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from typing import Dict, Any, Optional
import sys
import unicodedata

# Initialize console without the encoding parameter
console = Console(highlight=True, emoji=True, force_terminal=True)

def format_response(response_data: Dict[Any, Any], show_raw: bool = False) -> None:
    """Format and print the API response.

    Args:
        response_data: The JSON response from the Perplexity API
        show_raw: Whether to show the raw JSON response
    """
    if show_raw:
        console.print(Panel(
            Syntax(str(response_data), "json", theme="monokai", word_wrap=True),
            title="Raw API Response",
            border_style="dim"
        ))
        return

    try:
        content = response_data["choices"][0]["message"]["content"]
        model = response_data.get("model", "Unknown model")

        # Normalize Unicode characters to ensure compatibility
        try:
            content = unicodedata.normalize('NFKC', content)
        except Exception:
            # If normalization fails, continue with the original content
            pass

        # Print a header with model info
        console.print(f"[bold blue]Response from {model}[/bold blue]")
        console.print("─" * console.width)

        # Print the formatted response
        try:
            console.print(Markdown(content))
        except UnicodeEncodeError:
            # Fallback to ASCII-only output if Unicode fails
            ascii_content = content.encode('ascii', 'replace').decode('ascii')
            console.print(f"[bold yellow]Note: Some characters couldn't be displayed properly.[/bold yellow]")
            console.print(Markdown(ascii_content))
    except (KeyError, IndexError) as e:
        console.print("[bold red]Error parsing response from Perplexity API[/bold red]")
        console.print(f"Error details: {str(e)}")
        console.print(response_data)