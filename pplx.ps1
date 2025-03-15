# PowerShell script for Perplexity CLI
param([Parameter(ValueFromRemainingArguments = $true)]$args)

# Set UTF-8 encoding for PowerShell
try {
  # Force UTF-8 for PowerShell
  [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
  [Console]::InputEncoding = [System.Text.Encoding]::UTF8

  # Set environment variables for Python
  $env:PYTHONIOENCODING = "utf-8"
  $env:PYTHONLEGACYWINDOWSSTDIO = "0"

  # Set code page to UTF-8 (65001)
  chcp 65001 > $null
}
catch {
  Write-Warning "Could not set UTF-8 encoding: $_"
}

# Define possible Python paths in order of preference
$pythonPaths = @(
  "$PSScriptRoot\.venv\Scripts\python.exe",
  "C:\Python312\python.exe", # Adjust version number as needed
  "C:\Python311\python.exe",
  "C:\Python310\python.exe",
  "C:\Python39\python.exe",
  "C:\Program Files\Python312\python.exe",
  "C:\Program Files\Python311\python.exe",
  "C:\Program Files\Python310\python.exe",
  "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
  "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
  "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe"
)

# Find the first Python executable that exists
$pythonExe = $null
foreach ($path in $pythonPaths) {
  if (Test-Path $path) {
    $pythonExe = $path
    break
  }
}

# If no Python executable was found, try using the system Python
if ($null -eq $pythonExe) {
  try {
    # Try to find Python in the PATH
    $pythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source
  }
  catch {
    # If that fails, show an error message
    Write-Host "Error: Could not find Python. Please install Python or specify the full path in your PowerShell profile." -ForegroundColor Red
    exit 1
  }
}

# Run the CLI tool with the provided arguments
try {
  # Use the Python executable we found
  & $pythonExe "$PSScriptRoot\pplx.py" $args
}
catch {
  Write-Error "Error running Perplexity CLI: $_"
  Write-Host "Try running directly with: $pythonExe $PSScriptRoot\pplx.py $args"
}