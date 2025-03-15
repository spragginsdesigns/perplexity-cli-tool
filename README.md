# Perplexity CLI

A clean, efficient command-line interface for querying the Perplexity AI API directly from your terminal.

## Features

- Simple command-line interface: `pplx ask "your question"`
- Support for all official Perplexity AI models (sonar-pro, sonar-reasoning, etc.)
- Beautiful, formatted output with Markdown rendering
- Configuration management for API keys
- Environment variable support for CI/CD integration

## Windows Setup (Quick Start)

The tool is already set up on your Windows machine. You can use it from anywhere in PowerShell with:

```powershell
pplx ask "Your question here"
```

This works because:

1. The PowerShell profile has been updated with a `pplx` function
2. The script automatically finds Python on your system

## Usage

### Getting Help

There are two ways to get help:

1. Using the `help` command:

```powershell
# General help
pplx help

# Help for a specific command
pplx help ask
pplx help models
```

2. Using the `--help` flag:

```powershell
# General help
pplx --help

# Help for a specific command
pplx ask --help
pplx models --help
```

Both methods provide similar information, but the `help` command offers more detailed examples and usage information.

### Configuration

Your API key is already configured. If you need to update it:

```powershell
pplx configure
```

Alternatively, you can set the `PERPLEXITY_API_KEY` environment variable.

### Asking Questions

```powershell
# Basic usage
pplx ask "What is the capital of France?"

# You can also omit the quotes if your question doesn't contain special characters
pplx ask What is the capital of France?

# Use a specific model
pplx ask --model sonar-reasoning "Explain quantum computing in simple terms"

# Show raw JSON response
pplx ask --raw "What is the speed of light?"
```

### Listing Available Models

```powershell
pplx models
```

## Available Models

The following models are available from Perplexity AI:

| Model               | Context Length | Description                                                                               |
| ------------------- | -------------- | ----------------------------------------------------------------------------------------- |
| sonar-pro           | 200k           | Premier search offering with search grounding, supporting advanced queries and follow-ups |
| sonar               | 128k           | Lightweight offering with search grounding, quicker and cheaper than Sonar Pro            |
| sonar-reasoning-pro | 128k           | Premier reasoning offering powered by DeepSeek R1 with Chain of Thought (CoT)             |
| sonar-reasoning     | 128k           | Reasoning model with Chain of Thought (CoT)                                               |
| sonar-deep-research | 128k           | Performs exhaustive research across many sources with expert-level analysis               |
| r1-1776             | 128k           | DeepSeek R1 model post-trained for uncensored, unbiased information (no search)           |

## How It Works

The tool is set up in your PowerShell profile (`$PROFILE`) with a function that:

1. Finds Python on your system (checking multiple possible locations)
2. Runs the Perplexity CLI script with the found Python executable
3. Passes all arguments to the CLI script

The PowerShell script (`pplx.ps1`) also handles UTF-8 encoding to ensure proper display of Unicode characters.

## Troubleshooting

If you encounter any issues:

1. Run the debug command to check your environment:

   ```powershell
   pplx debug
   ```

2. Fix API key encoding issues:

   ```powershell
   python "C:\Users\Owner\Documents\Github_Repositories\perplexity-cli-tool\fix_api_key.py"
   ```

3. If the command stops working, check your PowerShell profile:

   ```powershell
   notepad $PROFILE
   ```

   Ensure the `pplx` function is present and correctly configured.

4. If you need to reinstall or update:
   ```powershell
   cd "C:\Users\Owner\Documents\Github_Repositories\perplexity-cli-tool"
   python install.py
   ```

## Command Reference

| Command     | Description                     | Example                                 |
| ----------- | ------------------------------- | --------------------------------------- |
| `ask`       | Ask a question to Perplexity AI | `pplx ask "What is quantum computing?"` |
| `models`    | List available models           | `pplx models`                           |
| `configure` | Configure your API key          | `pplx configure`                        |
| `debug`     | Show debugging information      | `pplx debug`                            |
| `help`      | Show detailed help information  | `pplx help` or `pplx help ask`          |
| `--help`    | Show help information           | `pplx --help` or `pplx ask --help`      |
| `--version` | Show version information        | `pplx --version`                        |

## Advanced Usage

### Using Different Models

For complex research questions:

```powershell
pplx ask --model sonar-deep-research "How have this year's US tariffs affected commodity prices around the world?"
```

For reasoning with step-by-step thinking:

```powershell
pplx ask --model sonar-reasoning "Explain how quantum computing works"
```

For quick factual questions:

```powershell
pplx ask --model sonar "What is the capital of France?"
```

### Using in Scripts

You can use the tool in PowerShell scripts:

```powershell
$question = "What is the population of New York City?"
$response = pplx ask $question
Write-Output "Response: $response"
```

## License

MIT
