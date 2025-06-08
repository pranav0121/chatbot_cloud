@echo off
echo ================================
echo YouCloudPay Chatbot - Quick Start
echo ================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ and try again
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Set environment variables
set FLASK_APP=app.py
set FLASK_ENV=development

REM Run the startup script
echo Starting YouCloudPay Chatbot...
python start.py

pause
