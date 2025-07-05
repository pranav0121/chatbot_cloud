@echo off
REM One-click setup for ChatBot application on Windows
echo === YouCloudTech ChatBot - One-Click Setup ===
echo.

REM Create .env from template if it doesn't exist
if not exist ".env" (
    echo [INFO] Creating .env file from template...
    copy env.template .env >nul
    echo [SUCCESS] .env file created. Please edit it with your actual credentials.
)

REM Create necessary directories
echo [INFO] Creating necessary directories...
if not exist "logs" mkdir logs
if not exist "uploads" mkdir uploads
if not exist "docker\ssl" mkdir docker\ssl
if not exist "backup" mkdir backup

REM Check Docker installation
echo [INFO] Checking Docker installation...
docker --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Docker Compose is not installed. Please install Docker Desktop with Compose.
    pause
    exit /b 1
)

echo [SUCCESS] Docker and Docker Compose are installed
echo.

REM Show current .env configuration
echo === Current .env configuration ===
type .env | findstr /R "^[A-Z]" | head -n 10
echo ... (edit .env for complete configuration)
echo.

REM Quick validation
echo [INFO] Validating configuration...
findstr "your-" .env >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [WARNING] Found placeholder values in .env file
    echo          Please update .env with your actual credentials before deployment
)

echo.
echo === Setup Complete! Next steps: ===
echo.
echo 1. Edit .env file with your actual credentials:
echo    - Database server and credentials
echo    - Odoo URL, username, and password  
echo    - Secret keys for security
echo.
echo 2. Deploy the application:
echo    Run: docker-build-test.bat
echo.
echo 3. Access the application:
echo    URL: http://localhost:5000
echo    Admin: admin@youcloudtech.com / admin123
echo.
echo 4. Verify health:
echo    curl http://localhost:5000/health
echo.
echo === Documentation ===
echo Complete guide: DOCKER_DEPLOYMENT_GUIDE_COMPLETE.md
echo Production info: PRODUCTION_DEPLOYMENT_READY.md
echo.
echo [SUCCESS] Ready for deployment!
echo.
pause
