#!/bin/bash

# =============================================================================
# CHATBOT APPLICATION - OPS DEPLOYMENT VERIFICATION SCRIPT
# =============================================================================
# This script performs comprehensive verification of deployment readiness
# Run this script to ensure all components are ready for production deployment
# =============================================================================

set -e  # Exit on any error

echo "🚀 CHATBOT APPLICATION - DEPLOYMENT VERIFICATION"
echo "=================================================="
echo "Date: $(date)"
echo "Host: $(hostname)"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# =============================================================================
# 1. VERIFY SYSTEM REQUIREMENTS
# =============================================================================
echo "1. 🔍 CHECKING SYSTEM REQUIREMENTS"
echo "-----------------------------------"

# Check Docker
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | grep -oP '\d+\.\d+\.\d+')
    print_success "Docker installed: $DOCKER_VERSION"
else
    print_error "Docker not installed"
    exit 1
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version | grep -oP '\d+\.\d+\.\d+')
    print_success "Docker Compose installed: $COMPOSE_VERSION"
else
    print_error "Docker Compose not installed"
    exit 1
fi

# Check Docker daemon
if docker info &> /dev/null; then
    print_success "Docker daemon running"
else
    print_error "Docker daemon not running"
    exit 1
fi

echo ""

# =============================================================================
# 2. VERIFY PROJECT FILES
# =============================================================================
echo "2. 📁 CHECKING PROJECT FILES"
echo "----------------------------"

