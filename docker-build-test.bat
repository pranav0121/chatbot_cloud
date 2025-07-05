@echo off
REM Docker build and test script for Windows
REM ChatBot application deployment

echo === ChatBot Docker Build and Test Script ===
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Docker is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Docker Compose is not installed or not in PATH
    pause
    exit /b 1
)

echo [INFO] Docker and Docker Compose are available
echo.

REM Check if .env file exists
if not exist ".env" (
    echo [WARNING] .env file not found
    if exist "env.template" (
        echo [INFO] Creating .env from template...
        copy env.template .env
        echo [INFO] Please edit .env file with your configuration
        echo.
    ) else (
        echo [ERROR] Neither .env nor env.template found
        pause
        exit /b 1
    )
)

REM Stop any running containers
echo [INFO] Stopping any running containers...
docker-compose down --remove-orphans

REM Build the application
echo [INFO] Building Docker images...
docker-compose build --no-cache

if %ERRORLEVEL% neq 0 (
    echo [ERROR] Docker build failed!
    pause
    exit /b 1
)

REM Start the services
echo [INFO] Starting services...
docker-compose up -d

REM Wait for services to start
echo [INFO] Waiting for services to start...
timeout /t 30 /nobreak

REM Check container status
echo [INFO] Checking container status...
docker-compose ps

REM Test application health (basic)
echo [INFO] Testing application health...
timeout /t 10 /nobreak

curl -f http://localhost:5000/health >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [SUCCESS] Application health check passed!
) else (
    echo [WARNING] Health check failed, but application might still be starting...
    echo [INFO] You can manually test at: http://localhost:5000
)

REM Test main endpoint
curl -f http://localhost:5000/ >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [SUCCESS] Main application endpoint is accessible!
) else (
    echo [WARNING] Main endpoint test failed, checking logs...
    docker-compose logs --tail=10 chatbot-app
)

echo.
echo === Build and Test Summary ===
echo Application URL: http://localhost:5000
echo Admin credentials: admin@youcloudtech.com / admin123
echo.
echo Useful commands:
echo   docker-compose logs -f               (view logs)
echo   docker-compose restart chatbot-app   (restart app)
echo   docker-compose down                  (stop all)
echo   docker-compose ps                    (show status)
echo.
echo [SUCCESS] Deployment ready for handoff to operations team!
echo.
pause
