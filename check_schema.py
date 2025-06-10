#!/usr/bin/env python3
"""
Check database schema and fix any issues
"""

import pyodbc
import logging
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_database_schema():
    """Check what tables and columns actually exist in the database"""
    try:
        config = Config()
        conn = pyodbc.connect(config.SQLALCHEMY_DATABASE_URI)
        cursor = conn.cursor()
        
        # Check what tables exist
        logger.info("Checking existing tables...")
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """)
        tables = cursor.fetchall()
        
        logger.info("Existing tables:")
        for table in tables:
            logger.info(f"  - {table[0]}")
        
        # Check Users table columns
        if any('Users' in str(table[0]) for table in tables):
            logger.info("\nUsers table columns:")
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'Users'
                ORDER BY ORDINAL_POSITION
            """)
            columns = cursor.fetchall()
            for col in columns:
                logger.info(f"  - {col[0]} ({col[1]}) - Nullable: {col[2]}, Default: {col[3]}")
        
        # Check Tickets table columns if it exists
        if any('Tickets' in str(table[0]) or 'Ticket' in str(table[0]) for table in tables):
            logger.info("\nTickets table columns:")
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME IN ('Tickets', 'Ticket')
                ORDER BY TABLE_NAME, ORDINAL_POSITION
            """)
            columns = cursor.fetchall()
            for col in columns:
                logger.info(f"  - {col[0]} ({col[1]}) - Nullable: {col[2]}, Default: {col[3]}")
        else:
            logger.info("\nNo Tickets table found!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Error checking database schema: {e}")

if __name__ == '__main__':
    check_database_schema()
