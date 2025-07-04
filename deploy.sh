#!/bin/bash

# YouCloudTech Chatbot - Quick Deployment Script
# This script helps deploy the chatbot application on a new server

set -e

echo "🚀 YouCloudTech Chatbot Deployment Script"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first:"
    echo "   sudo apt update && sudo apt install docker.io docker-compose"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first:"
    echo "   sudo apt install docker-compose"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    if [ -f ".env.template" ]; then
        echo "📝 Creating .env file from template..."
        cp .env.template .env
        echo ""
        echo "⚠️  IMPORTANT: Please edit the .env file with your settings:"
        echo "   - Database server and credentials"
        echo "   - Flask secret key"
        echo "   - Odoo configuration"
        echo ""
        echo "   nano .env"
        echo ""
        echo "Press Enter after you've configured the .env file..."
        read -p ""
    else
        echo "❌ No .env.template file found. Please create a .env file with your configuration."
        exit 1
    fi
else
    echo "✅ .env file exists"
fi

# Verify environment file has required variables
echo "🔍 Checking environment configuration..."
required_vars=("DB_SERVER" "DB_DATABASE" "DB_USERNAME" "DB_PASSWORD" "SECRET_KEY")
missing_vars=()

for var in "${required_vars[@]}"; do
    if ! grep -q "^${var}=" .env; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo "❌ Missing required environment variables in .env:"
    printf '   - %s\n' "${missing_vars[@]}"
    echo ""
    echo "Please add these variables to your .env file and run the script again."
    exit 1
fi

echo "✅ Required environment variables found"
echo ""

# Build the Docker image
echo "🏗️  Building Docker image..."
echo ""
cd docker/ || exit 1

if docker build -t chatbot-app:latest -f Dockerfile ..; then
    echo ""
    echo "✅ Docker image built successfully"
else
    echo ""
    echo "❌ Failed to build Docker image"
    exit 1
fi

echo ""

# Start the application
echo "🚀 Starting the application..."
echo ""

if docker-compose up -d; then
    echo ""
    echo "✅ Application started successfully!"
else
    echo ""
    echo "❌ Failed to start the application"
    exit 1
fi

echo ""
echo "📊 Checking application status..."
sleep 5

# Check if container is running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Container is running"
else
    echo "❌ Container is not running properly"
    echo "Check logs with: docker-compose logs"
    exit 1
fi

echo ""
echo "🏥 Testing health endpoint..."
sleep 10

# Test health endpoint
for i in {1..5}; do
    if curl -f http://localhost:5000/health > /dev/null 2>&1; then
        echo "✅ Health check passed"
        health_ok=true
        break
    else
        echo "⏳ Waiting for application to start... (attempt $i/5)"
        sleep 5
    fi
done

if [ "$health_ok" != true ]; then
    echo "⚠️  Health check failed, but the container is running."
    echo "This might be due to database connectivity issues."
    echo "Check the logs: docker-compose logs"
fi

echo ""
echo "🎉 Deployment Complete!"
echo "======================="
echo ""
echo "📋 Application Information:"
echo "   - Application URL: http://localhost:5000"
echo "   - Health Check: http://localhost:5000/health"
echo "   - Container Status: docker-compose ps"
echo "   - View Logs: docker-compose logs -f"
echo ""
echo "📚 Next Steps:"
echo "   1. Test the application: curl http://localhost:5000/health"
echo "   2. Configure reverse proxy (Nginx) for production"
echo "   3. Set up SSL certificate for HTTPS"
echo "   4. Configure firewall rules"
echo ""
echo "🔧 Useful Commands:"
echo "   - Stop application: docker-compose down"
echo "   - Restart application: docker-compose restart"
echo "   - View logs: docker-compose logs chatbot"
echo "   - Update application: docker-compose pull && docker-compose up -d"
echo ""

if [ "$health_ok" = true ]; then
    echo "✅ Your chatbot application is ready to use!"
else
    echo "⚠️  Please check the logs and verify your database configuration."
fi

echo ""
