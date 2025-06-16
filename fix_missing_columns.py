#!/usr/bin/env python3
"""
Fix Missing Database Columns
Adds missing columns to existing tables
"""

import logging
from sqlalchemy import text
from app import app, db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_missing_columns():
    """Add missing columns to existing tables"""
    
    with app.app_context():
        try:
            # Add missing columns to sla_logs table
            logger.info("Adding missing columns to sla_logs table...")
            
            # Check if status column exists
            result = db.session.execute(text("""
                SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'sla_logs' AND COLUMN_NAME = 'status'
            """))
            if not list(result):
                logger.info("Adding 'status' column to sla_logs...")
                db.session.execute(text("""
                    ALTER TABLE sla_logs ADD status nvarchar(20) DEFAULT 'on_time'
                """))
            
            # Check if logged_at column exists
            result = db.session.execute(text("""
                SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'sla_logs' AND COLUMN_NAME = 'logged_at'
            """))
            if not list(result):
                logger.info("Adding 'logged_at' column to sla_logs...")
                db.session.execute(text("""
                    ALTER TABLE sla_logs ADD logged_at datetime2 DEFAULT GETDATE()
                """))
            
            # Add missing columns to ticket_status_logs table
            logger.info("Adding missing columns to ticket_status_logs table...")
            
            # Check if changed_by column exists
            result = db.session.execute(text("""
                SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'ticket_status_logs' AND COLUMN_NAME = 'changed_by'
            """))
            if not list(result):
                logger.info("Adding 'changed_by' column to ticket_status_logs...")
                db.session.execute(text("""
                    ALTER TABLE ticket_status_logs ADD changed_by nvarchar(255)
                """))
            
            # Check if changed_at column exists
            result = db.session.execute(text("""
                SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'ticket_status_logs' AND COLUMN_NAME = 'changed_at'
            """))
            if not list(result):
                logger.info("Adding 'changed_at' column to ticket_status_logs...")
                db.session.execute(text("""
                    ALTER TABLE ticket_status_logs ADD changed_at datetime2 DEFAULT GETDATE()
                """))
            
            # Check if sla_status column exists
            result = db.session.execute(text("""
                SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'ticket_status_logs' AND COLUMN_NAME = 'sla_status'
            """))
            if not list(result):
                logger.info("Adding 'sla_status' column to ticket_status_logs...")
                db.session.execute(text("""
                    ALTER TABLE ticket_status_logs ADD sla_status nvarchar(20) DEFAULT 'on_time'
                """))
            
            # Check if notes column exists
            result = db.session.execute(text("""
                SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'ticket_status_logs' AND COLUMN_NAME = 'notes'
            """))
            if not list(result):
                logger.info("Adding 'notes' column to ticket_status_logs...")
                db.session.execute(text("""
                    ALTER TABLE ticket_status_logs ADD notes ntext
                """))
            
            # Add missing columns to bot_interactions table
            logger.info("Adding missing columns to bot_interactions table...")
            
            # Check if success column exists
            result = db.session.execute(text("""
                SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'bot_interactions' AND COLUMN_NAME = 'success'
            """))
            if not list(result):
                logger.info("Adding 'success' column to bot_interactions...")
                db.session.execute(text("""
                    ALTER TABLE bot_interactions ADD success bit DEFAULT 1
                """))
            
            # Check if response_time column exists
            result = db.session.execute(text("""
                SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'bot_interactions' AND COLUMN_NAME = 'response_time'
            """))
            if not list(result):
                logger.info("Adding 'response_time' column to bot_interactions...")
                db.session.execute(text("""
                    ALTER TABLE bot_interactions ADD response_time float
                """))
            
            # Update existing records with default values
            logger.info("Updating existing records with default values...")
            
            # Update sla_logs records
            db.session.execute(text("""
                UPDATE sla_logs 
                SET status = 'on_time', logged_at = created_at 
                WHERE status IS NULL OR logged_at IS NULL
            """))
            
            # Update ticket_status_logs records
            db.session.execute(text("""
                UPDATE ticket_status_logs 
                SET changed_at = created_at, sla_status = 'on_time'
                WHERE changed_at IS NULL OR sla_status IS NULL
            """))
            
            # Update bot_interactions records
            db.session.execute(text("""
                UPDATE bot_interactions 
                SET success = 1
                WHERE success IS NULL
            """))
            
            db.session.commit()
            logger.info("All missing columns added successfully!")
            
        except Exception as e:
            logger.error(f"Error adding missing columns: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    fix_missing_columns()
