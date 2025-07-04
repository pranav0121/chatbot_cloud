#!/bin/bash

# Docker Build and Test Script
# This script builds the Docker image and runs basic tests

set -e

echo "=== Chatbot Docker Build and Test ==="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Navigate to parent directory for Docker context
cd ..

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found. Creating from .env.example...${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${YELLOW}Please edit .env file with your actual configuration before proceeding.${NC}"
        read -p "Press Enter to continue once you've configured .env file..."
    else
        echo -e "${RED}Error: .env.example file not found!${NC}"
        exit 1
    fi
fi

echo "Step 1: Building Docker image..."
docker build -f docker/Dockerfile -t chatbot-app:latest . || {
    echo -e "${RED}Failed to build Docker image${NC}"
    exit 1
}
echo -e "${GREEN}✓ Docker image built successfully${NC}"
echo ""

echo "Step 2: Testing Docker image..."
# Start container in background for testing
docker run -d --name chatbot-test -p 5001:5000 --env-file .env chatbot-app:latest || {
    echo -e "${RED}Failed to start test container${NC}"
    exit 1
}

# Wait for container to start
echo "Waiting for container to start..."
sleep 10

# Test if application is responding
echo "Testing application health..."
if curl -f http://localhost:5001/api/database/test > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Application health check passed${NC}"
else
    echo -e "${YELLOW}⚠ Health check failed, but container is running${NC}"
    echo "Check logs with: docker logs chatbot-test"
fi

# Show container status
echo ""
echo "Container status:"
docker ps --filter name=chatbot-test --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Show recent logs
echo ""
echo "Recent logs:"
docker logs chatbot-test --tail 20

# Cleanup
echo ""
echo "Cleaning up test container..."
docker stop chatbot-test > /dev/null 2>&1
docker rm chatbot-test > /dev/null 2>&1

echo ""
echo -e "${GREEN}=== Build and test completed successfully! ===${NC}"
echo ""
echo "Next steps:"
echo "1. Run with: docker-compose -f docker-compose.prod.yml up -d"
echo "2. Or for development: docker-compose up -d"
echo "3. Access at: http://localhost:5000"
echo ""
