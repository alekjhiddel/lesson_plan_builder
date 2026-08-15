@echo off
REM IEP Lesson Planner - Windows Launcher
REM Double-click this file to start the app!

cd /d "%~dp0"

echo.
echo 🍎 Starting IEP Lesson Planner...
echo.

REM Check for Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Python is not installed.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation!
    pause
    exit /b 1
)

REM Check/install requirements
if not exist "venv" (
    echo 📦 First-time setup: Installing required packages...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt --quiet
    echo ✅ Setup complete!
    echo.
) else (
    call venv\Scripts\activate.bat
)

REM Run the app
echo 🌐 Opening in your browser at http://127.0.0.1:5000
echo    Press Ctrl+C to stop
echo.
python app.py
pause
