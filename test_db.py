#!/usr/bin/env python3
"""
Quick database connection test
"""

import pyodbc
import sys

try:
    # Check ODBC drivers
    drivers = pyodbc.drivers()
    print('Available ODBC drivers:')
    for d in drivers:
        if 'SQL' in d:
            print(f'  - {d}')
    
    # Test connection
    conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=PRANAV\\SQLEXPRESS;DATABASE=SupportChatbot;Trusted_Connection=yes;'
    print(f'\nAttempting connection with: {conn_str}')
    
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    # Check if tables exist
    cursor.execute("SELECT name FROM sys.tables WHERE type = 'U'")
    tables = cursor.fetchall()
    print(f'\nTables in database:')
    for table in tables:
        print(f'  - {table[0]}')
    
    conn.close()
    print('\nDatabase connection successful!')
    
except Exception as e:
    print(f'Database connection failed: {e}')
    print('Trying alternative connection methods...')
    
    # Try without specifying database
    try:
        conn_str_alt = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=PRANAV\\SQLEXPRESS;Trusted_Connection=yes;'
        conn = pyodbc.connect(conn_str_alt)
        cursor = conn.cursor()
        
        # List available databases
        cursor.execute("SELECT name FROM sys.databases")
        databases = cursor.fetchall()
        print('\nAvailable databases:')
        for db in databases:
            print(f'  - {db[0]}')
        
        conn.close()
    except Exception as e2:
        print(f'Alternative connection also failed: {e2}')
        sys.exit(1)
