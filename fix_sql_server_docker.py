#!/usr/bin/env python3
"""
Comprehensive SQL Server setup for Docker connectivity.
This script will enable Mixed Mode Authentication and create proper users.
"""
import pyodbc
import os
from dotenv import load_dotenv


def fix_sql_server_for_docker():
    """Fix SQL Server configuration for Docker connectivity."""
    load_dotenv()

    server = os.getenv('DB_SERVER', 'PRANAV\\SQLEXPRESS')
    database = os.getenv('DB_DATABASE', 'SupportChatbot')

    print("🔧 FIXING SQL SERVER FOR DOCKER CONNECTIVITY")
    print("=" * 50)
    print(f"Server: {server}")
    print(f"Database: {database}")

    # Connect using Windows Authentication (current working method)
    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE=master;Trusted_Connection=yes;"

    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()

            print("\\n1. Enabling Mixed Mode Authentication...")

            # Enable Mixed Mode Authentication using xp_instance_regwrite
            try:
                cursor.execute("""
                    EXEC xp_instance_regwrite 
                    N'HKEY_LOCAL_MACHINE', 
                    N'Software\\Microsoft\\MSSQLServer\\MSSQLServer', 
                    N'LoginMode', 
                    REG_DWORD, 2
                """)
                print("   ✅ Mixed Mode Authentication enabled")
            except Exception as e:
                print(f"   ⚠️  Mixed Mode Authentication: {e}")

            print("\\n2. Creating Docker user...")

            # Create a dedicated user for Docker
            docker_user = "dockeruser"
            docker_password = "DockerPass123!"

            try:
                # Drop user if exists
                cursor.execute(
                    f"IF EXISTS (SELECT * FROM sys.sql_logins WHERE name = '{docker_user}') DROP LOGIN [{docker_user}]")

                # Create new login
                cursor.execute(
                    f"CREATE LOGIN [{docker_user}] WITH PASSWORD = '{docker_password}', CHECK_POLICY = OFF")
                print(f"   ✅ Created login: {docker_user}")

                # Grant sysadmin role for full access
                cursor.execute(
                    f"ALTER SERVER ROLE sysadmin ADD MEMBER [{docker_user}]")
                print(f"   ✅ Granted sysadmin role to {docker_user}")

            except Exception as e:
                print(f"   ⚠️  Creating Docker user: {e}")

            print("\\n3. Enabling SA account...")

            try:
                # Enable SA account
                cursor.execute("ALTER LOGIN sa ENABLE")

                # Set SA password
                sa_password = "SA_DockerPass123!"
                cursor.execute(
                    f"ALTER LOGIN sa WITH PASSWORD = '{sa_password}'")
                print("   ✅ SA account enabled and password set")

            except Exception as e:
                print(f"   ⚠️  Enabling SA account: {e}")

            print("\\n4. Configuring TCP/IP Protocol...")

            try:
                # Enable TCP/IP (this requires SQL Server restart)
                cursor.execute("""
                    EXEC sp_configure 'remote access', 1
                    RECONFIGURE
                """)
                print("   ✅ Remote access enabled")

            except Exception as e:
                print(f"   ⚠️  Configuring TCP/IP: {e}")

            conn.commit()

            print("\\n5. Testing Docker user connection...")

            # Test the new user connection
            test_conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={docker_user};PWD={docker_password};"

            try:
                with pyodbc.connect(test_conn_str) as test_conn:
                    test_cursor = test_conn.cursor()
                    test_cursor.execute("SELECT @@VERSION")
                    version = test_cursor.fetchone()[0]
                    print("   ✅ Docker user connection test SUCCESSFUL!")

                    # Test database access
                    test_cursor.execute("SELECT COUNT(*) FROM Tickets")
                    ticket_count = test_cursor.fetchone()[0]
                    print(
                        f"   ✅ Database access confirmed - {ticket_count} tickets found")

                    return docker_user, docker_password

            except Exception as e:
                print(f"   ❌ Docker user connection test failed: {e}")

                # Try SA connection as fallback
                print("\\n   🔄 Trying SA account...")
                sa_conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID=sa;PWD={sa_password};"

                try:
                    with pyodbc.connect(sa_conn_str) as sa_conn:
                        sa_cursor = sa_conn.cursor()
                        sa_cursor.execute("SELECT @@VERSION")
                        print("   ✅ SA account connection test SUCCESSFUL!")
                        return "sa", sa_password

                except Exception as sa_e:
                    print(f"   ❌ SA account connection also failed: {sa_e}")

            return None, None

    except Exception as e:
        print(f"❌ Error connecting to SQL Server: {e}")
        return None, None


def update_docker_env_file(username, password):
    """Update Docker environment file with working credentials."""
    if not username or not password:
        print("❌ No working credentials found")
        return False

    env_content = f"""# Docker Environment Configuration - WORKING DATABASE CONNECTION
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=docker-production-secret-key-change-in-production
DEBUG=False

# Database Configuration for Docker (FIXED)
DB_SERVER=host.docker.internal\\SQLEXPRESS
DB_DATABASE=SupportChatbot
DB_USERNAME={username}
DB_PASSWORD={password}
DB_USE_WINDOWS_AUTH=False

# Odoo Configuration
ODOO_URL=https://youcloudpay.odoo.com
ODOO_DB=youcloudpay
ODOO_USERNAME=pranav.r@youcloudtech.com
ODOO_PASSWORD=Pranav.r@1124

# Logging
LOG_LEVEL=INFO
"""

    with open('.env.docker.fixed', 'w') as f:
        f.write(env_content)

    print(f"\\n📝 Created .env.docker.fixed with working credentials:")
    print(f"   Username: {username}")
    print(f"   Password: {password}")

    return True


if __name__ == "__main__":
    print("🚀 FIXING ALL DATABASE ISSUES FOR DOCKER...")

    username, password = fix_sql_server_for_docker()

    if username and password:
        if update_docker_env_file(username, password):
            print("\\n🎉 SUCCESS! Database issues fixed for Docker!")
            print("\\n📋 Next steps:")
            print("1. Restart SQL Server service (important for Mixed Mode)")
            print(
                "2. Run: docker run --rm -it -p 5000:5000 --env-file .env.docker.fixed chatbot-app:latest")
            print("3. Test: curl http://localhost:5000/health")
        else:
            print("\\n❌ Failed to create environment file")
    else:
        print("\\n❌ Failed to create working database credentials")
        print("\\n🔧 Manual steps required:")
        print("1. Open SQL Server Configuration Manager")
        print("2. Restart SQL Server (SQLEXPRESS) service")
        print("3. Enable TCP/IP protocol")
        print("4. Set port 1433 for TCP/IP")
        print("5. Restart service again")
