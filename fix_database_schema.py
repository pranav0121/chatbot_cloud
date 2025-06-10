#!/usr/bin/env python3
"""
Fix database schema to match the model definition
"""

import pyodbc
import logging
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_database_schema():
    """Fix the database schema to match the model definitions"""
    try:
        config = Config()
        conn = pyodbc.connect(config.SQLALCHEMY_DATABASE_URI)
        cursor = conn.cursor()
        
        logger.info("Checking and fixing database schema...")
        
        # Check what columns exist in Tickets table
        logger.info("Checking current Tickets table structure...")
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'Tickets'
            ORDER BY ORDINAL_POSITION
        """)
        existing_columns = [row[0] for row in cursor.fetchall()]
        logger.info(f"Existing Tickets columns: {existing_columns}")
        
        # Define required columns for Tickets table
        required_columns = {
            'Priority': 'nvarchar(20) DEFAULT \'medium\'',
            'OrganizationName': 'nvarchar(200)',
            'CreatedBy': 'nvarchar(100)',
            'AssignedTo': 'int',
            'UpdatedAt': 'datetime2 DEFAULT GETDATE()'
        }
        
        # Add missing columns
        for column_name, column_def in required_columns.items():
            if column_name not in existing_columns:
                logger.info(f"Adding missing column: {column_name}")
                try:
                    cursor.execute(f"ALTER TABLE Tickets ADD {column_name} {column_def}")
                    logger.info(f"Successfully added column: {column_name}")
                except Exception as e:
                    logger.error(f"Error adding column {column_name}: {e}")
        
        # Check Users table
        logger.info("Checking current Users table structure...")
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'Users'
            ORDER BY ORDINAL_POSITION
        """)
        user_columns = [row[0] for row in cursor.fetchall()]
        logger.info(f"Existing Users columns: {user_columns}")
        
        # Define required columns for Users table
        required_user_columns = {
            'OrganizationName': 'nvarchar(200)',
            'Position': 'nvarchar(100)',
            'PriorityLevel': 'nvarchar(20) DEFAULT \'medium\'',
            'Phone': 'nvarchar(20)',
            'Department': 'nvarchar(100)',
            'PreferredLanguage': 'nvarchar(10) DEFAULT \'en\'',
            'IsActive': 'bit DEFAULT 1',
            'IsAdmin': 'bit DEFAULT 0',
            'LastLogin': 'datetime2'
        }
        
        # Add missing columns to Users table
        for column_name, column_def in required_user_columns.items():
            if column_name not in user_columns:
                logger.info(f"Adding missing column to Users: {column_name}")
                try:
                    cursor.execute(f"ALTER TABLE Users ADD {column_name} {column_def}")
                    logger.info(f"Successfully added column to Users: {column_name}")
                except Exception as e:
                    logger.error(f"Error adding column {column_name} to Users: {e}")
        
        # Check Categories table
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = 'Categories'
        """)
        categories_exists = cursor.fetchone()[0] > 0
        
        if not categories_exists:
            logger.info("Creating Categories table...")
            cursor.execute("""
                CREATE TABLE Categories (
                    CategoryID int IDENTITY(1,1) PRIMARY KEY,
                    Name nvarchar(100) NOT NULL,
                    Team nvarchar(50),
                    CreatedAt datetime2 DEFAULT GETDATE()
                )
            """)
            logger.info("Categories table created")
        
        # Check if Categories table has the Team column
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'Categories'
        """)
        category_columns = [row[0] for row in cursor.fetchall()]
        
        if 'Team' not in category_columns:
            logger.info("Adding Team column to Categories...")
            cursor.execute("ALTER TABLE Categories ADD Team nvarchar(50)")
        
        if 'Description' not in category_columns:
            logger.info("Adding Description column to Categories...")
            cursor.execute("ALTER TABLE Categories ADD Description nvarchar(500)")
        
        # Commit all changes
        conn.commit()
        logger.info("Database schema fix completed successfully!")
        
        # Verify final structure
        logger.info("Final verification...")
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'Tickets'
            ORDER BY ORDINAL_POSITION
        """)
        final_tickets_columns = [row[0] for row in cursor.fetchall()]
        logger.info(f"Final Tickets columns: {final_tickets_columns}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Error fixing database schema: {e}")

if __name__ == '__main__':
    fix_database_schema()
