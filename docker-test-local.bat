@echo off
:: Docker Build and Test Script for Local MSSQL (Windows)
:: This script builds and runs the chatbot app connecting to your local MSSQL instance

echo 🚀 Building and Testing Chatbot with Local MSSQL
echo ==================================================

:: Step 1: Build the Docker image
echo 1️⃣ Building Docker image...
docker build -t chatbot-app:latest .
if %errorlevel% neq 0 (
    echo ❌ Building Docker image failed
    exit /b 1
)
echo ✅ Building Docker image completed successfully

:: Step 2: Stop any existing containers
echo 2️⃣ Stopping existing containers...
docker-compose -f docker-compose-local.yml down >nul 2>&1
echo ✅ Stopping existing containers completed successfully

:: Step 3: Create logs and uploads directories
echo 3️⃣ Creating required directories...
if not exist logs mkdir logs
if not exist uploads mkdir uploads
echo ✅ Creating directories completed successfully

:: Step 4: Test the Flask app connection to local MSSQL
echo 4️⃣ Testing Flask app with local MSSQL...
echo 🔄 Starting services with local MSSQL configuration...

:: Start services using the local MSSQL configuration
docker-compose -f docker-compose-local.yml --env-file .env.docker up -d
if %errorlevel% neq 0 (
    echo ❌ Starting Docker services failed
    exit /b 1
)
echo ✅ Starting Docker services completed successfully

:: Wait for services to be ready
echo ⏳ Waiting for services to be ready...
timeout /t 30 /nobreak >nul

:: Check service health
echo 5️⃣ Checking service health...
docker-compose -f docker-compose-local.yml ps

:: Test the Flask application
echo 6️⃣ Testing Flask application...
echo 🔄 Testing Flask health endpoint...

:: Wait a bit more for the app to fully start
timeout /t 10 /nobreak >nul

:: Test health endpoint
curl -f http://localhost:5000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Flask app is healthy and responding!
) else (
    echo ⚠️  Flask app health check failed, checking logs...
    docker logs chatbot-flask-app --tail 20
)

:: Test the main application endpoint
echo 🔄 Testing main application endpoint...
curl -f http://localhost:5000/ >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Main application endpoint is working!
) else (
    echo ⚠️  Main application endpoint failed, checking logs...
    docker logs chatbot-flask-app --tail 20
)

echo.
echo 🎉 Docker Testing Complete!
echo.
echo 📊 Service URLs:
echo    🌐 Main App: http://localhost:5000
echo    🏥 Health Check: http://localhost:5000/health
echo    🔧 Nginx Proxy: http://localhost
echo.
echo 📋 Useful Commands:
echo    📜 View app logs: docker logs chatbot-flask-app
echo    📜 View all logs: docker-compose -f docker-compose-local.yml logs
echo    🛑 Stop services: docker-compose -f docker-compose-local.yml down
echo    🔄 Restart services: docker-compose -f docker-compose-local.yml restart
echo.
echo 💡 The app is now running in Docker and connected to your local MSSQL!

pause
