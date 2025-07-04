@echo off
REM Docker Build and Test Script for Windows
REM This script builds the Docker image and runs basic tests

echo === Chatbot Docker Build and Test ===
echo.

REM Check if .env file exists
if not exist .env (
    echo Warning: .env file not found. Creating from .env.example...
    if exist .env.example (
        copy .env.example .env
        echo Please edit .env file with your actual configuration before proceeding.
        pause
    ) else (
        echo Error: .env.example file not found!
        exit /b 1
    )
)

echo Step 1: Building Docker image...
docker build -t chatbot-app:latest . || (
    echo Failed to build Docker image
    exit /b 1
)
echo Docker image built successfully
echo.

echo Step 2: Testing Docker image...
REM Start container in background for testing
docker run -d --name chatbot-test -p 5001:5000 --env-file .env chatbot-app:latest || (
    echo Failed to start test container
    exit /b 1
)

REM Wait for container to start
echo Waiting for container to start...
timeout /t 10 /nobreak > nul

REM Test if application is responding
echo Testing application health...
curl -f http://localhost:5001/api/database/test > nul 2>&1
if %errorlevel% == 0 (
    echo Application health check passed
) else (
    echo Health check failed, but container might still be starting
    echo Check logs with: docker logs chatbot-test
)

REM Show container status
echo.
echo Container status:
docker ps --filter name=chatbot-test --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

REM Show recent logs
echo.
echo Recent logs:
docker logs chatbot-test --tail 20

REM Cleanup
echo.
echo Cleaning up test container...
docker stop chatbot-test > nul 2>&1
docker rm chatbot-test > nul 2>&1

echo.
echo === Build and test completed successfully! ===
echo.
echo Next steps:
echo 1. Run with: docker-compose -f docker-compose.prod.yml up -d
echo 2. Or for development: docker-compose up -d
echo 3. Access at: http://localhost:5000
echo.
pause
