#!/usr/bin/env python3
"""
Simple script to create all database tables
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Ticket, Category, Message, CommonQuery
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables():
    """Create all database tables"""
    try:
        with app.app_context():
            logger.info("Creating all database tables...")
            db.create_all()
            logger.info("All tables created successfully!")
            
            # Verify tables were created
            from sqlalchemy import text
            result = db.session.execute(text("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """))
            
            tables = result.fetchall()
            logger.info("Created tables:")
            for table in tables:
                logger.info(f"  - {table[0]}")
                
    except Exception as e:
        logger.error(f"Error creating tables: {e}")

if __name__ == '__main__':
    create_tables()
