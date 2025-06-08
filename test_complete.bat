@echo off
echo Image Upload Fix - Complete Test
echo ================================
echo.

echo Starting Flask application in background...
start /B python app.py

echo Waiting for server to start...
timeout /t 8 /nobreak > nul

echo Running complete workflow test...
python test_complete_workflow.py

echo.
echo Test completed. Press any key to exit...
pause > nul
