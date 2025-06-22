#!/usr/bin/env python3
"""
Add Odoo Integration fields to Tickets table
"""

import pyodbc
from config import Config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_odoo_fields():
    """Add Odoo integration fields to the Tickets table"""
    config = Config()
    
    try:
        # Connect to database using proper config attributes
        if config.DB_USE_WINDOWS_AUTH:
            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config.DB_SERVER};DATABASE={config.DB_DATABASE};Trusted_Connection=yes;"
        else:
            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config.DB_SERVER};DATABASE={config.DB_DATABASE};UID={config.DB_USERNAME};PWD={config.DB_PASSWORD};"
        
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Check if columns already exist
        check_columns_sql = """
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = 'Tickets' 
        AND COLUMN_NAME IN ('odoo_customer_id', 'odoo_ticket_id')
        """
        
        cursor.execute(check_columns_sql)
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        # Add odoo_customer_id if it doesn't exist
        if 'odoo_customer_id' not in existing_columns:
            logger.info("Adding odoo_customer_id column...")
            cursor.execute("ALTER TABLE Tickets ADD odoo_customer_id INT NULL")
            logger.info("✅ Added odoo_customer_id column")
        else:
            logger.info("⚠️ odoo_customer_id column already exists")
        
        # Add odoo_ticket_id if it doesn't exist
        if 'odoo_ticket_id' not in existing_columns:
            logger.info("Adding odoo_ticket_id column...")
            cursor.execute("ALTER TABLE Tickets ADD odoo_ticket_id INT NULL")
            logger.info("✅ Added odoo_ticket_id column")
        else:
            logger.info("⚠️ odoo_ticket_id column already exists")
        
        # Commit changes
        conn.commit()
        logger.info("✅ Database migration completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Error during migration: {e}")
        if 'conn' in locals():
            conn.rollback()
        raise
        
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    logger.info("Starting Odoo integration database migration...")
    add_odoo_fields()
    logger.info("Migration completed!")
