#!/usr/bin/env python3
"""
Docker Deployment Script - Builds and tests the containerized chatbot application
"""
import os
import subprocess
import time
import sys


def run_command(command, description, check_output=False):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        if check_output:
            result = subprocess.run(
                command, shell=True, check=True, capture_output=True, text=True)
            print(f"   ✅ {description} completed successfully")
            return result.stdout.strip()
        else:
            subprocess.run(command, shell=True, check=True)
            print(f"   ✅ {description} completed successfully")
            return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ {description} failed: {e}")
        if hasattr(e, 'stdout') and e.stdout:
            print(f"   Output: {e.stdout}")
        if hasattr(e, 'stderr') and e.stderr:
            print(f"   Error: {e.stderr}")
        return False


def docker_deployment():
    """Complete Docker deployment process"""
    print("🐳 DOCKER DEPLOYMENT FOR CHATBOT APPLICATION")
    print("=" * 60)

    # Step 1: Verify Docker is installed
    print("\n1️⃣ Verifying Docker Installation...")
    docker_version = run_command(
        "docker --version", "Docker version check", check_output=True)
    if not docker_version:
        print("❌ Docker is not installed or not in PATH")
        return False
    print(f"   📦 {docker_version}")

    # Check Docker Compose
    compose_version = run_command(
        "docker-compose --version", "Docker Compose version check", check_output=True)
    if not compose_version:
        print("❌ Docker Compose is not installed or not in PATH")
        return False
    print(f"   📦 {compose_version}")

    # Step 2: Clean up any existing containers
    print("\n2️⃣ Cleaning up existing containers...")
    run_command("docker-compose down --remove-orphans",
                "Stopping existing containers")
    run_command("docker system prune -f", "Cleaning up Docker system")

    # Step 3: Create production environment file
    print("\n3️⃣ Creating production environment file...")
    create_production_env()

    # Step 4: Build the Docker images
    print("\n4️⃣ Building Docker images...")
    if not run_command("docker-compose build --no-cache", "Building Docker images"):
        print("❌ Docker build failed")
        return False

    # Step 5: Start the services
    print("\n5️⃣ Starting services...")
    if not run_command("docker-compose up -d", "Starting Docker services"):
        print("❌ Failed to start Docker services")
        return False

    # Step 6: Wait for services to be ready
    print("\n6️⃣ Waiting for services to be ready...")
    time.sleep(10)

    # Step 7: Check service status
    print("\n7️⃣ Checking service status...")
    if not run_command("docker-compose ps", "Checking service status"):
        print("❌ Failed to check service status")
        return False

    # Step 8: Test the application
    print("\n8️⃣ Testing the application...")
    time.sleep(5)  # Give services more time to start

    # Check if containers are running
    result = run_command("docker-compose ps --services --filter status=running",
                         "Checking running services", check_output=True)
    if result:
        print(f"   ✅ Running services: {result}")

    # Step 9: Show logs for debugging
    print("\n9️⃣ Showing application logs...")
    run_command("docker-compose logs --tail=20 chatbot",
                "Getting application logs")

    # Step 10: Final status
    print("\n🔟 Final deployment status...")
    print("=" * 60)
    print("🎉 DOCKER DEPLOYMENT COMPLETED!")
    print("\n📋 Next Steps:")
    print("   1. Check application logs: docker-compose logs -f chatbot")
    print("   2. Access application at: http://localhost:5000")
    print("   3. Stop services: docker-compose down")
    print("   4. View service status: docker-compose ps")

    return True


def create_production_env():
    """Create production environment file"""
    prod_env_content = """# Production Docker Environment
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=production-secret-key-change-in-production
DEBUG=False

# Production MSSQL Database Configuration
DB_SERVER=host.docker.internal\\SQLEXPRESS
DB_DATABASE=SupportChatbot
DB_USERNAME=sa
DB_PASSWORD=
DB_USE_WINDOWS_AUTH=False

# Odoo Configuration
ODOO_URL=https://youcloudpay.odoo.com
ODOO_DB=youcloudpay
ODOO_USERNAME=pranav.r@youcloudtech.com
ODOO_PASSWORD=Pranav.r@1124

# Production Settings
LOG_LEVEL=INFO
WORKERS=2
"""

    with open('.env.production', 'w') as f:
        f.write(prod_env_content)

    print("   ✅ Production environment file created")


if __name__ == "__main__":
    try:
        success = docker_deployment()
        if success:
            print("\n🚀 DOCKER DEPLOYMENT SUCCESSFUL!")
            sys.exit(0)
        else:
            print("\n❌ DOCKER DEPLOYMENT FAILED!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {e}")
        sys.exit(1)
