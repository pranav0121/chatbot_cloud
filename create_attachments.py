import pyodbc
import os

def create_attachments_table():
    try:
        # Direct connection to SQL Server using Windows Authentication
        server = 'localhost'
        database = 'SupportChatbot'
        
        # Connection string for Windows Authentication
        connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
        
        print("Connecting to database...")
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Check if Attachments table exists
        cursor.execute("""
            SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = 'Attachments'
        """)
        
        exists = cursor.fetchone()[0]
        
        if exists:
            print("Attachments table already exists. Dropping and recreating...")
            cursor.execute("DROP TABLE Attachments")
        
        # Create Attachments table
        print("Creating Attachments table...")
        create_sql = """
        CREATE TABLE Attachments (
            AttachmentID int IDENTITY(1,1) PRIMARY KEY,
            MessageID int NOT NULL,
            OriginalName nvarchar(255) NOT NULL,
            StoredName nvarchar(255) NOT NULL,
            FileSize int NOT NULL,
            MimeType nvarchar(100) NOT NULL,
            CreatedAt datetime2 DEFAULT GETDATE(),
            CONSTRAINT FK_Attachments_Messages 
                FOREIGN KEY (MessageID) REFERENCES Messages(MessageID)
        )
        """
        
        cursor.execute(create_sql)
        conn.commit()
        
        print("✅ SUCCESS: Attachments table created!")
        
        # Verify columns
        cursor.execute("""
            SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'Attachments' ORDER BY ORDINAL_POSITION
        """)
        
        columns = [row[0] for row in cursor.fetchall()]
        print(f"Columns created: {columns}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == '__main__':
    create_attachments_table()
