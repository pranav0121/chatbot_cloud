#!/usr/bin/env python3
"""
MSSQL Database Setup and Verification Script
This script ensures proper MSSQL setup with all required tables and data
"""

import pyodbc
import logging
import sys
import os
from urllib.parse import quote_plus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_odbc_drivers():
    """Check available ODBC drivers for SQL Server"""
    try:
        drivers = pyodbc.drivers()
        sql_drivers = [d for d in drivers if 'SQL Server' in d]
        logger.info("Available SQL Server ODBC drivers:")
        for driver in sql_drivers:
            logger.info(f"  - {driver}")
        return sql_drivers
    except Exception as e:
        logger.error(f"Error checking ODBC drivers: {e}")
        return []

def get_connection_string():
    """Get the proper MSSQL connection string"""
    # Check for environment variables first
    server = os.getenv('DB_SERVER', 'PRANAV\\SQLEXPRESS')
    database = os.getenv('DB_DATABASE', 'SupportChatbot')
    
    # Try different driver options
    drivers_to_try = [
        'ODBC Driver 17 for SQL Server',
        'ODBC Driver 13 for SQL Server',
        'ODBC Driver 11 for SQL Server',
        'SQL Server Native Client 11.0',
        'SQL Server'
    ]
    
    available_drivers = check_odbc_drivers()
    
    # Find the best available driver
    driver_to_use = None
    for driver in drivers_to_try:
        if driver in available_drivers:
            driver_to_use = driver
            break
    
    if not driver_to_use:
        logger.error("No suitable SQL Server ODBC driver found!")
        return None
    
    logger.info(f"Using driver: {driver_to_use}")
    
    # Build connection string with Windows Authentication
    conn_string = f"DRIVER={{{driver_to_use}}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
    
    logger.info(f"Connection string: {conn_string}")
    return conn_string

def test_connection():
    """Test MSSQL connection"""
    try:
        conn_string = get_connection_string()
        if not conn_string:
            return False, "No suitable ODBC driver found"
        
        logger.info("Testing database connection...")
        conn = pyodbc.connect(conn_string, timeout=30)
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        
        if result and result[0] == 1:
            cursor.close()
            conn.close()
            logger.info("✅ Database connection successful!")
            return True, "Connection successful"
        else:
            cursor.close()
            conn.close()
            return False, "Test query failed"
            
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False, str(e)

