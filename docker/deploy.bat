@echo off
REM YouCloudTech Chatbot - Windows Deployment Script
REM This script helps deploy the chatbot application on Windows servers

echo.
echo 🚀 YouCloudTech Chatbot Deployment Script (Windows)
echo ==========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker is not installed or not in PATH.
    echo Please install Docker Desktop for Windows first.
    echo Download from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Check if Docker Compose is available
docker-compose --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Docker Compose is not available.
    echo Please ensure Docker Desktop is properly installed.
    pause
    exit /b 1
)

echo ✅ Docker and Docker Compose are installed
echo.

REM Check if .env file exists
if not exist ".env" (
    if exist ".env.template" (
        echo 📝 Creating .env file from template...
        copy ".env.template" ".env" >nul
        echo.
        echo ⚠️  IMPORTANT: Please edit the .env file with your settings:
        echo    - Database server and credentials
        echo    - Flask secret key
        echo    - Odoo configuration
        echo.
        echo Opening .env file in notepad...
        start notepad .env
        echo.
        echo Press any key after you've configured the .env file...
        pause >nul
    ) else (
        echo ❌ No .env.template file found. Please create a .env file with your configuration.
        pause
        exit /b 1
    )
) else (
    echo ✅ .env file exists
)

REM Check for required environment variables
echo 🔍 Checking environment configuration...
findstr /C:"DB_SERVER=" .env >nul || (
    echo ❌ DB_SERVER not found in .env file
    set missing_vars=1
)
findstr /C:"DB_DATABASE=" .env >nul || (
    echo ❌ DB_DATABASE not found in .env file
    set missing_vars=1
)
findstr /C:"DB_USERNAME=" .env >nul || (
    echo ❌ DB_USERNAME not found in .env file
    set missing_vars=1
)
findstr /C:"DB_PASSWORD=" .env >nul || (
    echo ❌ DB_PASSWORD not found in .env file
    set missing_vars=1
)
findstr /C:"SECRET_KEY=" .env >nul || (
    echo ❌ SECRET_KEY not found in .env file
    set missing_vars=1
)

if defined missing_vars (
    echo.
    echo Please add the missing variables to your .env file and run the script again.
    pause
    exit /b 1
)

echo ✅ Required environment variables found
echo.

REM Build the Docker image
echo 🏗️  Building Docker image...
echo.

docker build -t chatbot-app:latest -f Dockerfile ..
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Failed to build Docker image
    pause
    exit /b 1
)

echo.
echo ✅ Docker image built successfully
echo.

REM Start the application
echo 🚀 Starting the application...
echo.

docker-compose up -d
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Failed to start the application
    pause
    exit /b 1
)

echo.
echo ✅ Application started successfully!
echo.

REM Wait for startup
echo 📊 Checking application status...
timeout /t 5 /nobreak >nul

REM Check if container is running
docker-compose ps | findstr "Up" >nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Container is not running properly
    echo Check logs with: docker-compose logs
    pause
    exit /b 1
)

echo ✅ Container is running
echo.

REM Test health endpoint
echo 🏥 Testing health endpoint...
timeout /t 10 /nobreak >nul

REM Try health check multiple times
set health_ok=0
for /L %%i in (1,1,5) do (
    curl -f http://localhost:5000/health >nul 2>&1
    if !ERRORLEVEL! EQU 0 (
        echo ✅ Health check passed
        set health_ok=1
        goto :health_done
    ) else (
        echo ⏳ Waiting for application to start... (attempt %%i/5)
        timeout /t 5 /nobreak >nul
    )
)

:health_done
if %health_ok% EQU 0 (
    echo ⚠️  Health check failed, but the container is running.
    echo This might be due to database connectivity issues.
    echo Check the logs: docker-compose logs
)

echo.
echo 🎉 Deployment Complete!
echo =======================
echo.
echo 📋 Application Information:
echo    - Application URL: http://localhost:5000
echo    - Health Check: http://localhost:5000/health
echo    - Container Status: docker-compose ps
echo    - View Logs: docker-compose logs -f
echo.
echo 📚 Next Steps:
echo    1. Test the application: curl http://localhost:5000/health
echo    2. Configure reverse proxy (IIS/Nginx) for production
echo    3. Set up SSL certificate for HTTPS
echo    4. Configure Windows Firewall rules
echo.
echo 🔧 Useful Commands:
echo    - Stop application: docker-compose down
echo    - Restart application: docker-compose restart
echo    - View logs: docker-compose logs chatbot
echo    - Update application: docker-compose pull ^&^& docker-compose up -d
echo.

if %health_ok% EQU 1 (
    echo ✅ Your chatbot application is ready to use!
) else (
    echo ⚠️  Please check the logs and verify your database configuration.
)

echo.
echo Press any key to exit...
pause >nul
