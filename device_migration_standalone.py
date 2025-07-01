#!/usr/bin/env python3
"""
Standalone Device Tracking Migration
Adds device tracking tables and fields without circular import issues
"""

import sqlite3
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_device_tracking_migration_standalone():
    """Add device tracking table and fields to SQLite database"""
    
    db_path = "chatbot.db"
    if not os.path.exists(db_path):
        logger.error(f"Database file {db_path} not found!")
        return False
    
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        logger.info("Starting device tracking migration...")
        
        # Check if device_tracking_logs table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='device_tracking_logs'
        """)
        
        if not cursor.fetchone():
            logger.info("Creating device_tracking_logs table...")
            
            # Create device_tracking_logs table
            cursor.execute("""
                CREATE TABLE device_tracking_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id VARCHAR(255) NOT NULL,
                    user_id INTEGER,
                    ticket_id INTEGER,
                    device_type VARCHAR(20),
                    browser_name VARCHAR(50),
                    browser_version VARCHAR(50),
                    os_name VARCHAR(50),
                    os_version VARCHAR(50),
                    user_agent TEXT,
                    ip_address VARCHAR(45),
                    is_mobile BOOLEAN DEFAULT 0,
                    is_tablet BOOLEAN DEFAULT 0,
                    is_bot BOOLEAN DEFAULT 0,
                    event_type VARCHAR(50) NOT NULL,
                    page_url VARCHAR(500),
                    referrer VARCHAR(500),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    session_started_at DATETIME,
                    FOREIGN KEY (user_id) REFERENCES Users(UserID),
                    FOREIGN KEY (ticket_id) REFERENCES Tickets(TicketID)
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX idx_device_logs_session ON device_tracking_logs(session_id)")
            cursor.execute("CREATE INDEX idx_device_logs_user ON device_tracking_logs(user_id)")
            cursor.execute("CREATE INDEX idx_device_logs_ticket ON device_tracking_logs(ticket_id)")
            cursor.execute("CREATE INDEX idx_device_logs_event ON device_tracking_logs(event_type)")
            cursor.execute("CREATE INDEX idx_device_logs_device_type ON device_tracking_logs(device_type)")
            cursor.execute("CREATE INDEX idx_device_logs_created ON device_tracking_logs(created_at)")
            
            logger.info("✅ Created device_tracking_logs table with indexes")
        else:
            logger.info("device_tracking_logs table already exists")
        
        # Check and add device fields to Users table
        try:
            cursor.execute("PRAGMA table_info(Users)")
            existing_columns = [row[1] for row in cursor.fetchall()]
            
            if 'LastDeviceType' not in existing_columns:
                logger.info("Adding device tracking fields to Users table...")
                
                cursor.execute("ALTER TABLE Users ADD COLUMN LastDeviceType VARCHAR(20)")
                cursor.execute("ALTER TABLE Users ADD COLUMN LastBrowser VARCHAR(50)")
                cursor.execute("ALTER TABLE Users ADD COLUMN LastOS VARCHAR(50)")
                cursor.execute("ALTER TABLE Users ADD COLUMN LastIPAddress VARCHAR(45)")
                cursor.execute("ALTER TABLE Users ADD COLUMN IsMobileUser BOOLEAN DEFAULT 0")
                
                logger.info("✅ Added device tracking fields to Users table")
            else:
                logger.info("Device tracking fields already exist in Users table")
                
        except Exception as e:
            logger.warning(f"Could not add device fields to Users table: {e}")
        
        # Check and add device fields to Tickets table
        try:
            cursor.execute("PRAGMA table_info(Tickets)")
            existing_columns = [row[1] for row in cursor.fetchall()]
            
            if 'CreatedFromDevice' not in existing_columns:
                logger.info("Adding device tracking fields to Tickets table...")
                
                cursor.execute("ALTER TABLE Tickets ADD COLUMN CreatedFromDevice VARCHAR(20)")
                cursor.execute("ALTER TABLE Tickets ADD COLUMN CreatedFromBrowser VARCHAR(50)")
                cursor.execute("ALTER TABLE Tickets ADD COLUMN CreatedFromOS VARCHAR(50)")
                cursor.execute("ALTER TABLE Tickets ADD COLUMN CreatedFromIP VARCHAR(45)")
                cursor.execute("ALTER TABLE Tickets ADD COLUMN UserAgent TEXT")
                
                logger.info("✅ Added device tracking fields to Tickets table")
            else:
                logger.info("Device tracking fields already exist in Tickets table")
                
        except Exception as e:
            logger.warning(f"Could not add device fields to Tickets table: {e}")
        
        # Commit all changes
        conn.commit()
        logger.info("✅ Device tracking migration completed successfully!")
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='device_tracking_logs'")
        logs_table_exists = cursor.fetchone()[0] > 0
        
        cursor.execute("PRAGMA table_info(Users)")
        user_columns = [row[1] for row in cursor.fetchall()]
        user_device_fields = [col for col in user_columns if col.startswith('Last') or col == 'IsMobileUser']
        
        cursor.execute("PRAGMA table_info(Tickets)")
        ticket_columns = [row[1] for row in cursor.fetchall()]
        ticket_device_fields = [col for col in ticket_columns if col.startswith('CreatedFrom') or col == 'UserAgent']
        
        print("\n📊 Migration Summary:")
        print(f"   device_tracking_logs table: {'✅ Exists' if logs_table_exists else '❌ Missing'}")
        print(f"   Users device fields: {len(user_device_fields)} fields ({', '.join(user_device_fields) if user_device_fields else 'None'})")
        print(f"   Tickets device fields: {len(ticket_device_fields)} fields ({', '.join(ticket_device_fields) if ticket_device_fields else 'None'})")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("🚀 Standalone Device Tracking Migration")
    print("=" * 40)
    
    if add_device_tracking_migration_standalone():
        print("\n✅ Migration completed successfully!")
        print("\n🔧 Next steps:")
        print("1. Modify create_ticket() function in app.py")
        print("2. Modify admin ticket view to show device info")
        print("3. Test device tracking integration")
    else:
        print("\n❌ Migration failed!")
        print("Check the error messages above.")
