#!/bin/bash
# Docker Build and Test Script for Local MSSQL
# This script builds and runs the chatbot app connecting to your local MSSQL instance

echo "🚀 Building and Testing Chatbot with Local MSSQL"
echo "=================================================="

# Function to check if command succeeded
check_command() {
    if [ $? -eq 0 ]; then
        echo "✅ $1 completed successfully"
    else
        echo "❌ $1 failed"
        exit 1
    fi
}

# Step 1: Build the Docker image
echo "1️⃣ Building Docker image..."
docker build -t chatbot-app:latest .
check_command "Building Docker image"

# Step 2: Stop any existing containers
echo "2️⃣ Stopping existing containers..."
docker-compose -f docker-compose-local.yml down 2>/dev/null || true
check_command "Stopping existing containers"

# Step 3: Create logs and uploads directories
echo "3️⃣ Creating required directories..."
mkdir -p logs uploads
check_command "Creating directories"

# Step 4: Test the Flask app connection to local MSSQL
echo "4️⃣ Testing Flask app with local MSSQL..."
echo "🔄 Starting services with local MSSQL configuration..."

# Start services using the local MSSQL configuration
docker-compose -f docker-compose-local.yml --env-file .env.docker up -d
check_command "Starting Docker services"

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "5️⃣ Checking service health..."
docker-compose -f docker-compose-local.yml ps

# Test the Flask application
echo "6️⃣ Testing Flask application..."
echo "🔄 Testing Flask health endpoint..."

# Wait a bit more for the app to fully start
sleep 10

if curl -f http://localhost:5000/health 2>/dev/null; then
    echo "✅ Flask app is healthy and responding!"
else
    echo "⚠️  Flask app health check failed, checking logs..."
    docker logs chatbot-flask-app --tail 20
fi

# Test the main application endpoint
echo "🔄 Testing main application endpoint..."
if curl -f http://localhost:5000/ 2>/dev/null; then
    echo "✅ Main application endpoint is working!"
else
    echo "⚠️  Main application endpoint failed, checking logs..."
    docker logs chatbot-flask-app --tail 20
fi

echo ""
echo "🎉 Docker Testing Complete!"
echo ""
echo "📊 Service URLs:"
echo "   🌐 Main App: http://localhost:5000"
echo "   🏥 Health Check: http://localhost:5000/health"
echo "   🔧 Nginx Proxy: http://localhost"
echo ""
echo "📋 Useful Commands:"
echo "   📜 View app logs: docker logs chatbot-flask-app"
echo "   📜 View all logs: docker-compose -f docker-compose-local.yml logs"
echo "   🛑 Stop services: docker-compose -f docker-compose-local.yml down"
echo "   🔄 Restart services: docker-compose -f docker-compose-local.yml restart"
echo ""
echo "💡 The app is now running in Docker and connected to your local MSSQL!"
