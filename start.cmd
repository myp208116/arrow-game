@echo off
cd /d "%~dp0"
if exist "dist\ArrowGame.exe" (
    start "" "dist\ArrowGame.exe"
    exit /b
)
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" main.py
) else (
    python main.py
)
if errorlevel 1 pause