def create_database_if_not_exists():
    """Create the database if it doesn't exist"""
    try:
        # Connect to master database first
        server = os.getenv('DB_SERVER', 'PRANAV\\SQLEXPRESS')
        database = 'SupportChatbot'
        
        conn_string = get_connection_string()
        if not conn_string:
            return False, "No ODBC driver available"
        
        # Modify connection string to connect to master
        master_conn_string = conn_string.replace(f"DATABASE={database}", "DATABASE=master")
        
        logger.info("Connecting to master database to check/create SupportChatbot...")
        conn = pyodbc.connect(master_conn_string, timeout=30)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM sys.databases 
            WHERE name = ?
        """, database)
        
        db_exists = cursor.fetchone()[0] > 0
        
        if not db_exists:
            logger.info(f"Creating database '{database}'...")
            cursor.execute(f"CREATE DATABASE [{database}]")
            logger.info(f"✅ Database '{database}' created successfully!")
        else:
            logger.info(f"✅ Database '{database}' already exists")
        
        cursor.close()
        conn.close()
        return True, "Database ready"
        
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        return False, str(e)

def create_tables():
    """Create all required tables with proper schema"""
    try:
        conn_string = get_connection_string()
        conn = pyodbc.connect(conn_string, timeout=30)
        cursor = conn.cursor()
        
        logger.info("Creating database tables...")
        
        # Create Categories table
        logger.info("Creating Categories table...")
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Categories' AND type='U')
            CREATE TABLE Categories (
                CategoryID int IDENTITY(1,1) PRIMARY KEY,
                Name nvarchar(100) NOT NULL,
                Description nvarchar(500),
                Team nvarchar(50) NOT NULL DEFAULT 'General',
                CreatedAt datetime2 DEFAULT GETDATE()
            )
        """)
        
        # Create Users table
        logger.info("Creating Users table...")
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Users' AND type='U')
            CREATE TABLE Users (
                UserID int IDENTITY(1,1) PRIMARY KEY,
                Name nvarchar(100) NOT NULL,
                Email nvarchar(255) NOT NULL UNIQUE,
                PasswordHash nvarchar(255) NOT NULL,
                OrganizationName nvarchar(200),
                Position nvarchar(100),
                PriorityLevel nvarchar(20) DEFAULT 'medium',
                Phone nvarchar(20),
                Department nvarchar(100),
                PreferredLanguage nvarchar(10) DEFAULT 'en',
                IsActive bit DEFAULT 1,
                IsAdmin bit DEFAULT 0,
                LastLogin datetime2,
                CreatedAt datetime2 DEFAULT GETDATE()
            )
        """)
        
        # Create Tickets table with all required columns
        logger.info("Creating Tickets table...")
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Tickets' AND type='U')
            CREATE TABLE Tickets (
                TicketID int IDENTITY(1,1) PRIMARY KEY,
                UserID int,
                CategoryID int,
                Subject nvarchar(255) NOT NULL,
                Priority nvarchar(20) DEFAULT 'medium',
                Status nvarchar(20) DEFAULT 'open',
                OrganizationName nvarchar(200),
                CreatedBy nvarchar(100),
                AssignedTo int,
                CreatedAt datetime2 DEFAULT GETDATE(),
                UpdatedAt datetime2 DEFAULT GETDATE(),
                FOREIGN KEY (UserID) REFERENCES Users(UserID),
                FOREIGN KEY (CategoryID) REFERENCES Categories(CategoryID),
                FOREIGN KEY (AssignedTo) REFERENCES Users(UserID)
            )
        """)
        
        # Create Messages table
        logger.info("Creating Messages table...")
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Messages' AND type='U')
            CREATE TABLE Messages (
                MessageID int IDENTITY(1,1) PRIMARY KEY,
                TicketID int NOT NULL,
                SenderID int,
                Content ntext NOT NULL,
                IsAdminReply bit DEFAULT 0,
                CreatedAt datetime2 DEFAULT GETDATE(),
                FOREIGN KEY (TicketID) REFERENCES Tickets(TicketID),
                FOREIGN KEY (SenderID) REFERENCES Users(UserID)
            )
        """)
        
        # Create CommonQueries table
        logger.info("Creating CommonQueries table...")
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='CommonQueries' AND type='U')
            CREATE TABLE CommonQueries (
                QueryID int IDENTITY(1,1) PRIMARY KEY,
                CategoryID int NOT NULL,
                Question nvarchar(255) NOT NULL,
                Solution ntext NOT NULL,
                CreatedAt datetime2 DEFAULT GETDATE(),
                UpdatedAt datetime2 DEFAULT GETDATE(),
                FOREIGN KEY (CategoryID) REFERENCES Categories(CategoryID)
            )
        """)
        
        # Create Attachments table
        logger.info("Creating Attachments table...")
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Attachments' AND type='U')
            CREATE TABLE Attachments (
                AttachmentID int IDENTITY(1,1) PRIMARY KEY,
                MessageID int,
                OriginalName nvarchar(255) NOT NULL,
                StoredName nvarchar(255) NOT NULL,
                FileSize int NOT NULL,
                MimeType nvarchar(100) NOT NULL,
                CreatedAt datetime2 DEFAULT GETDATE(),
                FOREIGN KEY (MessageID) REFERENCES Messages(MessageID)
            )
        """)
        
        # Create Feedback table
        logger.info("Creating Feedback table...")
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Feedback' AND type='U')
            CREATE TABLE Feedback (
                FeedbackID int IDENTITY(1,1) PRIMARY KEY,
                TicketID int NOT NULL,
                Rating int NOT NULL,
                Comment ntext,
                CreatedAt datetime2 DEFAULT GETDATE(),
                FOREIGN KEY (TicketID) REFERENCES Tickets(TicketID)
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("✅ All tables created successfully!")
        return True, "Tables created"
        
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        return False, str(e)

def create_sample_data():
    """Create sample data for testing"""
    try:
        from werkzeug.security import generate_password_hash
        
        conn_string = get_connection_string()
        conn = pyodbc.connect(conn_string, timeout=30)
        cursor = conn.cursor()
        
        logger.info("Creating sample data...")
        
        # Create categories
        categories = [
            ('Technical Support', 'Technical issues and troubleshooting', 'Tech'),
            ('Account Management', 'Account-related requests and changes', 'Admin'),
            ('Billing & Payment', 'Billing inquiries and payment issues', 'Billing'),
            ('Feature Request', 'New feature requests and suggestions', 'Product'),
            ('Bug Report', 'Software bugs and issues', 'Tech')
        ]
        
        for name, description, team in categories:
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM Categories WHERE Name = ?)
                INSERT INTO Categories (Name, Description, Team) VALUES (?, ?, ?)
            """, name, name, description, team)
        
        # Create admin user
        admin_email = 'admin@supportcenter.com'
        cursor.execute("SELECT COUNT(*) FROM Users WHERE Email = ?", admin_email)
        if cursor.fetchone()[0] == 0:
            admin_password = generate_password_hash('admin123')
            cursor.execute("""
                INSERT INTO Users (Name, Email, PasswordHash, OrganizationName, Position, 
                                 PriorityLevel, IsActive, IsAdmin) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, 'System Administrator', admin_email, admin_password, 
                'Support Center', 'Administrator', 'critical', 1, 1)
            logger.info("Created admin user: admin@supportcenter.com / admin123")
        
        # Create test users
        test_users = [
            ('John Doe', 'john.doe@techcorp.com', 'TechCorp Inc', 'Senior Developer', 'high'),
            ('Jane Smith', 'jane.smith@abccompany.com', 'ABC Company Ltd', 'Project Manager', 'medium'),
            ('Bob Johnson', 'bob.johnson@xyzsolutions.com', 'XYZ Solutions', 'IT Specialist', 'medium')
        ]
        
        for name, email, org, position, priority in test_users:
            cursor.execute("SELECT COUNT(*) FROM Users WHERE Email = ?", email)
            if cursor.fetchone()[0] == 0:
                password = generate_password_hash('password123')
                cursor.execute("""
                    INSERT INTO Users (Name, Email, PasswordHash, OrganizationName, Position, 
                                     PriorityLevel, IsActive, IsAdmin) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, name, email, password, org, position, priority, 1, 0)
        
        # Get category and user IDs
        cursor.execute("SELECT CategoryID FROM Categories WHERE Name = 'Technical Support'")
        tech_category_id = cursor.fetchone()[0]
        
        cursor.execute("SELECT UserID FROM Users WHERE Email = 'john.doe@techcorp.com'")
        user_id = cursor.fetchone()[0]
        
        cursor.execute("SELECT UserID FROM Users WHERE IsAdmin = 1")
        admin_id = cursor.fetchone()[0]
        
        # Create sample tickets
        sample_tickets = [
            ('Critical System Outage - Production Down', 'critical', 'open', 'TechCorp Inc', 'John Doe'),
            ('Database Performance Issues', 'high', 'in_progress', 'TechCorp Inc', 'John Doe'),
            ('Password Reset Request', 'medium', 'open', 'ABC Company Ltd', 'Jane Smith'),
            ('Software Installation Help', 'low', 'resolved', 'XYZ Solutions', 'Bob Johnson')
        ]
        
        for subject, priority, status, org, created_by in sample_tickets:
            cursor.execute("SELECT COUNT(*) FROM Tickets WHERE Subject = ?", subject)
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO Tickets (UserID, CategoryID, Subject, Priority, Status, 
                                       OrganizationName, CreatedBy, AssignedTo) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, user_id, tech_category_id, subject, priority, status, org, created_by, 
                    admin_id if status in ['in_progress', 'resolved'] else None)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("✅ Sample data created successfully!")
        return True, "Sample data created"
        
    except Exception as e:
        logger.error(f"Error creating sample data: {e}")
        return False, str(e)

