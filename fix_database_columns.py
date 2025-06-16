#!/usr/bin/env python3
"""
Fix database columns for SLA monitoring
"""

from sqlalchemy import text
from app import app, db

def fix_database_columns():
    with app.app_context():
        try:
            print('Starting database column fix...')
            
            # Check current columns
            result = db.session.execute(text("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'sla_logs'"))
            existing_columns = [row[0] for row in result]
            print(f'Existing columns: {existing_columns}')
            
            # Check if status column exists
            if 'status' not in existing_columns:
                print('Adding status column...')
                db.session.execute(text("ALTER TABLE sla_logs ADD status nvarchar(20) DEFAULT 'on_time'"))
            else:
                print('Status column already exists')
            
            # Check if logged_at column exists
            if 'logged_at' not in existing_columns:
                print('Adding logged_at column...')
                db.session.execute(text("ALTER TABLE sla_logs ADD logged_at datetime2 DEFAULT GETDATE()"))
            else:
                print('Logged_at column already exists')
            
            # Update existing records to ensure no NULL values
            print('Updating existing records...')
            db.session.execute(text("UPDATE sla_logs SET status = 'on_time' WHERE status IS NULL"))
            db.session.execute(text("UPDATE sla_logs SET logged_at = COALESCE(created_at, GETDATE()) WHERE logged_at IS NULL"))
            db.session.execute(text("UPDATE sla_logs SET created_at = GETDATE() WHERE created_at IS NULL"))
            
            db.session.commit()
            print('Successfully fixed database columns!')
            
        except Exception as e:
            print(f'Error: {e}')
            import traceback
            traceback.print_exc()
            db.session.rollback()

if __name__ == "__main__":
    fix_database_columns()
