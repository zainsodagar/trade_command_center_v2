$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $ProjectRoot "execution_agent\.venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    throw "Execution-agent virtual environment not found: $Python"
}

Set-Location $ProjectRoot

& $Python -m pytest execution_agent\tests -q

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}