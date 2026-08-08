@echo off
REM Colors for output (Windows batch)
setlocal enabledelayedexpansion

echo Facebook Page Scraper - Installation Guide

REM Check if .env file exists
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo ✓ .env created
    echo ⚠️  Please update .env with your Facebook credentials
    echo.
) else (
    echo ✓ .env file already exists
    echo.
)

REM Check for Node.js
where node >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✓ Node.js found
    
    echo Installing Node.js dependencies...
    call npm install
    
    if %ERRORLEVEL% EQU 0 (
        echo ✓ Node.js dependencies installed
        echo.
    ) else (
        echo ✗ Failed to install Node.js dependencies
        echo.
    )
) else (
    echo ℹ Node.js not found (optional)
    echo.
)

REM Check for Python
where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo ✓ Python found
    
    REM Check if venv exists
    if not exist venv (
        echo Creating Python virtual environment...
        python -m venv venv
        echo ✓ Virtual environment created
    )
    
    REM Activate venv and install dependencies
    call venv\Scripts\activate.bat
    
    echo Installing Python dependencies...
    pip install -r requirements.txt
    
    if %ERRORLEVEL% EQU 0 (
        echo ✓ Python dependencies installed
        echo.
    ) else (
        echo ✗ Failed to install Python dependencies
        echo.
    )
) else (
    echo ℹ Python not found (optional)
    echo.
)

REM Create output directory
if not exist output (
    mkdir output
)
echo ✓ Output directory ready
echo.

echo Installation complete!
echo.
echo Next steps:
echo 1. Edit .env and add your Facebook credentials
echo 2. Run: node scraper.js (Node.js) or python scraper.py (Python)
echo 3. Check output/ directory for results
echo.
echo For more details, see SETUP.md

pause
