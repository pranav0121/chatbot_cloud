#!/usr/bin/env python3
"""
Database Migration Script for User Registration and Organization System
This script safely migrates the existing database to support the new user registration
and organization management features.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pyodbc
import logging
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Get database connection using the same config as the main app"""
    config = Config()
    
    # Use pyodbc connection directly
    if config.DB_USE_WINDOWS_AUTH:
        # Use Windows Authentication
        connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config.DB_SERVER};DATABASE={config.DB_DATABASE};Trusted_Connection=yes'
    else:
        # Use SQL Server Authentication
        connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config.DB_SERVER};DATABASE={config.DB_DATABASE};UID={config.DB_USERNAME};PWD={config.DB_PASSWORD}'
    
    return pyodbc.connect(connection_string)

def check_column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table"""
    cursor.execute("""
        SELECT COUNT(*) 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = ? AND COLUMN_NAME = ?
    """, table_name, column_name)
    return cursor.fetchone()[0] > 0

def check_table_exists(cursor, table_name):
    """Check if a table exists"""
    cursor.execute("""
        SELECT COUNT(*) 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_NAME = ?
    """, table_name)
    return cursor.fetchone()[0] > 0

def migrate_user_table(cursor):
    """Migrate the Users table to include new organization fields"""
    logger.info("Migrating Users table...")
    
    # Check if table exists, if not create it
    if not check_table_exists(cursor, 'Users'):
        logger.info("Creating Users table...")
        cursor.execute("""
            CREATE TABLE [Users] (
                UserID int IDENTITY(1,1) PRIMARY KEY,
                Name nvarchar(100) NOT NULL,
                Email nvarchar(255) NOT NULL UNIQUE,
                PasswordHash nvarchar(255) NOT NULL,
                OrganizationName nvarchar(255),
                Position nvarchar(100),
                PriorityLevel nvarchar(20) DEFAULT 'medium',
                Phone nvarchar(20),
                Department nvarchar(100),
                CreatedAt datetime2 DEFAULT GETDATE(),
                LastLogin datetime2,
                IsActive bit DEFAULT 1,
                IsAdmin bit DEFAULT 0
            )        """)
        logger.info("Users table created successfully")
        return
    
    # Add new columns if they don't exist
    new_columns = [
        ('OrganizationName', 'nvarchar(255)'),
        ('Position', 'nvarchar(100)'),
        ('PriorityLevel', 'nvarchar(20)', 'medium'),
        ('Phone', 'nvarchar(20)'),
        ('Department', 'nvarchar(100)'),
        ('LastLogin', 'datetime2'),
        ('IsActive', 'bit', '1'),
        ('IsAdmin', 'bit', '0')
    ]
    
    for column_info in new_columns:
        column_name = column_info[0]
        column_type = column_info[1]
        default_value = column_info[2] if len(column_info) > 2 else None
        
        if not check_column_exists(cursor, 'Users', column_name):
            logger.info(f"Adding column {column_name} to Users table...")
            
            if default_value:
                if column_type == 'bit':
                    cursor.execute(f"ALTER TABLE [Users] ADD {column_name} {column_type} DEFAULT {default_value}")
                else:
                    cursor.execute(f"ALTER TABLE [Users] ADD {column_name} {column_type} DEFAULT '{default_value}'")
            else:
                cursor.execute(f"ALTER TABLE [Users] ADD {column_name} {column_type}")
            
            logger.info(f"Column {column_name} added successfully")
        else:
            logger.info(f"Column {column_name} already exists")

def migrate_ticket_table(cursor):
    """Migrate the Ticket table to include organization and priority fields"""
    logger.info("Migrating Ticket table...")
    
    # Check if table exists
    if not check_table_exists(cursor, 'Ticket'):
        logger.info("Ticket table doesn't exist, will be created by the app")
        return
    
    # Add new columns if they don't exist
    new_columns = [
        ('Priority', 'nvarchar(20)', 'medium'),
        ('OrganizationName', 'nvarchar(255)'),
        ('CreatedBy', 'int'),
        ('AssignedTo', 'int')
    ]
    
    for column_info in new_columns:
        column_name = column_info[0]
        column_type = column_info[1]
        default_value = column_info[2] if len(column_info) > 2 else None
        
        if not check_column_exists(cursor, 'Ticket', column_name):
            logger.info(f"Adding column {column_name} to Ticket table...")
            
            if default_value:
                cursor.execute(f"ALTER TABLE Ticket ADD {column_name} {column_type} DEFAULT '{default_value}'")
            else:
                cursor.execute(f"ALTER TABLE Ticket ADD {column_name} {column_type}")
            
            logger.info(f"Column {column_name} added successfully")
        else:
            logger.info(f"Column {column_name} already exists")
    
    # Add foreign key constraints if they don't exist
    try:
        # Check if foreign key constraints exist
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS 
            WHERE CONSTRAINT_NAME IN ('FK_Ticket_CreatedBy', 'FK_Ticket_AssignedTo')
        """)
        existing_constraints = cursor.fetchone()[0]
        
        if existing_constraints == 0:
            logger.info("Adding foreign key constraints...")
              # Add foreign key for CreatedBy
            cursor.execute("""
                ALTER TABLE Ticket 
                ADD CONSTRAINT FK_Ticket_CreatedBy 
                FOREIGN KEY (CreatedBy) REFERENCES [Users](UserID)
            """)
            
            # Add foreign key for AssignedTo
            cursor.execute("""
                ALTER TABLE Ticket 
                ADD CONSTRAINT FK_Ticket_AssignedTo 
                FOREIGN KEY (AssignedTo) REFERENCES [Users](UserID)
            """)
            
            logger.info("Foreign key constraints added successfully")
        else:
            logger.info("Foreign key constraints already exist")
            
    except Exception as e:
        logger.warning(f"Could not add foreign key constraints: {e}")

def create_admin_user(cursor):
    """Create a default admin user if none exists"""
    logger.info("Checking for admin user...")
    
    cursor.execute("SELECT COUNT(*) FROM [Users] WHERE IsAdmin = 1")
    admin_count = cursor.fetchone()[0]
    
    if admin_count == 0:
        logger.info("Creating default admin user...")
        from werkzeug.security import generate_password_hash
        
        # Create admin user with default credentials
        admin_password = generate_password_hash('admin123')
        cursor.execute("""
            INSERT INTO [Users] (Name, Email, PasswordHash, OrganizationName, Position, 
                               PriorityLevel, IsActive, IsAdmin) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, 'System Administrator', 'admin@supportcenter.com', admin_password,
             'Support Center', 'Administrator', 'critical', 1, 1)
        
        logger.info("Default admin user created:")
        logger.info("Email: admin@supportcenter.com")
        logger.info("Password: admin123")
        logger.info("Please change the password after first login!")
    else:
        logger.info(f"Found {admin_count} admin user(s)")

def main():
    """Main migration function"""
    logger.info("Starting database migration...")
    
    try:
        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Run migrations
        migrate_user_table(cursor)
        migrate_ticket_table(cursor)
        create_admin_user(cursor)
        
        # Commit changes
        conn.commit()
        logger.info("Database migration completed successfully!")
        
        # Close connection
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise

if __name__ == '__main__':
    main()
