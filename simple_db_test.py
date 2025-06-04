import pyodbc

# Simple test to check database connection and create table
try:
    print("Testing database connection...")
    
    # Connection string
    conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=SupportChatbot;Trusted_Connection=yes;'
    
    # Connect
    conn = pyodbc.connect(conn_str)
    print("✅ Connected to database successfully!")
    
    cursor = conn.cursor()
    
    # Check existing tables
    cursor.execute("SELECT name FROM sys.tables ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Existing tables: {tables}")
    
    # Check if Attachments table exists
    if 'Attachments' in tables:
        print("Attachments table exists - checking columns...")
        cursor.execute("""
            SELECT c.name FROM sys.columns c 
            JOIN sys.tables t ON c.object_id = t.object_id 
            WHERE t.name = 'Attachments'
            ORDER BY c.column_id
        """)
        columns = [row[0] for row in cursor.fetchall()]
        print(f"Attachments columns: {columns}")
    else:
        print("Attachments table does not exist - creating it...")
        
        # Create table
        create_sql = """
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
        
        cursor.execute(create_sql)
        conn.commit()
        print("✅ Attachments table created successfully!")
    
    conn.close()
    print("✅ Database test completed successfully!")
    
except Exception as e:
    print(f"❌ Database test failed: {e}")
    import traceback
    traceback.print_exc()
