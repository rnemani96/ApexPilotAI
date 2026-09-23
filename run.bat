@echo off
title ApexPilot AI - Ultra-Fast Stealth Copilot
cd /d "%~dp0"

echo ======================================================================
echo             APEXPILOT AI - STEALTH INTERVIEW AND MEETING COPILOT
echo ======================================================================
echo.

if not exist "%~dp0.venv\Scripts\python.exe" (
    echo [*] Virtual environment not found. Creating .venv...
    python -m venv "%~dp0.venv"
    if errorlevel 1 (
        echo [ERROR] Python not found on system PATH or failed to create venv.
        echo Please ensure Python 3.10+ is installed from python.org.
        pause
        exit /b 1
    )
    echo [*] Installing dependencies from requirements.txt...
    "%~dp0.venv\Scripts\python.exe" -m pip install --upgrade pip
    "%~dp0.venv\Scripts\python.exe" -m pip install -r "%~dp0requirements.txt"
)

echo [*] Virtual environment verified.
echo [*] Activating environment...
call "%~dp0.venv\Scripts\activate.bat"

echo [*] Launching ApexPilot AI...
echo [*] Global Shortcuts:
echo     - Ctrl + Alt + H : Panic / Boss Key (Instant Hide / Show)
echo     - Ctrl + Alt + S : Snip LeetCode Screen (OCR Solver)
echo     - Ctrl + Alt + T : Webcam Teleprompter HUD
echo     - Ctrl + Alt + X : Click-Through Toggle (Pass Clicks to Zoom/Teams)
echo     - Ctrl + Alt + C : Silent Code Copy
echo     - Ctrl + Alt + A : Instant Solve Highlight / Input Query
echo.

"%~dp0.venv\Scripts\python.exe" "%~dp0main.py"
if errorlevel 1 (
    echo.
    echo [!] ApexPilot AI exited with an error.
    pause
    exit /b 1
)

echo.
echo [*] ApexPilot AI closed.
pause
