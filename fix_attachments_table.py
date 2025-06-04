#!/usr/bin/env python3
"""
Force Create Attachments Table - Fix database schema issues
"""

import pyodbc
from config import Config

def force_create_attachments_table():
    """Force create the Attachments table with correct column names"""
    try:
        # Parse connection string
        connection_string = Config.SQLALCHEMY_DATABASE_URI.replace('mssql+pyodbc://', '')
        
        print("Connecting to database...")
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Drop existing Attachments table if it exists
        print("Dropping existing Attachments table if it exists...")
        cursor.execute("IF OBJECT_ID('Attachments', 'U') IS NOT NULL DROP TABLE Attachments")
        
        # Create Attachments table with correct column names
        print("Creating Attachments table...")
        create_table_sql = """
        CREATE TABLE Attachments (
            AttachmentID int IDENTITY(1,1) PRIMARY KEY,
            MessageID int NOT NULL,
            OriginalName nvarchar(255) NOT NULL,
            StoredName nvarchar(255) NOT NULL,
            FileSize int NOT NULL,
            MimeType nvarchar(100) NOT NULL,
            CreatedAt datetime2 DEFAULT GETDATE(),
            FOREIGN KEY (MessageID) REFERENCES Messages(MessageID)
        )
        """
        cursor.execute(create_table_sql)
        
        # Commit changes
        conn.commit()
        print("✅ Attachments table created successfully!")
        
        # Verify the table was created
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'Attachments'
            ORDER BY ORDINAL_POSITION
        """)
        
        columns = cursor.fetchall()
        print(f"\nVerified columns in Attachments table ({len(columns)}):")
        for col in columns:
            print(f"  - {col[0]} ({col[1]}) {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating Attachments table: {str(e)}")
        return False

if __name__ == '__main__':
    success = force_create_attachments_table()
    if success:
        print("\n🎉 Database schema fixed successfully!")
    else:
        print("\n💥 Failed to fix database schema.")
