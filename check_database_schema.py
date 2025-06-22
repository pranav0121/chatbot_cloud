#!/usr/bin/env python3
"""
Check current database schema and tables
"""

import pyodbc
from config import Config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_database_schema():
    """Check existing tables and their structure"""
    config = Config()
    
    try:
        # Build connection string manually
        if config.DB_USE_WINDOWS_AUTH:
            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config.DB_SERVER};DATABASE={config.DB_DATABASE};Trusted_Connection=yes;"
        else:
            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config.DB_SERVER};DATABASE={config.DB_DATABASE};UID={config.DB_USERNAME};PWD={config.DB_PASSWORD};"
        
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        tables = [row[0] for row in cursor.fetchall()]
        
        logger.info(f"Found {len(tables)} tables:")
        
        for table in tables:
            logger.info(f"\n📋 Table: {table}")
            
            # Get columns for each table
            cursor.execute("""
                SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = ?
                ORDER BY ORDINAL_POSITION
            """, table)
            
            columns = cursor.fetchall()
            for col in columns:
                logger.info(f"  - {col[0]} ({col[1]}) {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
            
            # Get row count
            try:
                cursor.execute(f"SELECT COUNT(*) FROM [{table}]")
                count = cursor.fetchone()[0]
                logger.info(f"  📊 Records: {count}")
            except:
                logger.info(f"  📊 Records: Unable to count")
        
    except Exception as e:
        logger.error(f"❌ Error checking schema: {e}")
        
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_database_schema()
