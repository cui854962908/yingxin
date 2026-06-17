<#
.SYNOPSIS
    在项目 backend 目录下启动 FastAPI（Uvicorn + reload）。

.DESCRIPTION
    请在 warehouse 根目录 backend 执行，例如：
        cd ...\student-welcome\backend
        .\scripts\start_backend.ps1
        .\scripts\start_backend.ps1 -Port 8001
        .\scripts\start_backend.ps1 -WithApiDocs

    -WithApiDocs 会为本进程设置 EXPOSE_API_DOCS=true（若 .env 已为 true 则冗余无害）。

.NOTES
    不包含：PostgreSQL 启动、alembic、Ollama。详见 docs/FRONTEND_API.md
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
    Write-Host "缺少 .env。请复制 .env.example 为 .env 并填写 DATABASE_URL、JWT_SECRET_KEY 等。" -ForegroundColor Yellow
    Write-Host "  Copy-Item .env.example .env" -ForegroundColor Gray
    exit 1
}

if ($WithApiDocs) {
    $env:EXPOSE_API_DOCS = "true"
    Write-Host "EXPOSE_API_DOCS=true → 可访问 http://127.0.0.1:$Port/docs" -ForegroundColor Green
}

Write-Host "Uvicorn http://127.0.0.1:$Port  (backend: $backendRoot)" -ForegroundColor Cyan

& uv run uvicorn app.main:app --reload --host 127.0.0.1 --port $Port
exit $LASTEXITCODE
