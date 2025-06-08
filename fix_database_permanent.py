"""
Permanent Database Fix Script for Support Chatbot
This script will completely recreate the database and fix all connection issues
"""
import pyodbc
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_SERVER = os.getenv('DB_SERVER', 'PRANAV\\SQLEXPRESS')
DB_DATABASE = os.getenv('DB_DATABASE', 'SupportChatbot')
DB_USERNAME = os.getenv('DB_USERNAME', 'sa')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_USE_WINDOWS_AUTH = os.getenv('DB_USE_WINDOWS_AUTH', 'True').lower() in ('true', '1', 't')

def get_connection_string(include_database=True):
    """Get connection string for pyodbc"""
    if DB_USE_WINDOWS_AUTH:
        if include_database:
            return f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={DB_SERVER};DATABASE={DB_DATABASE};Trusted_Connection=yes;'
        else:
            return f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={DB_SERVER};Trusted_Connection=yes;'
    else:
        if include_database:
            return f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={DB_SERVER};DATABASE={DB_DATABASE};UID={DB_USERNAME};PWD={DB_PASSWORD};'
        else:
            return f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={DB_SERVER};UID={DB_USERNAME};PWD={DB_PASSWORD};'

def test_sql_server_connection():
    """Test if SQL Server is accessible"""
    try:
        conn_str = get_connection_string(include_database=False)
        conn = pyodbc.connect(conn_str, timeout=10)
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()[0]
        print(f"✓ SQL Server connection successful!")
        print(f"  Version: {version[:100]}...")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"✗ SQL Server connection failed: {str(e)}")
        return False

def drop_and_create_database():
    """Drop existing database and create fresh one"""
    try:
        conn_str = get_connection_string(include_database=False)
        conn = pyodbc.connect(conn_str, timeout=10)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Drop database if exists
        print(f"Dropping database '{DB_DATABASE}' if it exists...")
        cursor.execute(f"""
            IF EXISTS (SELECT name FROM sys.databases WHERE name = N'{DB_DATABASE}')
            BEGIN
                ALTER DATABASE [{DB_DATABASE}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
                DROP DATABASE [{DB_DATABASE}];
            END
        """)
        
        # Create new database
        print(f"Creating database '{DB_DATABASE}'...")
        cursor.execute(f"CREATE DATABASE [{DB_DATABASE}]")
        
        print(f"✓ Database '{DB_DATABASE}' created successfully!")
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Error creating database: {str(e)}")
        return False

def create_tables():
    """Create all required tables with proper structure"""
    try:
        conn_str = get_connection_string(include_database=True)
        conn = pyodbc.connect(conn_str, timeout=10)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("Creating tables...")
        
        # Users table
        cursor.execute("""
            CREATE TABLE Users (
                UserID INT IDENTITY(1,1) PRIMARY KEY,
                Name NVARCHAR(100),
                Email NVARCHAR(255),
                CreatedAt DATETIME DEFAULT GETDATE()
            )
        """)
        print("✓ Users table created")
        
        # Categories table
        cursor.execute("""
            CREATE TABLE Categories (
                CategoryID INT IDENTITY(1,1) PRIMARY KEY,
                Name NVARCHAR(50) NOT NULL,
                Team NVARCHAR(50) NOT NULL,
                CreatedAt DATETIME DEFAULT GETDATE()
            )
        """)
        print("✓ Categories table created")
        
        # Tickets table
        cursor.execute("""
            CREATE TABLE Tickets (
                TicketID INT IDENTITY(1,1) PRIMARY KEY,
                UserID INT FOREIGN KEY REFERENCES Users(UserID),
                CategoryID INT FOREIGN KEY REFERENCES Categories(CategoryID),
                Subject NVARCHAR(255) NOT NULL,
                Status NVARCHAR(20) DEFAULT 'open',
                CreatedAt DATETIME DEFAULT GETDATE(),
                UpdatedAt DATETIME DEFAULT GETDATE()
            )
        """)
        print("✓ Tickets table created")
        
        # Messages table
        cursor.execute("""
            CREATE TABLE Messages (
                MessageID INT IDENTITY(1,1) PRIMARY KEY,
                TicketID INT FOREIGN KEY REFERENCES Tickets(TicketID),
                SenderID INT FOREIGN KEY REFERENCES Users(UserID),
                Content NTEXT NOT NULL,
                IsAdminReply BIT DEFAULT 0,
                CreatedAt DATETIME DEFAULT GETDATE()
            )
        """)
        print("✓ Messages table created")
        
        # CommonQueries table
        cursor.execute("""
            CREATE TABLE CommonQueries (
                QueryID INT IDENTITY(1,1) PRIMARY KEY,
                CategoryID INT FOREIGN KEY REFERENCES Categories(CategoryID),
                Question NVARCHAR(255) NOT NULL,
                Solution NTEXT NOT NULL,
                CreatedAt DATETIME DEFAULT GETDATE(),
                UpdatedAt DATETIME DEFAULT GETDATE()
            )
        """)
        print("✓ CommonQueries table created")
        
        # Feedback table
        cursor.execute("""
            CREATE TABLE Feedback (
                FeedbackID INT IDENTITY(1,1) PRIMARY KEY,
                TicketID INT FOREIGN KEY REFERENCES Tickets(TicketID),
                Rating INT NOT NULL,
                Comment NTEXT,
                CreatedAt DATETIME DEFAULT GETDATE()
            )
        """)
        print("✓ Feedback table created")
        
        # Attachments table
        cursor.execute("""
            CREATE TABLE Attachments (
                AttachmentID INT IDENTITY(1,1) PRIMARY KEY,
                MessageID INT FOREIGN KEY REFERENCES Messages(MessageID),
                OriginalName NVARCHAR(255) NOT NULL,
                StoredName NVARCHAR(255) NOT NULL,
                FileSize INT NOT NULL,
                MimeType NVARCHAR(100) NOT NULL,
                CreatedAt DATETIME DEFAULT GETDATE()
            )
        """)
        print("✓ Attachments table created")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Error creating tables: {str(e)}")
        return False

