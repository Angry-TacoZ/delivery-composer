[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $python)) {
    throw "Python environment not found. Create .venv and install api requirements first."
}

Push-Location $repoRoot
try {
    & $python -m ruff check api
    if ($LASTEXITCODE -ne 0) { throw "Ruff failed." }

    & $python -m pytest api\tests
    if ($LASTEXITCODE -ne 0) { throw "API tests failed." }

    & npm.cmd --prefix web run build
    if ($LASTEXITCODE -ne 0) { throw "Frontend production build failed." }
}
finally {
    Pop-Location
}
