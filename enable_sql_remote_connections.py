#!/usr/bin/env python3
"""
Enable SQL Server remote connections and configure TCP/IP properly.
"""
import pyodbc
import subprocess


def enable_remote_connections():
    """Enable remote connections on SQL Server."""

    print("🔧 ENABLING SQL SERVER REMOTE CONNECTIONS")
    print("=" * 50)

    # Connect locally first
    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER=PRANAV\\SQLEXPRESS;DATABASE=master;Trusted_Connection=yes;"

    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()

            print("\\n1. Enabling remote connections...")

            # Enable remote connections
            cursor.execute("EXEC sp_configure 'remote access', 1")
            cursor.execute("RECONFIGURE")
            print("   ✅ Remote access enabled")

            # Enable SQL Server Browser service (needed for named instances)
            try:
                result = subprocess.run(['sc', 'config', 'SQLBrowser', 'start=', 'auto'],
                                        capture_output=True, text=True)
                if result.returncode == 0:
                    print("   ✅ SQL Browser service configured")

                    # Start SQL Browser service
                    result = subprocess.run(['sc', 'start', 'SQLBrowser'],
                                            capture_output=True, text=True)
                    if result.returncode == 0:
                        print("   ✅ SQL Browser service started")
                    else:
                        print(
                            f"   ⚠️  SQL Browser service start: {result.stderr}")
                else:
                    print(
                        f"   ⚠️  SQL Browser service config: {result.stderr}")
            except Exception as e:
                print(f"   ⚠️  SQL Browser service: {e}")

            print("\\n2. Checking TCP/IP configuration...")

            # Check if TCP/IP is enabled (this is read-only, needs SQL Server Configuration Manager)
            print(
                "   📝 Note: TCP/IP protocol must be enabled in SQL Server Configuration Manager")
            print(
                "   📝 Location: SQL Server Network Configuration > Protocols for SQLEXPRESS")
            print("   📝 Enable: TCP/IP protocol")
            print("   📝 Port: Should be 1433 or dynamic")

            conn.commit()

            print("\\n🎯 SQL Server configuration updated!")
            print("\\n⚠️  IMPORTANT: You need to:")
            print("1. Open SQL Server Configuration Manager")
            print(
                "2. Go to 'SQL Server Network Configuration' > 'Protocols for SQLEXPRESS'")
            print("3. Enable 'TCP/IP' protocol")
            print("4. Right-click TCP/IP > Properties > IP Addresses tab")
            print("5. Set 'TCP Port' to 1433 (or note the dynamic port)")
            print("6. Restart SQL Server (SQLEXPRESS) service")

            return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def create_local_docker_solution():
    """Create a solution that works without remote connections."""

    print("\\n🔧 CREATING LOCAL DOCKER SOLUTION")
    print("=" * 40)

    # Create a Docker Compose that uses host networking
    docker_compose_host = '''version: '3.8'

services:
  chatbot-app:
    build: .
    container_name: chatbot-flask-app
    network_mode: host  # Use host networking to access local SQL Server
    environment:
      - FLASK_APP=app.py
      - FLASK_ENV=production
      - DB_SERVER=localhost\\SQLEXPRESS
      - DB_DATABASE=SupportChatbot
      - DB_USERNAME=dockeruser
      - DB_PASSWORD=DockerPass123!
      - DB_USE_WINDOWS_AUTH=False
      - ODOO_URL=https://youcloudpay.odoo.com
      - ODOO_DB=youcloudpay
      - ODOO_USERNAME=pranav.r@youcloudtech.com
      - ODOO_PASSWORD=Pranav.r@1124
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
'''

    with open('docker-compose.host-network.yml', 'w') as f:
        f.write(docker_compose_host)

    print("✅ Created docker-compose.host-network.yml")
    print("   This uses host networking to access local SQL Server")

    # Create environment file for host networking
    env_host = '''# Host Network Docker Configuration
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=docker-production-secret-key
DEBUG=False

# Database Configuration (Host Network - Local Access)
DB_SERVER=localhost\\SQLEXPRESS
DB_DATABASE=SupportChatbot
DB_USERNAME=dockeruser
DB_PASSWORD=DockerPass123!
DB_USE_WINDOWS_AUTH=False

# Odoo Configuration
ODOO_URL=https://youcloudpay.odoo.com
ODOO_DB=youcloudpay
ODOO_USERNAME=pranav.r@youcloudtech.com
ODOO_PASSWORD=Pranav.r@1124

# Logging
LOG_LEVEL=INFO'''

    with open('.env.docker.host', 'w') as f:
        f.write(env_host)

    print("✅ Created .env.docker.host")

    print("\\n🚀 To run with host networking:")
    print("   docker-compose -f docker-compose.host-network.yml up")
    print("\\n🌐 App will be available at:")
    print("   http://localhost:5000")

    return True


if __name__ == "__main__":
    print("🚀 FIXING DATABASE CONNECTION ISSUES FOR DOCKER")

    # Try to enable remote connections
    if enable_remote_connections():
        print("\\n✅ Remote connections configuration attempted")

    # Create local solution as backup
    if create_local_docker_solution():
        print("\\n✅ Local Docker solution created")

    print("\\n🎯 SOLUTION READY!")
    print("You now have two options:")
    print("1. Configure TCP/IP in SQL Server Configuration Manager (for standard Docker)")
    print("2. Use host networking Docker Compose (works immediately)")
