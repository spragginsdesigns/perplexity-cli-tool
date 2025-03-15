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

@app.command()
def help(
    command: Optional[str] = typer.Argument(None, help="Command to get help for")
):
    """Show help information for commands.

    If no command is specified, shows general help.
    """
    if command is None:
        # Show general help
        console.print("[bold]Perplexity CLI Help[/bold]")
        console.print("A command-line interface for querying the Perplexity AI API.\n")

        # Create a table for commands
        table = Table(show_header=True)
        table.add_column("Command", style="cyan")
        table.add_column("Description", style="yellow")

        # Add commands to the table
        table.add_row("ask", "Ask a question to Perplexity AI")
        table.add_row("models", "List available Perplexity models")
        table.add_row("configure", "Configure your API key")
        table.add_row("debug", "Show debugging information")
        table.add_row("help", "Show this help information")

        console.print(table)

        console.print("\n[bold]Usage:[/bold]")
        console.print("  pplx [command] [options]")

        console.print("\n[bold]Examples:[/bold]")
        console.print("  pplx ask \"What is the capital of France?\"")
        console.print("  pplx ask --model sonar-reasoning \"Explain quantum computing\"")
        console.print("  pplx models")
        console.print("  pplx help ask")

        console.print("\n[bold]Options:[/bold]")
        console.print("  --help    Show help for a command")
        console.print("  --version Show version information")
    elif command == "ask":
        console.print("[bold]Help for 'ask' command:[/bold]")
        console.print("Ask a question to Perplexity AI.\n")

        console.print("[bold]Usage:[/bold]")
        console.print("  pplx ask [OPTIONS] QUESTION")

        console.print("\n[bold]Options:[/bold]")
        console.print("  -m, --model TEXT  The model to use (default: sonar-pro)")
        console.print("  -r, --raw         Show raw JSON response")
        console.print("  --help            Show this message and exit")

        console.print("\n[bold]Examples:[/bold]")
        console.print("  pplx ask \"What is the capital of France?\"")
        console.print("  pplx ask What is the capital of France?")
        console.print("  pplx ask --model sonar-reasoning \"Explain quantum computing\"")
        console.print("  pplx ask --raw \"What is the speed of light?\"")
    elif command == "models":
        console.print("[bold]Help for 'models' command:[/bold]")
        console.print("List available Perplexity models.\n")

        console.print("[bold]Usage:[/bold]")
        console.print("  pplx models [OPTIONS]")

        console.print("\n[bold]Options:[/bold]")
        console.print("  --help  Show this message and exit")

        console.print("\n[bold]Examples:[/bold]")
        console.print("  pplx models")
    elif command == "configure":
        console.print("[bold]Help for 'configure' command:[/bold]")
        console.print("Configure the Perplexity API key.\n")

        console.print("[bold]Usage:[/bold]")
        console.print("  pplx configure [OPTIONS]")

        console.print("\n[bold]Options:[/bold]")
        console.print("  --help  Show this message and exit")

        console.print("\n[bold]Examples:[/bold]")
        console.print("  pplx configure")
    elif command == "debug":
        console.print("[bold]Help for 'debug' command:[/bold]")
        console.print("Show debugging information for troubleshooting.\n")

        console.print("[bold]Usage:[/bold]")
        console.print("  pplx debug [OPTIONS]")

        console.print("\n[bold]Options:[/bold]")
        console.print("  --help  Show this message and exit")

        console.print("\n[bold]Examples:[/bold]")
        console.print("  pplx debug")
    elif command == "help":
        console.print("[bold]Help for 'help' command:[/bold]")
        console.print("Show help information for commands.\n")

        console.print("[bold]Usage:[/bold]")
        console.print("  pplx help [COMMAND]")

        console.print("\n[bold]Arguments:[/bold]")
        console.print("  COMMAND  Command to get help for")

        console.print("\n[bold]Options:[/bold]")
        console.print("  --help  Show this message and exit")

        console.print("\n[bold]Examples:[/bold]")
        console.print("  pplx help")
        console.print("  pplx help ask")
    else:
        console.print(f"[bold red]Error:[/bold red] Unknown command '{command}'")
        console.print("Run 'pplx help' to see available commands.")

if __name__ == "__main__":
    app()