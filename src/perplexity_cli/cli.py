"""Command line interface for Perplexity CLI."""

import asyncio
import typer
import sys
import io
import locale
from typing import Optional, List
from rich.console import Console
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table
import platform

from .api import query_perplexity
from .config import load_config, save_config, Config
from .formatters import format_response
from .encoding_debug import print_encoding_info

# Set default encoding to UTF-8 using reconfigure (Python 3.7+)
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except AttributeError:
    # Fallback for older Python versions
    locale.setlocale(locale.LC_ALL, '')
    if locale.getpreferredencoding().upper() != 'UTF-8':
        # Force UTF-8 encoding for all I/O operations
        try:
            # For Windows, try to set the console code page to UTF-8
            if sys.platform == 'win32':
                import subprocess
                subprocess.run(['chcp', '65001'], shell=True, check=False, capture_output=True)

            # Wrap stdout and stderr with UTF-8 encoding
            if hasattr(sys.stdout, 'buffer'):
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            if hasattr(sys.stderr, 'buffer'):
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
        except Exception as e:
            # If we can't set the encoding, just log it and continue
            print(f"Warning: Could not set UTF-8 encoding: {e}")

app = typer.Typer(help="CLI tool for querying Perplexity API")
console = Console(highlight=True, emoji=True, force_terminal=True)

@app.callback()
def callback():
    """Query Perplexity AI from your terminal."""
    pass

@app.command()
def ask(
    question: List[str] = typer.Argument(None, help="The question to ask Perplexity"),
    model: str = typer.Option("sonar-pro", "--model", "-m", help="The model to use"),
    raw: bool = typer.Option(False, "--raw", "-r", help="Show raw JSON response")
):
    """Ask a question to Perplexity API.

    Examples:
        pplx ask "What is the capital of France?"
        pplx ask What is the capital of France?
        pplx ask -m sonar-reasoning "Explain quantum computing"
    """
    if not question:
        # If no question is provided, show help
        typer.echo(app.info.help)
        return

    # Join all arguments into a single question string
    full_question = " ".join(question)

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]Querying Perplexity AI...[/bold blue]"),
        transient=True,
    ) as progress:
        progress.add_task("query", total=None)
        try:
            response = asyncio.run(query_perplexity(full_question, model=model))
            format_response(response, show_raw=raw)
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")

@app.command()
def configure():
    """Configure the Perplexity API key."""
    config = load_config()

    # Show current configuration
    if config.api_key:
        masked_key = f"{config.api_key[:5]}{'*' * (len(config.api_key) - 9)}{config.api_key[-4:]}"
        console.print(f"[bold]Current API key:[/bold] {masked_key}")
    else:
        console.print("[bold yellow]No API key configured[/bold yellow]")

    # Prompt for new API key
    api_key = Prompt.ask(
        "Enter your Perplexity API key (press Enter to keep current)",
        password=True,
        default=config.api_key
    )

    if api_key != config.api_key:
        config.api_key = api_key
        save_config(config)
        console.print("[bold green]API key saved successfully![/bold green]")
    else:
        console.print("Configuration unchanged.")

@app.command()
def models():
    """List available Perplexity models."""
    console.print("[bold]Available Perplexity Models:[/bold]")

    # Create a table for better formatting
    table = Table(show_header=True)
    table.add_column("Model", style="cyan")
    table.add_column("Context Length", style="green")
    table.add_column("Description", style="yellow")

    # Add models from the documentation
    table.add_row("sonar-pro", "200k", "Premier search offering with search grounding, supporting advanced queries and follow-ups")
    table.add_row("sonar", "128k", "Lightweight offering with search grounding, quicker and cheaper than Sonar Pro")
    table.add_row("sonar-reasoning-pro", "128k", "Premier reasoning offering powered by DeepSeek R1 with Chain of Thought (CoT)")
    table.add_row("sonar-reasoning", "128k", "Reasoning model with Chain of Thought (CoT)")
    table.add_row("sonar-deep-research", "128k", "Performs exhaustive research across many sources with expert-level analysis")
    table.add_row("r1-1776", "128k", "DeepSeek R1 model post-trained for uncensored, unbiased information (no search)")

    console.print(table)

    console.print("\n[italic]Use with the --model option:[/italic]")
    console.print("  pplx ask --model sonar-reasoning \"Your question here\"")

@app.command()
def debug():
    """Show debugging information for troubleshooting."""
    console.print(Panel("Debugging Information", expand=False))

    # Print Python version
    console.print(f"Python Version: {sys.version}")

    # Print encoding information
    print_encoding_info()

    # Test rich output with Unicode
    console.print("Testing Rich Unicode Output:")
    console.print("Unicode test: àáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ")

    # Test API key configuration
    config = load_config()
    if config.api_key:
        masked_key = f"{config.api_key[:5]}{'*' * (len(config.api_key) - 9)}{config.api_key[-4:]}"
        console.print("Testing API Connection:")
        console.print(f"API Key configured: {masked_key}")
    else:
        console.print("[bold yellow]No API key configured[/bold yellow]")

if __name__ == "__main__":
    app()