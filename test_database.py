#!/usr/bin/env python3
"""
Simple test to create a basic ticket and test database functionality
"""

import pyodbc
import logging
from config import Config
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database():
    """Test basic database operations"""
    try:
        config = Config()
        conn = pyodbc.connect(config.SQLALCHEMY_DATABASE_URI)
        cursor = conn.cursor()
        
        # Create Categories table if it doesn't exist
        logger.info("Creating Categories table...")
        cursor.execute("""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Categories' AND type='U')
            CREATE TABLE Categories (
                CategoryID int IDENTITY(1,1) PRIMARY KEY,
                Name nvarchar(100) NOT NULL,
                Description nvarchar(500),
                CreatedAt datetime2 DEFAULT GETDATE()
            )
        """)
        
        # Create Tickets table if it doesn't exist
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
        
        conn.commit()
        logger.info("Tables created successfully!")
        
        # Insert a sample category
        cursor.execute("SELECT COUNT(*) FROM Categories")
        cat_count = cursor.fetchone()[0]
        
        if cat_count == 0:
            logger.info("Creating sample category...")
            cursor.execute("""
                INSERT INTO Categories (Name, Description) 
                VALUES (?, ?)
            """, 'Technical Support', 'General technical support requests')
            conn.commit()
            logger.info("Sample category created")
        
        # Get category ID
        cursor.execute("SELECT CategoryID FROM Categories WHERE Name = 'Technical Support'")
        category_id = cursor.fetchone()[0]
        
        # Insert some sample tickets
        sample_tickets = [
            ('Critical System Down', 'critical', 'TechCorp Inc', 'John Doe'),
            ('Password Reset Request', 'medium', 'ABC Company', 'Jane Smith'),
            ('Software Installation Help', 'low', 'XYZ Corp', 'Bob Wilson')
        ]
        
        for subject, priority, org, created_by in sample_tickets:
            # Check if ticket already exists
            cursor.execute("SELECT COUNT(*) FROM Tickets WHERE Subject = ?", subject)
            if cursor.fetchone()[0] == 0:
                logger.info(f"Creating ticket: {subject}")
                cursor.execute("""
                    INSERT INTO Tickets (CategoryID, Subject, Priority, OrganizationName, CreatedBy)
                    VALUES (?, ?, ?, ?, ?)
                """, category_id, subject, priority, org, created_by)
        
        conn.commit()
        
        # Verify tickets were created
        cursor.execute("SELECT COUNT(*) FROM Tickets")
        ticket_count = cursor.fetchone()[0]
        logger.info(f"Total tickets in database: {ticket_count}")
        
        # Show all tickets
        cursor.execute("""
            SELECT TicketID, Subject, Priority, OrganizationName, CreatedBy, Status
            FROM Tickets 
            ORDER BY 
                CASE Priority 
                    WHEN 'critical' THEN 4
                    WHEN 'high' THEN 3
                    WHEN 'medium' THEN 2
                    WHEN 'low' THEN 1
                    ELSE 2
                END DESC,
                CreatedAt DESC
        """)
        
        tickets = cursor.fetchall()
        logger.info("Current tickets:")
        for ticket in tickets:
            logger.info(f"  #{ticket[0]} - {ticket[1]} ({ticket[2]}) - {ticket[3]} - {ticket[5]}")
        
        cursor.close()
        conn.close()
        logger.info("Database test completed successfully!")
        
    except Exception as e:
        logger.error(f"Database test failed: {e}")

if __name__ == '__main__':
    test_database()
