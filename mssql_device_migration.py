#!/usr/bin/env python3
"""
MSSQL Device Tracking Migration
Adds device tracking fields to existing MSSQL tables
"""

import logging
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_mssql_device_migration():
    """Add device tracking fields to MSSQL tables"""
    
    try:
        # Create database connection
        config = Config()
        engine = create_engine(config.SQLALCHEMY_DATABASE_URI, echo=False)
        
        logger.info("Connected to MSSQL database")
        logger.info("Starting device tracking migration...")
        
        with engine.connect() as conn:
            # Check existing columns in Users table
            inspector = inspect(engine)
            
            try:
                users_columns = [col['name'] for col in inspector.get_columns('Users')]
                logger.info(f"Users table exists with {len(users_columns)} columns")
                
                # Add device fields to Users table if they don't exist
                device_fields_users = [
                    "device_type VARCHAR(20)",
                    "operating_system VARCHAR(50)", 
                    "browser VARCHAR(50)",
                    "browser_version VARCHAR(50)",
                    "os_version VARCHAR(50)",
                    "device_brand VARCHAR(50)",
                    "device_model VARCHAR(50)",
                    "device_fingerprint VARCHAR(255)",
                    "user_agent TEXT",
                    "ip_address VARCHAR(45)"
                ]
                
                added_users = 0
                for field in device_fields_users:
                    field_name = field.split()[0]
                    if field_name not in users_columns:
                        try:
                            alter_sql = f"ALTER TABLE Users ADD {field}"
                            conn.execute(text(alter_sql))
                            logger.info(f"Added {field_name} to Users table")
                            added_users += 1
                        except Exception as e:
                            logger.warning(f"Could not add {field_name} to Users: {e}")
                
                logger.info(f"Added {added_users} device fields to Users table")
                            
            except Exception as e:
                logger.warning(f"Could not modify Users table: {e}")
            
            try:
                tickets_columns = [col['name'] for col in inspector.get_columns('Tickets')]
                logger.info(f"Tickets table exists with {len(tickets_columns)} columns")
                
                # Add device fields to Tickets table if they don't exist
                device_fields_tickets = [
                    "device_type VARCHAR(20)",
                    "operating_system VARCHAR(50)",
                    "browser VARCHAR(50)", 
                    "browser_version VARCHAR(50)",
                    "os_version VARCHAR(50)",
                    "device_brand VARCHAR(50)",
                    "device_model VARCHAR(50)",
                    "device_fingerprint VARCHAR(255)",
                    "user_agent TEXT",
                    "ip_address VARCHAR(45)"
                ]
                
                added_tickets = 0
                for field in device_fields_tickets:
                    field_name = field.split()[0]
                    if field_name not in tickets_columns:
                        try:
                            alter_sql = f"ALTER TABLE Tickets ADD {field}"
                            conn.execute(text(alter_sql))
                            logger.info(f"Added {field_name} to Tickets table")
                            added_tickets += 1
                        except Exception as e:
                            logger.warning(f"Could not add {field_name} to Tickets: {e}")
                
                logger.info(f"Added {added_tickets} device fields to Tickets table")
                            
            except Exception as e:
                logger.warning(f"Could not modify Tickets table: {e}")
            
            # Commit changes (autocommit is enabled by default)
            
        logger.info("✅ MSSQL device tracking migration completed!")
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        return False
    except Exception as e:
        logger.error(f"Migration error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 MSSQL Device Tracking Migration")
    print("=" * 40)
    
    if run_mssql_device_migration():
        print("\n✅ Migration completed successfully!")
        print("\n🔧 Next steps:")
        print("1. Restart the Flask application")
        print("2. Test device tracking in tickets")
        print("3. Verify admin UI shows device info")
    else:
        print("\n❌ Migration failed!")
        print("Please check the logs for details")
