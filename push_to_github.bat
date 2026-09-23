@echo off
title ApexPilot AI - Upload to GitHub
cd /d "%~dp0"

echo ======================================================================
echo              APEXPILOT AI - GITHUB REPOSITORY UPLOAD
echo ======================================================================
echo.

set "GH_EXE=C:\Program Files\GitHub CLI\gh.exe"

if exist "%GH_EXE%" (
    echo [*] GitHub CLI found at "%GH_EXE%"
    echo.
    echo Choose an option:
    echo   [1] Log in with GitHub CLI (gh auth login) and create a new repository automatically
    echo   [2] Enter your existing GitHub repository URL manually
    echo.
    set /p CHOICE="Enter choice [1 or 2]: "
    if "%CHOICE%"=="1" (
        echo [*] Running GitHub CLI authentication...
        "%GH_EXE%" auth login -w -p https
        echo [*] Creating GitHub repository...
        "%GH_EXE%" repo create ApexPilotAI --public --source=. --remote=origin --push
        if errorlevel 1 (
            echo.
            echo [!] If repository already exists, pushing directly...
            git push -u origin master
        )
        echo.
        echo [SUCCESS] Project uploaded to GitHub!
        pause
        exit /b 0
    )
)

echo.
echo Please enter your GitHub repository URL:
echo (e.g. https://github.com/your-username/ApexPilotAI.git)
echo.
set /p REPO_URL="Repository URL: "

if "%REPO_URL%"=="" (
    echo [ERROR] No URL provided. Aborting.
    pause
    exit /b 1
)

echo [*] Configuring remote origin...
git remote remove origin 2>nul
git remote add origin %REPO_URL%
git branch -M main

echo [*] Pushing code to GitHub (main branch)...
git push -u origin main
if errorlevel 1 (
    echo.
    echo [!] Push failed. Please verify repository permissions or authentication.
    echo     You can run 'gh auth login' or check your Personal Access Token.
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo [SUCCESS] ApexPilot AI successfully pushed to: %REPO_URL%
echo ======================================================================
pause
