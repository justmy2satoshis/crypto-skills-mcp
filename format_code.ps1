#!/usr/bin/env pwsh
# Format all Python files with Black

Write-Host "Running Black formatter..." -ForegroundColor Cyan
python -m black .

Write-Host "`nFormatting complete!" -ForegroundColor Green
Write-Host "Run 'git diff' to see changes." -ForegroundColor Yellow
