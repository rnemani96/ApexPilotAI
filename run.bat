@echo off
title ApexPilot AI - Ultra-Fast Stealth Copilot
cd /d "%~dp0"

echo ======================================================================
echo             APEXPILOT AI - STEALTH INTERVIEW & MEETING COPILOT
echo ======================================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [*] Creating virtual environment (.venv)...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Python not found or failed to create venv.
        pause
        exit /b 1
    )
    echo [*] Installing dependencies...
    .venv\Scripts\python.exe -m pip install -r requirements.txt
)

echo [*] Activating virtual environment...
call .venv\Scripts\activate.bat

echo [*] Launching ApexPilot AI...
echo [*] Shortcuts:
echo     - Ctrl + Alt + H : Panic / Boss Key (Instant Hide/Unhide)
echo     - Ctrl + Alt + S : Snip LeetCode Screen (OCR Solver)
echo     - Ctrl + Alt + T : Webcam Teleprompter HUD
echo     - Ctrl + Alt + C : Silent Code Copy
echo.

python main.py
if errorlevel 1 (
    echo.
    echo [!] ApexPilot AI exited with an error.
    pause
)
