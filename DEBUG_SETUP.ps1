#!/usr/bin/env pwsh
# Healthcare Analytics - Quick Setup & Verification Script (PowerShell)
# This script helps diagnose and fix registration issues

Write-Host "`n" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Healthcare Analytics Setup Wizard" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`n" -ForegroundColor White

# Check if .venv exists
if (-not (Test-Path ".venv")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run: python -m venv .venv" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
Write-Host "Step 1: Activating virtual environment..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to activate virtual environment" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "✓ DONE" -ForegroundColor Green
Write-Host "`n" -ForegroundColor White

# Run diagnostic
Write-Host "Step 2: Running database diagnostic (test_db.py)" -ForegroundColor Yellow
Write-Host "This will test MySQL connection, database, and tables...`n" -ForegroundColor Gray
python test_db.py
Write-Host "`n" -ForegroundColor White

# Ask user if they want to continue
$continue = Read-Host "Press Enter to start Flask app, or type 'exit' to quit"
if ($continue -eq "exit") {
    exit 0
}

Write-Host "`n" -ForegroundColor White
Write-Host "Step 3: Starting Flask application..." -ForegroundColor Yellow
Write-Host "`n" -ForegroundColor White
Write-Host "*** IMPORTANT: Watch the console below for registration errors ***" -ForegroundColor Yellow
Write-Host "*** When you get 'Database connection failed', check the error above it ***`n" -ForegroundColor Yellow

python app.py

Read-Host "Press Enter to exit"
