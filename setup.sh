#!/bin/bash
# One-click deployment setup for ChatBot application
# This script sets up everything needed for deployment

set -e

echo "🚀 YouCloudTech ChatBot - One-Click Setup"
echo "=========================================="

# Create .env from template if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp env.template .env
    echo "✅ .env file created. Please edit it with your actual credentials before deployment."
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs uploads docker/ssl backup

# Set permissions for scripts
echo "🔧 Setting script permissions..."
chmod +x entrypoint.sh wait-for-db.sh docker-build-test.sh

# Check Docker installation
echo "🐳 Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Show current .env configuration
echo ""
echo "📋 Current .env configuration:"
echo "------------------------------"
grep -E "^[A-Z]" .env | head -10
echo "... (edit .env for complete configuration)"
echo ""

# Quick validation
echo "🔍 Validating configuration..."

# Check if essential variables are set
if grep -q "your-" .env; then
    echo "⚠️  WARNING: Found placeholder values in .env file"
    echo "   Please update .env with your actual credentials before deployment"
fi

echo ""
echo "🎯 Setup Complete! Next steps:"
echo "=============================="
echo ""
echo "1. Edit .env file with your actual credentials:"
echo "   - Database server and credentials"
echo "   - Odoo URL, username, and password"
echo "   - Secret keys for security"
echo ""
echo "2. Deploy the application:"
echo "   Linux/Mac: ./docker-build-test.sh"
echo "   Windows:   docker-build-test.bat"
echo ""
echo "3. Access the application:"
echo "   URL: http://localhost:5000"
echo "   Admin: admin@youcloudtech.com / admin123"
echo ""
echo "4. Verify health:"
echo "   curl http://localhost:5000/health"
echo ""
echo "📚 For complete documentation, see:"
echo "   - DOCKER_DEPLOYMENT_GUIDE_COMPLETE.md"
echo "   - PRODUCTION_DEPLOYMENT_READY.md"
echo ""
echo "✅ Ready for deployment!"
