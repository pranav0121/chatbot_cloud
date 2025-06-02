import os
import sys
import pyodbc
from config import Config

def diagnose_connection():
    print("=== SQL Server Connection Diagnosis ===")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    
    # Print configuration
    print("\n=== Configuration ===")
    config = Config()
    print(f"DB_SERVER: {config.DB_SERVER}")
    print(f"DB_DATABASE: {config.DB_DATABASE}")
    print(f"DB_USERNAME: {config.DB_USERNAME}")
    print(f"DB_USE_WINDOWS_AUTH: {config.DB_USE_WINDOWS_AUTH}")
    print(f"Connection String: {config.SQLALCHEMY_DATABASE_URI}")
    
    # List available ODBC drivers
    print("\n=== Available ODBC Drivers ===")
    try:
        drivers = pyodbc.drivers()
        sql_drivers = [d for d in drivers if 'SQL Server' in d]
        if sql_drivers:
            for driver in sql_drivers:
                print(f"✓ {driver}")
        else:
            print("❌ No SQL Server ODBC drivers found!")
            print("Available drivers:", drivers)
    except Exception as e:
        print(f"Error listing drivers: {e}")
    
    # Test different connection strings
    print("\n=== Testing Connection Strings ===")
    
    test_connections = []
    
    # Windows Authentication options
    for driver in ['ODBC Driver 17 for SQL Server', 'SQL Server Native Client 11.0', 'SQL Server']:
        test_connections.append({
            'name': f'Windows Auth - {driver}',
            'conn_str': f'DRIVER={{{driver}}};SERVER={config.DB_SERVER};DATABASE={config.DB_DATABASE};Trusted_Connection=yes;'
        })
    
    # Test each connection
    for test in test_connections:
        try:
            print(f"\nTesting: {test['name']}")
            conn = pyodbc.connect(test['conn_str'], timeout=10)
            cursor = conn.cursor()
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()[0]
            print(f"✓ SUCCESS!")
            
            # Test if database exists
            cursor.execute("SELECT DB_ID('SupportChatbot')")
            db_id = cursor.fetchone()[0]
            if db_id:
                print(f"✓ SupportChatbot database exists (ID: {db_id})")
                
                # Check tables
                cursor.execute("USE SupportChatbot; SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
                table_count = cursor.fetchone()[0]
                print(f"✓ Found {table_count} tables in database")
                
                if table_count > 0:
                    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
                    tables = cursor.fetchall()
                    print("Tables:", [t[0] for t in tables])
            else:
                print("❌ SupportChatbot database does not exist")
            
            cursor.close()
            conn.close()
            
            # If this connection worked, update the config
            print(f"🎯 WORKING CONNECTION STRING: {test['conn_str']}")
            break
            
        except Exception as e:
            print(f"❌ FAILED: {str(e)}")
    
    print("\n=== Recommendations ===")
    print("1. If no connections worked, check if SQL Server is running:")
    print("   Get-Service -Name 'MSSQL$SQLEXPRESS'")
    print("2. If database doesn't exist, run the setup script")
    print("3. Update config.py with the working connection string")

if __name__ == "__main__":
    diagnose_connection()