def verify_database():
    """Verify the database setup"""
    try:
        conn_string = get_connection_string()
        conn = pyodbc.connect(conn_string, timeout=30)
        cursor = conn.cursor()
        
        logger.info("Verifying database setup...")
        
        # Check tables
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """)
        tables = [row[0] for row in cursor.fetchall()]
        logger.info(f"Found tables: {', '.join(tables)}")
        
        # Check data counts
        counts = {}
        for table in ['Users', 'Categories', 'Tickets', 'Messages']:
            if table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                counts[table] = cursor.fetchone()[0]
        
        logger.info("Data counts:")
        for table, count in counts.items():
            logger.info(f"  {table}: {count} records")
        
        cursor.close()
        conn.close()
        
        logger.info("✅ Database verification complete!")
        return True, counts
        
    except Exception as e:
        logger.error(f"Error verifying database: {e}")
        return False, str(e)

def main():
    """Main setup function"""
    logger.info("=== MSSQL Database Setup ===")
    
    # Step 1: Check ODBC drivers
    logger.info("Step 1: Checking ODBC drivers...")
    available_drivers = check_odbc_drivers()
    if not available_drivers:
        logger.error("❌ No SQL Server ODBC drivers found!")
        return False
    
    # Step 2: Create database if needed
    logger.info("Step 2: Creating database if needed...")
    success, message = create_database_if_not_exists()
    if not success:
        logger.error(f"❌ Database creation failed: {message}")
        return False
    
    # Step 3: Test connection
    logger.info("Step 3: Testing database connection...")
    success, message = test_connection()
    if not success:
        logger.error(f"❌ Connection test failed: {message}")
        return False
    
    # Step 4: Create tables
    logger.info("Step 4: Creating database tables...")
    success, message = create_tables()
    if not success:
        logger.error(f"❌ Table creation failed: {message}")
        return False
    
    # Step 5: Create sample data
    logger.info("Step 5: Creating sample data...")
    success, message = create_sample_data()
    if not success:
        logger.error(f"❌ Sample data creation failed: {message}")
        return False
    
    # Step 6: Verify setup
    logger.info("Step 6: Verifying database setup...")
    success, counts = verify_database()
    if not success:
        logger.error(f"❌ Database verification failed: {counts}")
        return False
    
    logger.info("🎉 MSSQL Database setup completed successfully!")
    logger.info("")
    logger.info("=== Setup Summary ===")
    logger.info("✅ ODBC drivers available")
    logger.info("✅ Database created/verified")
    logger.info("✅ Connection successful")
    logger.info("✅ Tables created")
    logger.info("✅ Sample data loaded")
    logger.info("✅ Database verified")
    logger.info("")
    logger.info("Admin Login Credentials:")
    logger.info("  Email: admin@supportcenter.com")
    logger.info("  Password: admin123")
    logger.info("")
    logger.info("You can now start the Flask application!")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
