Set-Location -Path $PSScriptRoot
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Starting ShadowMind Cyber Defense Command Deck..." -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
& "$PSScriptRoot\.venv\Scripts\python.exe" main.py

