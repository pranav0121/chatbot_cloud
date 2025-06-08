@echo off
echo ================================================
echo    Customer Support System Startup Script
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

echo ✓ Python is installed

REM Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo WARNING: Some packages might not have installed correctly
    echo You may need to install them manually
)

echo ✓ Dependencies installed

REM Start the application
echo.
echo ================================================
echo Starting Customer Support System...
echo ================================================
echo.
echo User Interface will be available at:
echo   http://localhost:5000
echo.
echo Admin Dashboard will be available at:
echo   http://localhost:5000/admin
echo.
echo Press Ctrl+C to stop the server
echo ================================================
echo.

python app.py

echo.
echo Application has stopped.
pause
