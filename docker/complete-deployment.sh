#!/bin/bash
# Complete Deployment Script for Linux/Mac
# This script handles the entire deployment process

echo "========================================"
echo "   Chatbot Application Deployment"
echo "   Complete Automated Setup"
echo "========================================"
echo

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    echo "Please install Docker and try again"
    exit 1
fi

echo "✅ Docker is installed"

# Check if .env file exists
if [ ! -f "../.env" ]; then
    echo "⚠️  .env file not found"
    echo "Copying .env.example to .env..."
    cp "../.env.example" "../.env"
    echo
    echo "❗ IMPORTANT: Edit .env file with your MSSQL server details before continuing"
    echo "Press Enter after editing .env file..."
    read
fi

echo "✅ Environment file found"

# Check if we're in the docker directory
if [ ! -f "Dockerfile" ]; then
    echo "❌ This script must be run from the docker/ directory"
    echo "Current directory: $(pwd)"
    exit 1
fi

echo "✅ Running from correct directory"

# Build the Docker image
echo
echo "🔨 Building Docker image..."
if ! docker build -f Dockerfile -t chatbot-app:latest ..; then
    echo "❌ Docker build failed"
    exit 1
fi

echo "✅ Docker image built successfully"

# Stop existing container if running
echo
echo "🛑 Stopping existing containers..."
docker stop chatbot-app 2>/dev/null || true
docker rm chatbot-app 2>/dev/null || true

# Run the container
echo
echo "🚀 Starting application container..."
if ! docker run -d --name chatbot-app -p 5000:5000 --env-file ../.env chatbot-app:latest; then
    echo "❌ Failed to start container"
    echo "Checking logs..."
    docker logs chatbot-app
    exit 1
fi

echo "✅ Container started successfully"

# Wait for application to start
echo
echo "⏳ Waiting for application to initialize..."
sleep 15

# Check if Python is available for validation
if command -v python3 &> /dev/null; then
    echo
    echo "🔍 Running deployment validation..."
    python3 validate-deployment.py
elif command -v python &> /dev/null; then
    echo
    echo "🔍 Running deployment validation..."
    python validate-deployment.py
else
    echo
    echo "⚠️  Python not found, skipping automated validation"
    echo "Manual validation steps:"
    echo "1. Open browser to http://localhost:5000"
    echo "2. Check http://localhost:5000/api/database/test"
    echo "3. Access admin panel at http://localhost:5000/admin"
fi

# Show container status
echo
echo "📊 Container Status:"
docker ps | grep chatbot-app

echo
echo "📋 Next Steps:"
echo "1. Open your browser to http://localhost:5000"
echo "2. Test the admin panel at http://localhost:5000/admin"
echo "3. Check database connection at http://localhost:5000/api/database/test"
echo
echo "📚 For troubleshooting, check:"
echo "- Container logs: docker logs chatbot-app"
echo "- Application health: http://localhost:5000/api/database/test"
echo
echo "🎉 Deployment Complete!"
echo
