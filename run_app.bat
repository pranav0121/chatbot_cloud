@echo off
cd /d "c:\Users\prana\Downloads\chatbot_cloud"
echo Creating database...
python create_db_direct.py
echo.
echo Starting Flask app...
python app.py
