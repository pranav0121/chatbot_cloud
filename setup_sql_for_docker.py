#!/usr/bin/env python3
"""
Script to enable SQL Server Authentication and create a user for Docker connection.
Run this script to prepare your MSSQL Express for Docker connectivity.
"""

import pyodbc
import os
from dotenv import load_dotenv


def setup_sql_server_for_docker():
    """Enable SQL Server Authentication and create Docker user."""
    load_dotenv()

    server = os.getenv('DB_SERVER', 'PRANAV\\SQLEXPRESS')
    database = os.getenv('DB_DATABASE', 'SupportChatbot')

    print("🔧 Setting up SQL Server for Docker connectivity...")
    print(f"Server: {server}")
    print(f"Database: {database}")

    # Connect using Windows Authentication (current working connection)
    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE=master;Trusted_Connection=yes;"

    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()

            print("\\n1. Checking SQL Server Authentication mode...")

            # Check current authentication mode
            cursor.execute("SELECT SERVERPROPERTY('IsIntegratedSecurityOnly')")
            is_windows_only = cursor.fetchone()[0]

            if is_windows_only:
                print("   ⚠️  SQL Server is in Windows Authentication mode only")
                print("   📝 You need to enable Mixed Mode Authentication:")
                print("   1. Open SQL Server Configuration Manager")
                print(
                    "   2. Go to SQL Server Network Configuration > Protocols for SQLEXPRESS")
                print("   3. Enable TCP/IP protocol")
                print(
                    "   4. In SQL Server Management Studio, right-click server > Properties > Security")
                print("   5. Select 'SQL Server and Windows Authentication mode'")
                print("   6. Restart SQL Server service")
                print("\\n   🔄 Please enable Mixed Mode and re-run this script.")
                return False
            else:
                print("   ✅ Mixed Mode Authentication is enabled")

            print("\\n2. Checking if 'sa' account is enabled...")

            # Check if sa account exists and is enabled
            cursor.execute(
                "SELECT name, is_disabled FROM sys.sql_logins WHERE name = 'sa'")
            sa_info = cursor.fetchone()

            if sa_info:
                if sa_info[1]:  # is_disabled
                    print("   🔧 Enabling 'sa' account...")
                    cursor.execute("ALTER LOGIN sa ENABLE")
                    print("   ✅ 'sa' account enabled")
                else:
                    print("   ✅ 'sa' account is already enabled")

            print("\\n3. Setting 'sa' password...")

            # Set a password for sa account
            sa_password = "DockerTest123!"
            try:
                cursor.execute(
                    f"ALTER LOGIN sa WITH PASSWORD = '{sa_password}'")
                print(f"   ✅ 'sa' password set to: {sa_password}")
                print(f"   📝 Update your .env.docker.sqlauth file with this password")
            except Exception as e:
                print(f"   ⚠️  Error setting sa password: {e}")
                print(
                    "   💡 You may need to set a different password or use an existing one")

            print("\\n4. Granting database access...")

            # Grant access to the specific database
            try:
                cursor.execute(f"USE [{database}]")
                cursor.execute("CREATE USER [sa] FOR LOGIN [sa]")
                cursor.execute("ALTER ROLE db_owner ADD MEMBER [sa]")
                print(f"   ✅ 'sa' granted access to {database} database")
            except Exception as e:
                if "already exists" in str(e):
                    print(
                        f"   ✅ 'sa' already has access to {database} database")
                else:
                    print(f"   ⚠️  Error granting database access: {e}")

            print("\\n5. Testing connection...")

            # Test SQL Server Authentication connection
            test_conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID=sa;PWD={sa_password};"

            try:
                with pyodbc.connect(test_conn_str) as test_conn:
                    test_cursor = test_conn.cursor()
                    test_cursor.execute("SELECT @@VERSION")
                    version = test_cursor.fetchone()[0]
                    print("   ✅ SQL Server Authentication test successful!")
                    print(f"   📊 Connected to: {version[:50]}...")
            except Exception as e:
                print(f"   ❌ SQL Server Authentication test failed: {e}")
                return False

            print("\\n🎉 SQL Server is now configured for Docker connectivity!")
            print("\\n📝 Next steps:")
            print("1. Update .env.docker.sqlauth with the SA password")
            print("2. Run Docker container with: docker run --rm -it -p 5000:5000 --env-file .env.docker.sqlauth chatbot-app:latest")

            return True

    except Exception as e:
        print(f"❌ Error connecting to SQL Server: {e}")
        print("💡 Make sure SQL Server is running and accessible")
        return False


if __name__ == "__main__":
    setup_sql_server_for_docker()
