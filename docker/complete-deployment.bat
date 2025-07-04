@echo off
REM Complete Deployment Script for Windows
REM This script handles the entire deployment process

echo ========================================
echo    Chatbot Application Deployment
echo    Complete Automated Setup
echo ========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed or not in PATH
    echo Please install Docker Desktop and try again
    pause
    exit /b 1
)

echo ✅ Docker is installed

REM Check if .env file exists
if not exist "..\..env" (
    echo ⚠️  .env file not found
    echo Copying .env.example to .env...
    copy "..\..env.example" "..\.env"
    echo.
    echo ❗ IMPORTANT: Edit .env file with your MSSQL server details before continuing
    echo Press any key after editing .env file...
    pause
)

echo ✅ Environment file found

REM Check if we're in the docker directory
if not exist "Dockerfile" (
    echo ❌ This script must be run from the docker/ directory
    echo Current directory: %CD%
    pause
    exit /b 1
)

echo ✅ Running from correct directory

REM Build the Docker image
echo.
echo 🔨 Building Docker image...
docker build -f Dockerfile -t chatbot-app:latest ..
if errorlevel 1 (
    echo ❌ Docker build failed
    pause
    exit /b 1
)

echo ✅ Docker image built successfully

REM Stop existing container if running
echo.
echo 🛑 Stopping existing containers...
docker stop chatbot-app 2>nul
docker rm chatbot-app 2>nul

REM Run the container
echo.
echo 🚀 Starting application container...
docker run -d --name chatbot-app -p 5000:5000 --env-file ..\.env chatbot-app:latest
if errorlevel 1 (
    echo ❌ Failed to start container
    echo Checking logs...
    docker logs chatbot-app
    pause
    exit /b 1
)

echo ✅ Container started successfully

REM Wait for application to start
echo.
echo ⏳ Waiting for application to initialize...
timeout /t 15 /nobreak > nul

REM Check if Python is available for validation
python --version >nul 2>&1
if not errorlevel 1 (
    echo.
    echo 🔍 Running deployment validation...
    python validate-deployment.py
) else (
    echo.
    echo ⚠️  Python not found, skipping automated validation
    echo Manual validation steps:
    echo 1. Open browser to http://localhost:5000
    echo 2. Check http://localhost:5000/api/database/test
    echo 3. Access admin panel at http://localhost:5000/admin
)

REM Show container status
echo.
echo 📊 Container Status:
docker ps | findstr chatbot-app

echo.
echo 📋 Next Steps:
echo 1. Open your browser to http://localhost:5000
echo 2. Test the admin panel at http://localhost:5000/admin
echo 3. Check database connection at http://localhost:5000/api/database/test
echo.
echo 📚 For troubleshooting, check:
echo - Container logs: docker logs chatbot-app
echo - Application health: http://localhost:5000/api/database/test
echo.
echo 🎉 Deployment Complete!
echo.

pause
