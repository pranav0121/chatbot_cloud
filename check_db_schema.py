#!/usr/bin/env python3
"""
Check Database Schema - Verify table structures
"""

import pyodbc
from config import Config

def check_database_schema():
    """Check the actual database schema"""
    try:
        # Parse connection string
        connection_string = Config.SQLALCHEMY_DATABASE_URI.replace('mssql+pyodbc://', '')
        
        print("Checking database schema...")
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Check if Attachments table exists
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE' 
            AND TABLE_NAME = 'Attachments'
        """)
        
        tables = cursor.fetchall()
        if tables:
            print("✅ Attachments table exists")
            
            # Get column names for Attachments table
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'Attachments'
                ORDER BY ORDINAL_POSITION
            """)
            
            columns = cursor.fetchall()
            print("\nAttachments table columns:")
            for col in columns:
                print(f"  - {col[0]} ({col[1]}) {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
        else:
            print("❌ Attachments table does not exist")
            
        # List all tables
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE' 
            ORDER BY TABLE_NAME
        """)
        
        all_tables = cursor.fetchall()
        print(f"\nAll tables in database ({len(all_tables)}):")
        for table in all_tables:
            print(f"  - {table[0]}")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error checking database schema: {str(e)}")
        return False

if __name__ == '__main__':
    check_database_schema()
