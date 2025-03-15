# Building a Perplexity CLI Tool for Windows

Goal: To build a clean, efficient CLI tool that lets you query Perplexity API directly from PowerShell with a simple command like `pplx "your question"`, or `perplexity "your question"` or something similar and easy to use.

## Project Structure

```
perplexity-cli/
├── pyproject.toml        # Project metadata and dependencies
├── README.md             # Documentation
├── src/
│   └── perplexity_cli/
│       ├── __init__.py   # Package initialization
│       ├── cli.py        # CLI entry point
│       ├── api.py        # Perplexity API interaction
│       ├── config.py     # Configuration management
│       └── formatters.py # Output formatting
└── tests/                # Test directory
```

## Development Plan

### 1. Setup Environment

```powershell
# Create project directory
mkdir perplexity-cli-tool
cd perplexity-cli-tool

# Setup virtual environment with UV (faster alternative to venv)
uv venv

# Activate environment
.\.venv\Scripts\Activate.ps1
```

### 2. Configure Dependencies

Create a `pyproject.toml`:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "perplexity-cli"
version = "0.1.0"
description = "CLI tool for querying Perplexity API"
readme = "README.md"
requires-python = ">=3.8"
license = { text = "MIT" }
dependencies = [
    "typer>=0.9.0",
    "httpx>=0.24.0",
    "rich>=13.4.2",
    "pydantic>=2.0.0",
]

[project.scripts]
pplx = "perplexity_cli.cli:app"
perplexity = "perplexity_cli.cli:app"

[tool.hatch.build.targets.wheel]
packages = ["src/perplexity_cli"]
```

Install dependencies:

```powershell
uv pip install -e .
```

### 3. Implement Core Components

#### `config.py` - Configuration Management

```python
from pathlib import Path
import json
from pydantic import BaseModel

class Config(BaseModel):
    api_key: str = ""

CONFIG_DIR = Path.home() / ".config" / "perplexity-cli"
CONFIG_FILE = CONFIG_DIR / "config.json"

def load_config() -> Config:
    if not CONFIG_FILE.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        config = Config()
        save_config(config)
        return config

    try:
        with open(CONFIG_FILE, "r") as f:
            return Config.model_validate(json.load(f))
    except Exception:
        return Config()

def save_config(config: Config) -> None:
    with open(CONFIG_FILE, "w") as f:
        f.write(config.model_dump_json())
```

#### `api.py` - Perplexity API Integration

```python
import httpx
from typing import Dict, Any
from .config import load_config

PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"

async def query_perplexity(question: str) -> Dict[Any, Any]:
    """Query the Perplexity API with the given question."""
    config = load_config()

    if not config.api_key:
        raise ValueError("Perplexity API key not configured. Run 'pplx --configure' to set it up.")

    headers = {
        "Authorization": f"Bearer {config.api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistral-7b-instruct",  # Or the model you prefer
        "messages": [{"role": "user", "content": question}]
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            PERPLEXITY_API_URL,
            headers=headers,
            json=payload,
            timeout=30.0
        )

        response.raise_for_status()
        return response.json()
```

#### `formatters.py` - Output Formatting

```python
from rich.console import Console
from rich.markdown import Markdown
from typing import Dict, Any

console = Console()

def format_response(response_data: Dict[Any, Any]) -> None:
    """Format and print the API response."""
    try:
        content = response_data["choices"][0]["message"]["content"]
        console.print(Markdown(content))
    except (KeyError, IndexError):
        console.print("[bold red]Error parsing response from Perplexity API[/bold red]")
        console.print(response_data)
```

#### `cli.py` - Command Line Interface

```python
import asyncio
import typer
from typing import Optional
from rich.console import Console
from rich.prompt import Prompt

from .api import query_perplexity
from .config import load_config, save_config, Config
from .formatters import format_response

app = typer.Typer(help="CLI tool for querying Perplexity API")
console = Console()

@app.callback()
def callback():
    """Query Perplexity AI from your terminal."""
    pass

@app.command()
def ask(
    question: str = typer.Argument(..., help="The question to ask Perplexity")
):
    """Ask a question to Perplexity API."""
    try:
        response = asyncio.run(query_perplexity(question))
        format_response(response)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")

@app.command()
def configure():
    """Configure the Perplexity API key."""
    config = load_config()
    current = f"Current API key: {config.api_key[:5]}..." if config.api_key else "No API key configured"
    console.print(f"[bold]Perplexity CLI Configuration[/bold]\n{current}")

    api_key = Prompt.ask("Enter your Perplexity API key", password=True)
    config.api_key = api_key
    save_config(config)
    console.print("[bold green]API key saved successfully![/bold green]")

if __name__ == "__main__":
    app()
```

### 4. Create PowerShell Integration

Create a PowerShell profile extension to allow typing `pplx` directly:

```powershell
# Save this to a file and then add it to your PowerShell profile
function pplx {
    param([string]$question)
    if ($question) {
        & python -m perplexity_cli.cli ask $question
    } else {
        & python -m perplexity_cli.cli
    }
}
```

### 5. Build and Install

```powershell
# Install in development mode
pip install -e .

# For distribution
python -m build
pip install dist/perplexity_cli-0.1.0-py3-none-any.whl
```

## Usage

```powershell
# Configure API key first
pplx --configure

# Ask questions
pplx "What is the capital of France?"
perplexity "Explain quantum computing in simple terms"
```

## Enhancement Ideas

1. Add caching for repeated queries
2. Implement streaming responses
3. Add support for different Perplexity models
4. Create a colorful progress spinner during API requests
5. Add history feature to recall previous queries

This plan builds a clean, maintainable CLI tool that fits your development preferences and will work perfectly on Windows 11 with PowerShell.
