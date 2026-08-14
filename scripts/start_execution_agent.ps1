$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $ProjectRoot "execution_agent\.venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    throw "Execution-agent virtual environment not found: $Python"
}

Set-Location $ProjectRoot

& $Python -m uvicorn `
    execution_agent.app.main:app `
    --host 127.0.0.1 `
    --port 8765