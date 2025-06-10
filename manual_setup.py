#!/usr/bin/env python3
"""
Manual MSSQL Database Setup
"""

import pyodbc
import logging
import sys
import os

# Configure logging to console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def check_drivers():
    """Check available ODBC drivers"""
    try:
        drivers = pyodbc.drivers()
        sql_drivers = [d for d in drivers if 'SQL Server' in d]
        logger.info("Available SQL Server ODBC drivers:")
        for driver in sql_drivers:
            logger.info(f"  - {driver}")
        return sql_drivers
    except Exception as e:
        logger.error(f"Error checking drivers: {e}")
        return []

def get_connection():
    """Get database connection"""
    server = 'PRANAV\\SQLEXPRESS'
    database = 'SupportChatbot'
    
    # Try different drivers
    drivers_to_try = [
        'ODBC Driver 17 for SQL Server',
        'SQL Server Native Client 11.0',
        'SQL Server'
    ]
    
    for driver in drivers_to_try:
        try:
            conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};Trusted_Connection=yes;"
            logger.info(f"Trying connection with driver: {driver}")
            conn = pyodbc.connect(conn_str, timeout=30)
            logger.info(f"✅ Connected successfully with {driver}")
            return conn
        except Exception as e:
            logger.warning(f"Failed with {driver}: {e}")
            continue
    
    return None

def create_database():
    """Create database if it doesn't exist"""
    server = 'PRANAV\\SQLEXPRESS'
    
    for driver in ['ODBC Driver 17 for SQL Server', 'SQL Server Native Client 11.0', 'SQL Server']:
        try:
            # Connect to master database
            conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE=master;Trusted_Connection=yes;"
            conn = pyodbc.connect(conn_str, timeout=30)
            cursor = conn.cursor()
            
            # Check if database exists
            cursor.execute("SELECT database_id FROM sys.databases WHERE name = 'SupportChatbot'")
            exists = cursor.fetchone()
            
            if not exists:
                logger.info("Creating SupportChatbot database...")
                cursor.execute("CREATE DATABASE SupportChatbot")
                conn.commit()
                logger.info("✅ Database created")
            else:
                logger.info("✅ Database already exists")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            logger.warning(f"Database creation failed with {driver}: {e}")
            continue
    
    return False

def create_tables():
    """Create tables"""
    conn = get_connection()
    if not conn:
        logger.error("❌ Cannot connect to database")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Create Users table
        users_table = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Users' AND xtype='U')
        CREATE TABLE Users (
            UserID int IDENTITY(1,1) PRIMARY KEY,
            Email nvarchar(255) UNIQUE NOT NULL,
            PasswordHash nvarchar(255) NOT NULL,
            FullName nvarchar(255) NOT NULL,
            OrganizationName nvarchar(255),
            Position nvarchar(255),
            PriorityLevel nvarchar(50) DEFAULT 'low',
            Phone nvarchar(20),
            Department nvarchar(255),
            DateCreated datetime2 DEFAULT GETDATE(),
            LastLogin datetime2,
            IsActive bit DEFAULT 1,
            IsAdmin bit DEFAULT 0
        )
        """
        
        logger.info("Creating Users table...")
        cursor.execute(users_table)
        
        # Create Tickets table
        tickets_table = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Tickets' AND xtype='U')
        CREATE TABLE Tickets (
            TicketID int IDENTITY(1,1) PRIMARY KEY,
            Subject nvarchar(255) NOT NULL,
            Description ntext,
            Category nvarchar(100),
            Priority nvarchar(50) DEFAULT 'medium',
            Status nvarchar(50) DEFAULT 'open',
            CreatedAt datetime2 DEFAULT GETDATE(),
            UpdatedAt datetime2 DEFAULT GETDATE(),
            Email nvarchar(255),
            FullName nvarchar(255),
            Phone nvarchar(20),
            OrganizationName nvarchar(255),
            CreatedBy int,
            AssignedTo int,
            FOREIGN KEY (CreatedBy) REFERENCES Users(UserID),
            FOREIGN KEY (AssignedTo) REFERENCES Users(UserID)
        )
        """
        
        logger.info("Creating Tickets table...")
        cursor.execute(tickets_table)
        
        conn.commit()
        logger.info("✅ Tables created successfully")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Table creation failed: {e}")
        return False

def create_admin_user():
    """Create admin user"""
    conn = get_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Check if admin exists
        cursor.execute("SELECT UserID FROM Users WHERE Email = 'admin@supportcenter.com'")
        exists = cursor.fetchone()
        
        if not exists:
            # Create admin user (password: admin123)
            # This is a bcrypt hash of 'admin123'
            password_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewlqkkMCHUdE3M2e'
            
            cursor.execute("""
                INSERT INTO Users (Email, PasswordHash, FullName, OrganizationName, Position, PriorityLevel, IsAdmin, IsActive)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                'admin@supportcenter.com',
                password_hash,
                'System Administrator',
                'Support Center',
                'Administrator',
                'critical',
                1,
                1
            ))
            
            conn.commit()
            logger.info("✅ Admin user created")
        else:
            logger.info("✅ Admin user already exists")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Admin user creation failed: {e}")
        return False

def verify_setup():
    """Verify the setup"""
    conn = get_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT COUNT(*) FROM Users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Tickets")
        ticket_count = cursor.fetchone()[0]
        
        logger.info(f"✅ Setup verified - Users: {user_count}, Tickets: {ticket_count}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}")
        return False

def main():
    """Main setup function"""
    logger.info("=== Manual MSSQL Database Setup ===")
    
    # Step 1: Check drivers
    logger.info("Step 1: Checking ODBC drivers...")
    drivers = check_drivers()
    if not drivers:
        logger.error("❌ No SQL Server drivers found")
        return False
    
    # Step 2: Create database
    logger.info("Step 2: Creating database...")
    if not create_database():
        logger.error("❌ Database creation failed")
        return False
    
    # Step 3: Create tables
    logger.info("Step 3: Creating tables...")
    if not create_tables():
        logger.error("❌ Table creation failed")
        return False
    
    # Step 4: Create admin user
    logger.info("Step 4: Creating admin user...")
    if not create_admin_user():
        logger.error("❌ Admin user creation failed")
        return False
    
    # Step 5: Verify setup
    logger.info("Step 5: Verifying setup...")
    if not verify_setup():
        logger.error("❌ Setup verification failed")
        return False
    
    logger.info("✅ Database setup completed successfully!")
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
