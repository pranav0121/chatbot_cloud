#!/usr/bin/env python3
"""
Add Country Information tracking to Users and Tickets tables
- Adds Country field to Users table for user's location  
- Adds Country field to Tickets table for ticket origin tracking
- Does NOT modify any existing working code or logic
"""

import pyodbc
from config import Config
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_country_fields():
    """Add Country fields to Users and Tickets tables"""
    config = Config()
    
    try:
        # Connect to database
        if config.DB_USE_WINDOWS_AUTH:
            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config.DB_SERVER};DATABASE={config.DB_DATABASE};Trusted_Connection=yes;"
        else:
            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config.DB_SERVER};DATABASE={config.DB_DATABASE};UID={config.DB_USERNAME};PWD={config.DB_PASSWORD};"
        
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        logger.info("✅ Connected to MSSQL database")
        
        # Check if Country columns already exist
        logger.info("🔍 Checking for existing Country columns...")
        
        # Check Users table
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'Users' 
            AND COLUMN_NAME = 'Country'
        """)
        users_country_exists = len(cursor.fetchall()) > 0
        
        # Check Tickets table  
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'Tickets' 
            AND COLUMN_NAME = 'Country'
        """)
        tickets_country_exists = len(cursor.fetchall()) > 0
        
        logger.info(f"Users.Country exists: {users_country_exists}")
        logger.info(f"Tickets.Country exists: {tickets_country_exists}")
        
        # Add Country to Users table if it doesn't exist
        if not users_country_exists:
            logger.info("➕ Adding Country column to Users table...")
            cursor.execute("""
                ALTER TABLE Users 
                ADD Country NVARCHAR(100) NULL
            """)
            logger.info("✅ Country column added to Users table!")
            
            # Set default country for existing users (can be updated later)
            logger.info("📝 Setting default country for existing users...")
            cursor.execute("""
                UPDATE Users 
                SET Country = 'Unknown'
                WHERE Country IS NULL
            """)
            updated_users = cursor.rowcount
            logger.info(f"✅ Updated {updated_users} existing users with default country")
        else:
            logger.info("ℹ️  Country column already exists in Users table")
        
        # Add Country to Tickets table if it doesn't exist
        if not tickets_country_exists:
            logger.info("➕ Adding Country column to Tickets table...")
            cursor.execute("""
                ALTER TABLE Tickets 
                ADD Country NVARCHAR(100) NULL
            """)
            logger.info("✅ Country column added to Tickets table!")
            
            # Populate country for existing tickets from their users
            logger.info("📝 Populating country for existing tickets from user data...")
            cursor.execute("""
                UPDATE t 
                SET t.Country = COALESCE(u.Country, 'Unknown')
                FROM Tickets t
                LEFT JOIN Users u ON t.UserID = u.UserID
                WHERE t.Country IS NULL
            """)
            updated_tickets = cursor.rowcount
            logger.info(f"✅ Updated {updated_tickets} existing tickets with country information")
        else:
            logger.info("ℹ️  Country column already exists in Tickets table")
        
        # Commit changes
        conn.commit()
        logger.info("✅ Database migration completed successfully!")
        
        # Verify the changes
        logger.info("🔍 Verifying migration results...")
        
        # Check Users table structure
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'Users' 
            AND COLUMN_NAME = 'Country'
        """)
        users_result = cursor.fetchone()
        if users_result:
            logger.info(f"✅ Users.Country: {users_result[1]} ({users_result[2]})")
        
        # Check Tickets table structure
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'Tickets' 
            AND COLUMN_NAME = 'Country'
        """)
        tickets_result = cursor.fetchone()
        if tickets_result:
            logger.info(f"✅ Tickets.Country: {tickets_result[1]} ({tickets_result[2]})")
        
        # Show sample data
        cursor.execute("SELECT COUNT(*) FROM Users WHERE Country IS NOT NULL")
        users_with_country = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Tickets WHERE Country IS NOT NULL") 
        tickets_with_country = cursor.fetchone()[0]
        
        logger.info(f"📊 Users with country data: {users_with_country}")
        logger.info(f"📊 Tickets with country data: {tickets_with_country}")
        
    except Exception as e:
        logger.error(f"❌ Error during migration: {e}")
        if 'conn' in locals():
            conn.rollback()
        raise
        
    finally:
        if 'conn' in locals():
            conn.close()
            logger.info("🔐 Database connection closed")

if __name__ == "__main__":
    logger.info("🌍 Starting Country Information Migration...")
    logger.info("=" * 60)
    add_country_fields()
    logger.info("=" * 60)
    logger.info("🎉 Country Information Migration Completed!")
