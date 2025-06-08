@echo off
echo Starting Flask application...
start cmd /k "python app.py"

echo Waiting for server to start...
timeout /t 5 /nobreak

echo Running image upload fix test...
python test_image_upload_fix.py

echo.
echo Test completed. Check the results above.
echo Press any key to exit...
pause
