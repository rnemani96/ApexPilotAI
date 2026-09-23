@echo off
setlocal
title ApexPilot AI - Upload to GitHub
cd /d "%~dp0"

echo ======================================================================
echo              APEXPILOT AI - GITHUB REPOSITORY UPLOAD
echo ======================================================================
echo.

set "GH_EXE=C:\Program Files\GitHub CLI\gh.exe"
if not exist "%GH_EXE%" (
    where gh.exe >nul 2>&1
    if not errorlevel 1 (
        set "GH_EXE=gh.exe"
    ) else (
        set "GH_EXE="
    )
)

:MENU
echo Choose how you would like to upload your project to GitHub:
echo.
if defined GH_EXE (
    echo   [1] Automatic: Log in via browser with GitHub CLI and create repository
) else (
    echo   [1] Automatic: GitHub CLI not detected (Install from cli.github.com)
)
echo   [2] Manual: Enter your GitHub repository URL directly
echo   [3] Cancel / Exit
echo.

set "CHOICE="
set /p CHOICE="Enter choice [1, 2, or 3]: "
if not defined CHOICE goto :CANCEL_EXIT

if "%CHOICE%"=="1" goto :DO_GH_CLI
if "%CHOICE%"=="2" goto :DO_MANUAL
if "%CHOICE%"=="3" goto :CANCEL_EXIT

echo [!] Invalid selection '%CHOICE%'. Please enter 1, 2, or 3.
echo.
goto :MENU

:DO_GH_CLI
if not defined GH_EXE (
    echo [ERROR] GitHub CLI is not installed.
    echo Please choose Option 2 to enter your repository URL manually,
    echo or download GitHub CLI from https://cli.github.com/
    echo.
    pause
    goto :MENU
)

echo.
echo [*] Step 1: Authenticating with GitHub...
echo [*] Your browser will open. Please confirm the one-time code to authorize.
echo.
"%GH_EXE%" auth login -w -p https
if errorlevel 1 (
    echo.
    echo [ERROR] GitHub authentication failed or was cancelled.
    pause
    goto :MENU
)

echo.
echo [*] Step 2: Creating and pushing to GitHub repository 'ApexPilotAI'...
"%GH_EXE%" repo create ApexPilotAI --public --source=. --remote=origin --push
if errorlevel 1 (
    echo.
    echo [*] If repository already exists on your account, pushing directly to origin...
    git branch -M main
    git push -u origin main
    if errorlevel 1 (
        git push -u origin master
    )
)
goto :SUCCESS_EXIT

:DO_MANUAL
echo.
echo ======================================================================
echo                      MANUAL REPOSITORY SETUP
echo ======================================================================
echo.
echo Please create a new empty repository on https://github.com/new
echo Then paste its HTTPS URL below.
echo Examples:
echo   https://github.com/your-username/ApexPilotAI.git
echo   (Or with token: https://TOKEN@github.com/your-username/ApexPilotAI.git)
echo.
set "REPO_URL="
set /p REPO_URL="Repository URL: "
if not defined REPO_URL goto :MENU

echo.
echo [*] Configuring remote origin to: %REPO_URL%
git remote remove origin >nul 2>&1
git remote add origin %REPO_URL%
git branch -M main

echo [*] Pushing code to GitHub...
git push -u origin main
if errorlevel 1 (
    echo.
    echo [!] Push to main branch failed, trying master branch...
    git push -u origin master
    if errorlevel 1 (
        echo.
        echo [ERROR] Push failed.
        echo Possible reasons:
        echo   1. The repository URL is incorrect.
        echo   2. You need to log in to GitHub on your machine (try Option 1).
        echo   3. Your personal access token needs 'repo' permissions.
        echo.
        pause
        goto :MENU
    )
)

:SUCCESS_EXIT
echo.
echo ======================================================================
echo [SUCCESS] ApexPilot AI successfully published to your GitHub!
echo ======================================================================
echo.
pause
exit /b 0

:CANCEL_EXIT
echo.
echo [*] Operation cancelled.
exit /b 0
