import pyodbc
import sys

print("Testing pyodbc connection...")

try:
    # Test basic pyodbc functionality
    drivers = pyodbc.drivers()
    print(f"Found {len(drivers)} ODBC drivers")
    
    sql_drivers = [d for d in drivers if 'SQL' in d]
    print(f"SQL Server drivers: {sql_drivers}")
    
    # Try to connect
    server = 'PRANAV\\SQLEXPRESS'
    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE=master;Trusted_Connection=yes;"
    print(f"Trying connection: {conn_str}")
    
    conn = pyodbc.connect(conn_str, timeout=10)
    print("✅ Connected to SQL Server")
    
    cursor = conn.cursor()
    cursor.execute("SELECT @@VERSION")
    version = cursor.fetchone()[0]
    print(f"SQL Server Version: {version[:100]}...")
    
    # Check if SupportChatbot database exists
    cursor.execute("SELECT database_id FROM sys.databases WHERE name = 'SupportChatbot'")
    db_exists = cursor.fetchone()
    
    if db_exists:
        print("✅ SupportChatbot database exists")
    else:
        print("Creating SupportChatbot database...")
        cursor.execute("CREATE DATABASE SupportChatbot")
        conn.commit()
        print("✅ SupportChatbot database created")
    
    cursor.close()
    conn.close()
    print("✅ Database setup successful")
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
