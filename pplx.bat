@echo off

if exist "C:\Users\Owner\Documents\Github_Repositories\perplexity-cli-tool\.venv\Scripts\python.exe" (
    "C:\Users\Owner\Documents\Github_Repositories\perplexity-cli-tool\.venv\Scripts\python.exe" "C:\Users\Owner\Documents\Github_Repositories\perplexity-cli-tool\pplx.py" %*
) else (
    python "C:\Users\Owner\Documents\Github_Repositories\perplexity-cli-tool\pplx.py" %*
)
