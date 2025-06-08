@echo off
echo Chatbot Fix Testing Script
echo =========================
echo.

echo Starting the chatbot server...
start /B python app.py

echo Waiting for server to start...
timeout /t 5 /nobreak > nul

echo.
echo Running fix verification tests...
python test_fixes.py

echo.
echo Testing complete. Press any key to continue...
pause > nul
