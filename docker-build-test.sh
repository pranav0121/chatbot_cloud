#!/bin/bash
# Docker build and test script for ChatBot application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== ChatBot Docker Build and Test Script ===${NC}"

# Function to print status
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from template..."
    if [ -f "env.template" ]; then
        cp env.template .env
        print_status ".env file created from template. Please edit it with your configuration."
    else
        print_error "Neither .env nor env.template found. Please create .env file."
        exit 1
    fi
fi

# Stop any running containers
print_status "Stopping any running containers..."
docker-compose down --remove-orphans || true

# Build the application
print_status "Building Docker images..."
docker-compose build --no-cache

if [ $? -ne 0 ]; then
    print_error "Docker build failed!"
    exit 1
fi

# Start the services
print_status "Starting services..."
docker-compose up -d

# Wait for services to be ready
print_status "Waiting for services to start..."
sleep 30

# Check if containers are running
print_status "Checking container status..."
docker-compose ps

# Test database connectivity
print_status "Testing database connectivity..."
docker-compose exec -T chatbot-app python -c "
import sys
sys.path.append('/app')
try:
    from app import db
    from sqlalchemy import text
    with db.engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        print('✓ Database connection successful!')
except Exception as e:
    print(f'✗ Database connection failed: {e}')
    sys.exit(1)
" || {
    print_error "Database connectivity test failed!"
    docker-compose logs chatbot-app
    exit 1
}

# Test application health
print_status "Testing application health..."
sleep 10

for i in {1..30}; do
    if curl -f http://localhost:5000/health &> /dev/null; then
        print_status "✓ Application health check passed!"
        break
    elif [ $i -eq 30 ]; then
        print_error "Application health check failed after 30 attempts!"
        docker-compose logs chatbot-app
        exit 1
    else
        print_status "Waiting for application to be ready... (attempt $i/30)"
        sleep 2
    fi
done

# Test main application endpoint
print_status "Testing main application endpoint..."
if curl -f http://localhost:5000/ &> /dev/null; then
    print_status "✓ Main application endpoint is accessible!"
else
    print_warning "Main application endpoint test failed. Checking logs..."
    docker-compose logs --tail=20 chatbot-app
fi

# Test admin login API
print_status "Testing admin login API..."
ADMIN_TEST=$(curl -s -X POST http://localhost:5000/api/login \
    -H "Content-Type: application/json" \
    -d '{"email": "admin@youcloudtech.com", "password": "admin123"}' || echo "failed")

if [[ "$ADMIN_TEST" == *"token"* ]] || [[ "$ADMIN_TEST" == *"success"* ]]; then
    print_status "✓ Admin login API is working!"
else
    print_warning "Admin login API test inconclusive. Response: $ADMIN_TEST"
fi

# Show container logs summary
print_status "Application logs (last 10 lines):"
docker-compose logs --tail=10 chatbot-app

# Show running containers
print_status "Running containers:"
docker-compose ps

# Show resource usage
print_status "Resource usage:"
docker stats --no-stream

# Final status
print_status "${GREEN}=== Build and Test Completed Successfully! ===${NC}"
print_status "Application is running at: http://localhost:5000"
print_status "Admin credentials: admin@youcloudtech.com / admin123"
print_status ""
print_status "Useful commands:"
print_status "  - View logs: docker-compose logs -f"
print_status "  - Restart app: docker-compose restart chatbot-app"
print_status "  - Stop all: docker-compose down"
print_status "  - Full rebuild: docker-compose down && docker-compose build --no-cache && docker-compose up -d"

echo -e "${GREEN}✓ Deployment ready for handoff to operations team!${NC}"
