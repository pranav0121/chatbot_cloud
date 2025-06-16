@echo off
echo === Restarting Flask Application ===
echo.

echo Stopping any running Flask processes...
taskkill /f /im python.exe 2>nul
timeout /t 2 /nobreak >nul

echo Starting Flask application...
cd /d "c:\Users\prana\Downloads\chatbot_cloud"
set FLASK_APP=app.py
set FLASK_ENV=development
start "Flask App" cmd /k "flask run"

echo.
echo Flask application restarted!
echo Open browser: http://localhost:5000/auth/admin/login
echo.
pause
