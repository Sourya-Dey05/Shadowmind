@echo off
cd /d "%~dp0"
echo ============================================================
echo  Starting ShadowMind Cyber Defense Command Deck...
echo ============================================================
"%~dp0.venv\Scripts\python.exe" main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Application exited with code %ERRORLEVEL%.
    pause
)

