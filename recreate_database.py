#!/usr/bin/env python3
"""
Complete database recreation with proper schema
"""

import pyodbc
import logging
from config import Config
from werkzeug.security import generate_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def recreate_database():
    """Recreate the database with the correct schema"""
    try:
        config = Config()
        conn = pyodbc.connect(config.SQLALCHEMY_DATABASE_URI)
        cursor = conn.cursor()
        
        logger.info("Recreating database with proper schema...")
        
        # Drop existing tables in correct order (handle foreign keys)
        tables_to_drop = ['Messages', 'Tickets', 'Users', 'Categories']
        for table in tables_to_drop:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
                logger.info(f"Dropped table: {table}")
            except Exception as e:
                logger.warning(f"Could not drop {table}: {e}")
        
        # Create Users table with all required columns
        logger.info("Creating Users table...")
        cursor.execute("""
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
        
        # Create Categories table
        logger.info("Creating Categories table...")
        cursor.execute("""
            CREATE TABLE Categories (
                CategoryID int IDENTITY(1,1) PRIMARY KEY,
                Name nvarchar(100) NOT NULL,
                Team nvarchar(50),
                Description nvarchar(500),
                CreatedAt datetime2 DEFAULT GETDATE()
            )
        """)
        
        # Create Tickets table with all required columns
        logger.info("Creating Tickets table...")
        cursor.execute("""
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
            CREATE TABLE Messages (
                MessageID int IDENTITY(1,1) PRIMARY KEY,
                TicketID int,
                SenderID int,
                Content ntext NOT NULL,
                IsAdminReply bit DEFAULT 0,
                CreatedAt datetime2 DEFAULT GETDATE(),
                FOREIGN KEY (TicketID) REFERENCES Tickets(TicketID),
                FOREIGN KEY (SenderID) REFERENCES Users(UserID)
            )
        """)
        
        conn.commit()
        logger.info("All tables created successfully!")
        
        # Insert default data
        logger.info("Inserting default data...")
        
        # Create admin user
        admin_password = generate_password_hash('admin123')
        cursor.execute("""
            INSERT INTO Users (Name, Email, PasswordHash, OrganizationName, Position, 
                              PriorityLevel, IsActive, IsAdmin) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, 'System Administrator', 'admin@supportcenter.com', admin_password,
             'Support Center', 'Administrator', 'critical', 1, 1)
        
        # Create categories
        categories = [
            ('Technical Support', 'Tech', 'Technical issues and troubleshooting'),
            ('Account Management', 'Account', 'Account-related requests'),
            ('Billing & Payment', 'Billing', 'Billing and payment issues'),
            ('General Inquiries', 'General', 'General questions and support')
        ]
        
        for name, team, desc in categories:
            cursor.execute("""
                INSERT INTO Categories (Name, Team, Description) 
                VALUES (?, ?, ?)
            """, name, team, desc)
        
        # Create test users
        test_users = [
            ('John Doe', 'john.doe@techcorp.com', 'TechCorp Inc', 'Developer', 'high'),
            ('Jane Smith', 'jane.smith@abccompany.com', 'ABC Company', 'Manager', 'medium'),
            ('Bob Johnson', 'bob.johnson@xyzsolutions.com', 'XYZ Solutions', 'IT Specialist', 'medium')
        ]
        
        for name, email, org, position, priority in test_users:
            password = generate_password_hash('password123')
            cursor.execute("""
                INSERT INTO Users (Name, Email, PasswordHash, OrganizationName, Position, 
                                  PriorityLevel, IsActive, IsAdmin) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, name, email, password, org, position, priority, 1, 0)
        
        # Create test tickets
        test_tickets = [
            (2, 1, 'Critical System Outage', 'critical', 'open', 'TechCorp Inc', 'John Doe'),
            (3, 1, 'Password Reset Request', 'high', 'in_progress', 'ABC Company', 'Jane Smith'),
            (4, 2, 'Account Upgrade Needed', 'medium', 'open', 'XYZ Solutions', 'Bob Johnson'),
            (2, 3, 'Billing Question', 'low', 'resolved', 'TechCorp Inc', 'John Doe')
        ]
        
        for user_id, cat_id, subject, priority, status, org, created_by in test_tickets:
            cursor.execute("""
                INSERT INTO Tickets (UserID, CategoryID, Subject, Priority, Status, 
                                   OrganizationName, CreatedBy) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, user_id, cat_id, subject, priority, status, org, created_by)
        
        conn.commit()
        logger.info("Default data inserted successfully!")
        
        # Verify the setup
        cursor.execute("SELECT COUNT(*) FROM Users")
        user_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Tickets")
        ticket_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM Categories")
        category_count = cursor.fetchone()[0]
        
        logger.info("=== DATABASE RECREATION COMPLETE ===")
        logger.info(f"Users: {user_count}")
        logger.info(f"Tickets: {ticket_count}")
        logger.info(f"Categories: {category_count}")
        logger.info("")
        logger.info("Admin Login:")
        logger.info("  Email: admin@supportcenter.com")
        logger.info("  Password: admin123")
        logger.info("")
        logger.info("Database is ready!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Error recreating database: {e}")

if __name__ == '__main__':
    recreate_database()
