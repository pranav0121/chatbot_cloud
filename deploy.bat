@echo off
REM Chatbot Application - Docker Deployment Script for Windows
REM This script builds and deploys the chatbot application using Docker

setlocal enabledelayedexpansion

echo 🚀 Starting Chatbot Application Deployment...

REM Configuration
set APP_NAME=chatbot-app
if "%VERSION%"=="" set VERSION=latest
set APP_VERSION=%VERSION%
if "%REGISTRY_URL%"=="" set REGISTRY_URL=your-registry-url
set CONTAINER_PORT=5000
if "%HOST_PORT%"=="" set HOST_PORT=5000

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed. Please install Docker first.
    exit /b 1
)

REM Check if .env file exists, if not create from example
if not exist .env (
    echo [WARNING] .env file not found. Creating from .env.example...
    copy .env.example .env
    echo [WARNING] Please edit .env file with your actual configuration before running again.
    exit /b 1
)

echo [INFO] Building Docker image...

REM Build the Docker image
docker build -t %APP_NAME%:%APP_VERSION% .
if errorlevel 1 (
    echo [ERROR] Failed to build Docker image
    exit /b 1
)

echo [INFO] Docker image built successfully: %APP_NAME%:%APP_VERSION%

REM Tag for registry if REGISTRY_URL is provided
if not "%REGISTRY_URL%"=="your-registry-url" (
    echo [INFO] Tagging image for registry: %REGISTRY_URL%/%APP_NAME%:%APP_VERSION%
    docker tag %APP_NAME%:%APP_VERSION% %REGISTRY_URL%/%APP_NAME%:%APP_VERSION%
)

REM Run container for testing
echo [INFO] Starting container for testing...

REM Stop existing container if running
docker stop %APP_NAME% >nul 2>&1
docker rm %APP_NAME% >nul 2>&1

REM Run new container
docker run -d --name %APP_NAME% --env-file .env -p %HOST_PORT%:%CONTAINER_PORT% --restart unless-stopped -v "%cd%\static\uploads":/app/static/uploads -v "%cd%\translations":/app/translations %APP_NAME%:%APP_VERSION%
if errorlevel 1 (
    echo [ERROR] Failed to start container
    exit /b 1
)

echo [INFO] Container started successfully!

REM Wait for application to be ready
echo [INFO] Waiting for application to be ready...
timeout /t 10 /nobreak >nul

REM Health check
echo [INFO] Performing health check...
curl -f http://localhost:%HOST_PORT%/api/database/test >nul 2>&1
if errorlevel 1 (
    echo [ERROR] ❌ Health check failed. Check container logs:
    docker logs %APP_NAME%
    exit /b 1
)

echo [INFO] ✅ Health check passed! Application is running successfully.
echo.
echo 🌐 Application URLs:
echo    - Main App: http://localhost:%HOST_PORT%/
echo    - Admin Panel: http://localhost:%HOST_PORT%/admin/login
echo    - API Health: http://localhost:%HOST_PORT%/api/database/test
echo.
echo 🔐 Admin Credentials:
echo    - Email: admin@youcloudtech.com
echo    - Password: admin123
echo.
echo 📋 Container Info:
echo    - Container Name: %APP_NAME%
echo    - Image: %APP_NAME%:%APP_VERSION%
echo    - Port: %HOST_PORT%:%CONTAINER_PORT%
echo.
echo 🛠️ Management Commands:
echo    - View logs: docker logs %APP_NAME%
echo    - Stop: docker stop %APP_NAME%
echo    - Start: docker start %APP_NAME%
echo    - Remove: docker rm -f %APP_NAME%

REM Push to registry if configured
if not "%REGISTRY_URL%"=="your-registry-url" (
    echo [INFO] Pushing to registry: %REGISTRY_URL%/%APP_NAME%:%APP_VERSION%
    docker push %REGISTRY_URL%/%APP_NAME%:%APP_VERSION%
    if errorlevel 1 (
        echo [WARNING] Failed to push to registry (continuing anyway^)
    )
)

echo [INFO] 🎉 Deployment completed successfully!
pause
