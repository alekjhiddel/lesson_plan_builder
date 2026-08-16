@echo off
REM ═══════════════════════════════════════════════════════
REM  SPARK — Windows Launcher
REM  Double-click this file to start the app!
REM ═══════════════════════════════════════════════════════

cd /d "%~dp0"

echo.
echo ═══════════════════════════════════════════════════════
echo   SPARK
echo ═══════════════════════════════════════════════════════
echo.

REM ─── Step 1: Check for Python ───
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Python is not installed on this computer.
    echo.
    echo    To install Python:
    echo    1. Go to: https://www.python.org/downloads/
    echo    2. Click the big yellow "Download Python" button
    echo    3. IMPORTANT: Check the box that says "Add Python to PATH"
    echo    4. Click "Install Now"
    echo    5. Then come back and double-click start.bat again
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do echo Found: %%i

REM ─── Step 2: Set up virtual environment (first time only) ───
if not exist "venv" (
    echo.
    echo Setting up for first time use... (takes about 30 seconds)
    echo.
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ❌ Failed to create virtual environment.
        echo    Make sure Python was installed with "Add to PATH" checked.
        pause
        exit /b 1
    )
    call venv\Scripts\activate.bat
    pip install -r requirements.txt --quiet
    if %errorlevel% neq 0 (
        echo ❌ Failed to install packages.
        echo    Check your internet connection and try again.
        pause
        exit /b 1
    )
    echo Setup complete!
) else (
    call venv\Scripts\activate.bat
)

REM ─── Step 3: Launch the app ───
echo.
echo ═══════════════════════════════════════════════════════
echo   Opening in your browser...
echo   Address: http://127.0.0.1:5000
echo.
echo   To STOP the app: Press Ctrl+C or close this window
echo ═══════════════════════════════════════════════════════
echo.

python app.py
pause