def insert_default_data():
    """Insert default categories and common queries"""
    try:
        conn_str = get_connection_string(include_database=True)
        conn = pyodbc.connect(conn_str, timeout=10)
        cursor = conn.cursor()
        
        print("Inserting default data...")
        
        # Insert default categories
        categories = [
            ('Payments', 'Billing'),
            ('Product Issues', 'Product'),
            ('Technical Glitches', 'Tech'),
            ('General Inquiries', 'General')
        ]
        
        for name, team in categories:
            cursor.execute("INSERT INTO Categories (Name, Team) VALUES (?, ?)", name, team)
        
        print("✓ Default categories inserted")
        
        # Insert common queries
        common_queries = [
            (1, 'How do I update my payment method?', 
             'You can update your payment method by going to Settings > Billing > Payment Methods and clicking "Add New Method".'),
            (1, 'When will I be charged?', 
             'Billing occurs on the first of each month for monthly plans. Annual plans are billed on your subscription anniversary date.'),
            (2, 'Product features not working', 
             'Please try clearing your browser cache and refreshing the page. If the issue persists, try logging out and back in.'),
            (3, 'Cannot login to account', 
             'First, ensure your caps lock is off and you\'re using the correct email address. If you still can\'t login, use the "Forgot Password" link to reset your password.'),
            (4, 'How do I contact support?', 
             'You can contact our support team through this chat interface or by sending an email to support@example.com')
        ]
        
        for category_id, question, solution in common_queries:
            cursor.execute(
                "INSERT INTO CommonQueries (CategoryID, Question, Solution) VALUES (?, ?, ?)",
                category_id, question, solution
            )
        
        print("✓ Common queries inserted")
        
        # Create a test user and ticket for verification
        cursor.execute("INSERT INTO Users (Name, Email) VALUES (?, ?)", "Test User", "test@example.com")
        cursor.execute("SELECT SCOPE_IDENTITY()")
        user_id = cursor.fetchone()[0]
        
        cursor.execute(
            "INSERT INTO Tickets (UserID, CategoryID, Subject, Status) VALUES (?, ?, ?, ?)",
            user_id, 1, "Test Support Ticket", "open"
        )
        cursor.execute("SELECT SCOPE_IDENTITY()")
        ticket_id = cursor.fetchone()[0]
        
        cursor.execute(
            "INSERT INTO Messages (TicketID, SenderID, Content, IsAdminReply) VALUES (?, ?, ?, ?)",
            ticket_id, user_id, "This is a test message to verify the database is working correctly.", 0
        )
        
        print("✓ Test data inserted")
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Error inserting default data: {str(e)}")
        return False

def verify_database():
    """Verify the database is working correctly"""
    try:
        conn_str = get_connection_string(include_database=True)
        conn = pyodbc.connect(conn_str, timeout=10)
        cursor = conn.cursor()
        
        print("Verifying database...")
        
        # Check tables exist
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """)
        tables = [row[0] for row in cursor.fetchall()]
        expected_tables = ['Attachments', 'Categories', 'CommonQueries', 'Feedback', 'Messages', 'Tickets', 'Users']
        
        print(f"  Tables found: {tables}")
        
        if all(table in tables for table in expected_tables):
            print("✓ All required tables exist")
        else:
            print("✗ Some tables are missing")
            return False
        
        # Check data
        cursor.execute("SELECT COUNT(*) FROM Categories")
        category_count = cursor.fetchone()[0]
        print(f"  Categories: {category_count}")
        
        cursor.execute("SELECT COUNT(*) FROM CommonQueries")
        query_count = cursor.fetchone()[0]
        print(f"  Common Queries: {query_count}")
        
        cursor.execute("SELECT COUNT(*) FROM Tickets")
        ticket_count = cursor.fetchone()[0]
        print(f"  Tickets: {ticket_count}")
        
        if category_count >= 4 and query_count >= 5 and ticket_count >= 1:
            print("✓ Database verification successful!")
        else:
            print("✗ Database verification failed - insufficient data")
            return False
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Database verification failed: {str(e)}")
        return False

def main():
    """Main function to recreate database"""
    print("=== Support Chatbot Database Recreation ===")
    print(f"Server: {DB_SERVER}")
    print(f"Database: {DB_DATABASE}")
    print(f"Windows Auth: {DB_USE_WINDOWS_AUTH}")
    print()
    
    # Step 1: Test SQL Server connection
    if not test_sql_server_connection():
        print("\n❌ Cannot connect to SQL Server. Please ensure:")
        print("  1. SQL Server is running")
        print("  2. Server name is correct in .env file")
        print("  3. Authentication settings are correct")
        return False
    
    # Step 2: Drop and create database
    if not drop_and_create_database():
        print("\n❌ Failed to create database")
        return False
    
    # Step 3: Create tables
    if not create_tables():
        print("\n❌ Failed to create tables")
        return False
    
    # Step 4: Insert default data
    if not insert_default_data():
        print("\n❌ Failed to insert default data")
        return False
    
    # Step 5: Verify database
    if not verify_database():
        print("\n❌ Database verification failed")
        return False
    
    print("\n🎉 Database recreation completed successfully!")
    print("   The admin panel should now work without any database errors.")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