REQUIRED_FILES=(
    "app.py"
    "config.py"
    "database.py" 
    "requirements.txt"
    "Dockerfile"
    "docker-compose.yml"
    ".env.template"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        print_success "Found: $file"
    else
        print_error "Missing: $file"
        exit 1
    fi
done

# Check for environment files
if [[ -f ".env" || -f ".env.production" || -f ".env.docker.production" ]]; then
    print_success "Environment configuration files present"
else
    print_warning "No .env files found - remember to configure before deployment"
fi

echo ""

# =============================================================================
# 3. VERIFY DOCKER CONFIGURATION
# =============================================================================
echo "3. 🐳 VERIFYING DOCKER CONFIGURATION"
echo "------------------------------------"

# Validate docker-compose.yml
if docker-compose config > /dev/null 2>&1; then
    print_success "docker-compose.yml syntax valid"
else
    print_error "docker-compose.yml has syntax errors"
    docker-compose config
    exit 1
fi

# Check if production image exists
if docker images | grep -q "chatbot-app.*production"; then
    print_success "Production Docker image found"
else
    print_warning "No production image found - will build during deployment"
fi

echo ""

# =============================================================================
# 4. TEST BUILD PROCESS
# =============================================================================
echo "4. 🔨 TESTING BUILD PROCESS"
echo "---------------------------"

print_info "Building test image..."
if docker build -t chatbot-app:deployment-test . > build.log 2>&1; then
    print_success "Docker build successful"
    
    # Get image size
    IMAGE_SIZE=$(docker images chatbot-app:deployment-test --format "table {{.Size}}" | tail -1)
    print_info "Image size: $IMAGE_SIZE"
    
    # Clean up test image
    docker rmi chatbot-app:deployment-test > /dev/null 2>&1
else
    print_error "Docker build failed - check build.log"
    exit 1
fi

echo ""

# =============================================================================
# 5. VERIFY DEPENDENCIES
# =============================================================================
echo "5. 📦 CHECKING DEPENDENCIES"
echo "---------------------------"

# Check requirements.txt
if [[ -f "requirements.txt" ]]; then
    PACKAGE_COUNT=$(wc -l < requirements.txt)
    print_success "Requirements file contains $PACKAGE_COUNT packages"
    
    # Check for critical packages
    CRITICAL_PACKAGES=("Flask" "pyodbc" "gunicorn")
    for package in "${CRITICAL_PACKAGES[@]}"; do
        if grep -q "^$package" requirements.txt; then
            print_success "Critical package found: $package"
        else
            print_error "Missing critical package: $package"
        fi
    done
fi

echo ""

# =============================================================================
# 6. NETWORK CHECKS
# =============================================================================
echo "6. 🌐 NETWORK VERIFICATION"
echo "-------------------------"

# Check if port 5000 is available
if ! netstat -tuln 2>/dev/null | grep -q ":5000 "; then
    print_success "Port 5000 available"
else
    print_warning "Port 5000 already in use"
fi

# Check if port 6379 is available (Redis)
if ! netstat -tuln 2>/dev/null | grep -q ":6379 "; then
    print_success "Port 6379 available (Redis)"
else
    print_warning "Port 6379 already in use"
fi

echo ""

# =============================================================================
# 7. SECURITY CHECKS
# =============================================================================
echo "7. 🔒 SECURITY VERIFICATION"
echo "---------------------------"

# Check for sensitive files in repo
SENSITIVE_PATTERNS=(".env" "*.key" "*.pem" "password" "secret")
FOUND_SENSITIVE=false

for pattern in "${SENSITIVE_PATTERNS[@]}"; do
    if find . -name "$pattern" -type f 2>/dev/null | grep -v ".env.template" | grep -v ".env.example" | head -1 | read; then
        print_warning "Sensitive files found matching: $pattern"
        FOUND_SENSITIVE=true
    fi
done

if [[ "$FOUND_SENSITIVE" == false ]]; then
    print_success "No sensitive files in repository"
fi

# Check Dockerfile security
if grep -q "USER" Dockerfile; then
    print_success "Non-root user configured in Dockerfile"
else
    print_warning "No USER directive in Dockerfile - running as root"
fi

echo ""

# =============================================================================
# 8. DEPLOYMENT READINESS SUMMARY
# =============================================================================
echo "8. 📋 DEPLOYMENT READINESS SUMMARY"
echo "===================================="

# Calculate readiness score
TOTAL_CHECKS=0
PASSED_CHECKS=0

# System requirements (3 checks)
TOTAL_CHECKS=$((TOTAL_CHECKS + 3))
PASSED_CHECKS=$((PASSED_CHECKS + 3))  # We exit early if these fail

# Project files (count required files)
TOTAL_CHECKS=$((TOTAL_CHECKS + ${#REQUIRED_FILES[@]}))
for file in "${REQUIRED_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    fi
done

# Docker checks (2 checks)
TOTAL_CHECKS=$((TOTAL_CHECKS + 2))
if docker-compose config > /dev/null 2>&1; then
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
fi
if docker build -t chatbot-app:test-build . > /dev/null 2>&1; then
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
    docker rmi chatbot-app:test-build > /dev/null 2>&1
fi

# Calculate percentage
READINESS_PERCENT=$((PASSED_CHECKS * 100 / TOTAL_CHECKS))

echo ""
echo "READINESS SCORE: $PASSED_CHECKS/$TOTAL_CHECKS ($READINESS_PERCENT%)"
echo ""

if [[ $READINESS_PERCENT -ge 90 ]]; then
    print_success "🎉 DEPLOYMENT READY - All critical checks passed"
    echo ""
    echo "✅ NEXT STEPS FOR OPS TEAM:"
    echo "1. Copy project files to production server"
    echo "2. Configure .env file with production settings"
    echo "3. Run: docker-compose up -d"
    echo "4. Verify: curl http://localhost:5000/health"
    echo "5. Configure reverse proxy (Nginx) for SSL"
    echo ""
    exit 0
elif [[ $READINESS_PERCENT -ge 75 ]]; then
    print_warning "⚠️  MOSTLY READY - Minor issues need attention"
    echo ""
    echo "📝 REVIEW WARNINGS ABOVE BEFORE DEPLOYMENT"
    exit 0
else
    print_error "❌ NOT READY - Critical issues must be resolved"
    echo ""
    echo "🔧 FIX ERRORS ABOVE BEFORE ATTEMPTING DEPLOYMENT"
    exit 1
fi
