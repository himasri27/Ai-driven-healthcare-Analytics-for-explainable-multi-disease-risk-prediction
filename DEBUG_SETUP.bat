@echo off
REM Healthcare Analytics - Quick Setup & Verification Script
REM This script helps diagnose and fix registration issues

color 0A
echo.
echo ========================================
echo  Healthcare Analytics Setup Wizard
echo ========================================
echo.

REM Check if .venv exists
if not exist ".venv" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv .venv
    pause
    exit /b 1
)

REM Activate virtual environment
echo Step 1: Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo DONE
echo.

REM Run diagnostic
echo Step 2: Running database diagnostic (test_db.py)...
echo This will test MySQL connection, database, and tables...
echo.
python test_db.py
echo.

REM Ask user if they want to continue
set /p continue="Press Enter to continue, or type 'exit' to quit: "
if /i "%continue%"=="exit" exit /b 0

echo.
echo Step 3: Starting Flask application...
echo.
echo *** IMPORTANT: Watch the console below for registration errors ***
echo *** When you get "Database connection failed", check the error above it ***
echo.
python app.py

pause
