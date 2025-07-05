#!/usr/bin/env python3
"""
Test database connection script to diagnose MSSQL connectivity issues.
"""
import os
import pyodbc
from dotenv import load_dotenv


def test_direct_connection():
    """Test direct pyodbc connection to MSSQL."""
    load_dotenv()

    server = os.getenv('DB_SERVER', 'PRANAV\\SQLEXPRESS')
    database = os.getenv('DB_DATABASE', 'SupportChatbot')
    use_windows_auth = os.getenv(
        'DB_USE_WINDOWS_AUTH', 'True').lower() == 'true'
    username = os.getenv('DB_USERNAME', '')
    password = os.getenv('DB_PASSWORD', '')

    print(f"Testing connection to:")
    print(f"  Server: {server}")
    print(f"  Database: {database}")
    print(f"  Windows Auth: {use_windows_auth}")
    print(f"  Username: {username}")
    print(f"  Password: {'***' if password else '(empty)'}")
    print()

    # List available drivers
    print("Available ODBC drivers:")
    drivers = [driver for driver in pyodbc.drivers() if 'SQL Server' in driver]
    for driver in drivers:
        print(f"  - {driver}")
    print()

    if not drivers:
        print("ERROR: No SQL Server ODBC drivers found!")
        return False

    # Use the most recent driver
    driver = drivers[-1] if drivers else "SQL Server"

    try:
        if use_windows_auth:
            # Windows Authentication
            conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
        else:
            # SQL Server Authentication
            conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password};"

        print(f"Connection string: {conn_str}")
        print("Attempting connection...")

        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()[0]
            print(f"SUCCESS: Connected to SQL Server")
            print(f"Version: {version}")

            # Test if database exists
            cursor.execute("SELECT DB_NAME()")
            current_db = cursor.fetchone()[0]
            print(f"Current database: {current_db}")

            # List tables in the database
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """)
            tables = cursor.fetchall()
            if tables:
                print(f"Tables found: {[table[0] for table in tables]}")
            else:
                print("No tables found in database")

            return True

    except Exception as e:
        print(f"ERROR: Failed to connect to database")
        print(f"Error: {e}")

        # Try connecting to master database instead
        try:
            print("\nTrying to connect to master database...")
            if use_windows_auth:
                master_conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE=master;Trusted_Connection=yes;"
            else:
                master_conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE=master;UID={username};PWD={password};"

            with pyodbc.connect(master_conn_str) as conn:
                cursor = conn.cursor()
                print("SUCCESS: Connected to master database")

                # Check if our target database exists
                cursor.execute(
                    "SELECT name FROM sys.databases WHERE name = ?", database)
                db_exists = cursor.fetchone()
                if db_exists:
                    print(f"Database '{database}' exists")
                else:
                    print(f"Database '{database}' does NOT exist")

                    # List available databases
                    cursor.execute(
                        "SELECT name FROM sys.databases ORDER BY name")
                    databases = cursor.fetchall()
                    print(
                        f"Available databases: {[db[0] for db in databases]}")

                return True

        except Exception as e2:
            print(f"ERROR: Failed to connect to master database")
            print(f"Error: {e2}")
            return False


if __name__ == "__main__":
    test_direct_connection()
