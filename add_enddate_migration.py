#!/usr/bin/env python3
"""
Database migration script to add EndDate column to Tickets table.
This column tracks when tickets are actually resolved or closed.
"""

import pyodbc
import logging
from datetime import datetime
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_enddate_column():
    """Add EndDate column to the Tickets table"""
    try:
        config = Config()
        
        # Connect to database
        if config.DB_USE_WINDOWS_AUTH:
            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config.DB_SERVER};DATABASE={config.DB_DATABASE};Trusted_Connection=yes;"
        else:
            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config.DB_SERVER};DATABASE={config.DB_DATABASE};UID={config.DB_USERNAME};PWD={config.DB_PASSWORD};"
        
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        logger.info("🔍 Checking if EndDate column already exists...")
        
        # Check if EndDate column already exists
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'Tickets' AND COLUMN_NAME = 'EndDate'
        """)
        
        existing_column = cursor.fetchone()
        
        if existing_column:
            logger.info("✅ EndDate column already exists in Tickets table")
        else:
            logger.info("➕ Adding EndDate column to Tickets table...")
            
            # Add the EndDate column
            cursor.execute("""
                ALTER TABLE Tickets 
                ADD EndDate DATETIME2 NULL
            """)
            
            logger.info("✅ EndDate column added successfully!")
            
            # Optionally populate EndDate for already resolved/closed tickets
            # using their UpdatedAt timestamp as an approximation
            logger.info("📝 Updating existing resolved/closed tickets with EndDate...")
            
            cursor.execute("""
                UPDATE Tickets 
                SET EndDate = UpdatedAt 
                WHERE Status IN ('resolved', 'closed') 
                AND EndDate IS NULL
            """)
            
            updated_rows = cursor.rowcount
            logger.info(f"✅ Updated {updated_rows} existing tickets with EndDate")
        
        # Commit changes
        conn.commit()
        
        # Verify the column was added
        logger.info("🔍 Verifying Tickets table structure...")
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'Tickets' 
            ORDER BY ORDINAL_POSITION
        """)
        
        columns = cursor.fetchall()
        logger.info("Current Tickets table columns:")
        for col in columns:
            logger.info(f"  - {col[0]} ({col[1]}) - Nullable: {col[2]}")
        
        cursor.close()
        conn.close()
        
        logger.info("🎉 EndDate column migration completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error adding EndDate column: {e}")
        try:
            conn.rollback()
            conn.close()
        except:
            pass
        return False

if __name__ == "__main__":
    logger.info("=== ENDDATE COLUMN MIGRATION ===")
    logger.info("Adding EndDate column to track ticket closure timestamps")
    logger.info("=" * 50)
    
    success = add_enddate_column()
    
    if success:
        logger.info("🎉 Migration completed successfully!")
        logger.info("The EndDate column will now track when tickets are resolved or closed.")
    else:
        logger.error("❌ Migration failed!")
