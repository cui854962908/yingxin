<#
.SYNOPSIS
    Start FastAPI (Uvicorn + reload) from the backend directory.

.DESCRIPTION
    Run from the backend directory:
        cd ...\yingxin-master\backend
        .\scripts\start_backend.ps1
        .\scripts\start_backend.ps1 -Port 8001
        .\scripts\start_backend.ps1 -WithApiDocs
#>
param(
    [ValidateRange(1, 65535)]
    [int] $Port = 8000,
    [switch] $WithApiDocs
)

$ErrorActionPreference = "Stop"

$backendRoot = Split-Path -Parent $PSScriptRoot
Set-Location $backendRoot

if (-not (Test-Path (Join-Path $backendRoot ".env"))) {
    Write-Host "Missing .env. Copy .env.example to .env and fill in DATABASE_URL, JWT_SECRET_KEY, etc." -ForegroundColor Yellow
    Write-Host "  Copy-Item .env.example .env" -ForegroundColor Gray
    exit 1
}

if ($WithApiDocs) {
    $env:EXPOSE_API_DOCS = "true"
    Write-Host "EXPOSE_API_DOCS=true -> http://127.0.0.1:$Port/docs" -ForegroundColor Green
}

Write-Host "Uvicorn http://0.0.0.0:$Port  (backend: $backendRoot)" -ForegroundColor Cyan

& uv run uvicorn app.main:app --reload --host 0.0.0.0 --port $Port
exit $LASTEXITCODE
