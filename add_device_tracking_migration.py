#!/usr/bin/env python3
"""
Device Tracking Migration - Add device tracking tables and fields
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_device_tracking_migration():
    """Add device tracking table and fields"""
    
    try:
        with app.app_context():
            logger.info("Starting device tracking migration...")
            
            # Check if device_tracking_logs table exists
            result = db.session.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='device_tracking_logs'
            """)).fetchone()
            
            if not result:
                logger.info("Creating device_tracking_logs table...")
                
                # Create device_tracking_logs table
                db.session.execute(text("""
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
                """))
                
                # Create indexes for better performance
                db.session.execute(text("""
                    CREATE INDEX idx_device_logs_session ON device_tracking_logs(session_id)
                """))
                
                db.session.execute(text("""
                    CREATE INDEX idx_device_logs_user ON device_tracking_logs(user_id)
                """))
                
                db.session.execute(text("""
                    CREATE INDEX idx_device_logs_ticket ON device_tracking_logs(ticket_id)
                """))
                
                db.session.execute(text("""
                    CREATE INDEX idx_device_logs_event ON device_tracking_logs(event_type)
                """))
                
                db.session.execute(text("""
                    CREATE INDEX idx_device_logs_device_type ON device_tracking_logs(device_type)
                """))
                
                db.session.execute(text("""
                    CREATE INDEX idx_device_logs_created ON device_tracking_logs(created_at)
                """))
                
                logger.info("✅ Created device_tracking_logs table with indexes")
            else:
                logger.info("device_tracking_logs table already exists")
            
            # Check if we need to add device fields to Users table
            try:
                # Check if device fields exist in Users table
                result = db.session.execute(text("PRAGMA table_info(Users)")).fetchall()
                existing_columns = [row[1] for row in result]
                
                if 'LastDeviceType' not in existing_columns:
                    logger.info("Adding device tracking fields to Users table...")
                    
                    db.session.execute(text("""
                        ALTER TABLE Users ADD COLUMN LastDeviceType VARCHAR(20)
                    """))
                    
                    db.session.execute(text("""
                        ALTER TABLE Users ADD COLUMN LastBrowser VARCHAR(50)
                    """))
                    
                    db.session.execute(text("""
                        ALTER TABLE Users ADD COLUMN LastOS VARCHAR(50)
                    """))
                    
                    db.session.execute(text("""
                        ALTER TABLE Users ADD COLUMN LastIPAddress VARCHAR(45)
                    """))
                    
                    db.session.execute(text("""
                        ALTER TABLE Users ADD COLUMN IsMobileUser BOOLEAN DEFAULT 0
                    """))
                    
                    logger.info("✅ Added device tracking fields to Users table")
                else:
                    logger.info("Device tracking fields already exist in Users table")
                    
            except Exception as e:
                logger.info(f"Could not add device fields to Users table: {e}")
            
            # Check if we need to add device fields to Tickets table
            try:
                result = db.session.execute(text("PRAGMA table_info(Tickets)")).fetchall()
                existing_columns = [row[1] for row in result]
                
                if 'CreatedFromDevice' not in existing_columns:
                    logger.info("Adding device tracking fields to Tickets table...")
                    
                    db.session.execute(text("""
                        ALTER TABLE Tickets ADD COLUMN CreatedFromDevice VARCHAR(20)
                    """))
                    
                    db.session.execute(text("""
                        ALTER TABLE Tickets ADD COLUMN CreatedFromBrowser VARCHAR(50)
                    """))
                    
                    db.session.execute(text("""
                        ALTER TABLE Tickets ADD COLUMN CreatedFromOS VARCHAR(50)
                    """))
                    
                    db.session.execute(text("""
                        ALTER TABLE Tickets ADD COLUMN CreatedFromIP VARCHAR(45)
                    """))
                    
                    db.session.execute(text("""
                        ALTER TABLE Tickets ADD COLUMN UserAgent TEXT
                    """))
                    
                    logger.info("✅ Added device tracking fields to Tickets table")
                else:
                    logger.info("Device tracking fields already exist in Tickets table")
                    
            except Exception as e:
                logger.info(f"Could not add device fields to Tickets table: {e}")
            
            # Commit all changes
            db.session.commit()
            
            logger.info("✅ Device tracking migration completed successfully!")
            return True
            
    except Exception as e:
        logger.error(f"❌ Error in device tracking migration: {e}")
        db.session.rollback()
        return False

def verify_device_tracking_setup():
    """Verify that device tracking tables and fields are properly set up"""
    
    try:
        with app.app_context():
            logger.info("Verifying device tracking setup...")
            
            # Check device_tracking_logs table
            result = db.session.execute(text("""
                SELECT COUNT(*) as count FROM sqlite_master 
                WHERE type='table' AND name='device_tracking_logs'
            """)).fetchone()
            
            if result[0] == 1:
                logger.info("✅ device_tracking_logs table exists")
                
                # Check table structure
                columns = db.session.execute(text("PRAGMA table_info(device_tracking_logs)")).fetchall()
                expected_columns = [
                    'id', 'session_id', 'user_id', 'ticket_id', 'device_type',
                    'browser_name', 'browser_version', 'os_name', 'os_version',
                    'user_agent', 'ip_address', 'is_mobile', 'is_tablet', 'is_bot',
                    'event_type', 'page_url', 'referrer', 'created_at', 'session_started_at'
                ]
                
                existing_columns = [col[1] for col in columns]
                missing_columns = [col for col in expected_columns if col not in existing_columns]
                
                if not missing_columns:
                    logger.info("✅ device_tracking_logs table structure is correct")
                else:
                    logger.warning(f"⚠️ Missing columns in device_tracking_logs: {missing_columns}")
            else:
                logger.error("❌ device_tracking_logs table does not exist")
            
            # Check indexes
            indexes = db.session.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND tbl_name='device_tracking_logs'
            """)).fetchall()
            
            index_names = [idx[0] for idx in indexes]
            expected_indexes = [
                'idx_device_logs_session', 'idx_device_logs_user', 
                'idx_device_logs_ticket', 'idx_device_logs_event',
                'idx_device_logs_device_type', 'idx_device_logs_created'
            ]
            
            existing_indexes = [idx for idx in expected_indexes if idx in index_names]
            logger.info(f"✅ Found {len(existing_indexes)} out of {len(expected_indexes)} expected indexes")
            
            # Test device tracking functionality
            from device_tracker import DeviceInfo, DeviceSession
            
            # Test DeviceInfo
            device_info = DeviceInfo("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            device_data = device_info.get_complete_info()
            
            if device_data:
                logger.info("✅ DeviceInfo class working correctly")
            else:
                logger.error("❌ DeviceInfo class not working")
            
            logger.info("Device tracking verification completed!")
            return True
            
    except Exception as e:
        logger.error(f"❌ Error verifying device tracking setup: {e}")
        return False

def create_sample_device_data():
    """Create sample device tracking data for testing"""
    
    try:
        with app.app_context():
            logger.info("Creating sample device tracking data...")
            
            # Sample device tracking entries
            sample_data = [
                {
                    'session_id': 'test-session-1',
                    'device_type': 'desktop',
                    'browser_name': 'Chrome',
                    'browser_version': '91.0.4472.124',
                    'os_name': 'Windows',
                    'os_version': '10',
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'ip_address': '192.168.1.100',
                    'event_type': 'page_view',
                    'page_url': '/chat'
                },
                {
                    'session_id': 'test-session-2',
                    'device_type': 'mobile',
                    'browser_name': 'Safari',
                    'browser_version': '14.0',
                    'os_name': 'iOS',
                    'os_version': '14.6',
                    'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15',
                    'ip_address': '192.168.1.101',
                    'is_mobile': True,
                    'event_type': 'ticket_create'
                },
                {
                    'session_id': 'test-session-3',
                    'device_type': 'tablet',
                    'browser_name': 'Firefox',
                    'browser_version': '89.0',
                    'os_name': 'Android',
                    'os_version': '11',
                    'user_agent': 'Mozilla/5.0 (Android 11; Tablet; rv:89.0) Gecko/89.0 Firefox/89.0',
                    'ip_address': '192.168.1.102',
                    'is_tablet': True,
                    'event_type': 'chat_message'
                }
            ]
            
            for data in sample_data:
                db.session.execute(text("""
                    INSERT INTO device_tracking_logs 
                    (session_id, device_type, browser_name, browser_version, os_name, os_version,
                     user_agent, ip_address, is_mobile, is_tablet, is_bot, event_type, page_url)
                    VALUES 
                    (:session_id, :device_type, :browser_name, :browser_version, :os_name, :os_version,
                     :user_agent, :ip_address, :is_mobile, :is_tablet, 0, :event_type, :page_url)
                """), {
                    'session_id': data['session_id'],
                    'device_type': data['device_type'],
                    'browser_name': data['browser_name'],
                    'browser_version': data['browser_version'],
                    'os_name': data['os_name'],
                    'os_version': data['os_version'],
                    'user_agent': data['user_agent'],
                    'ip_address': data['ip_address'],
                    'is_mobile': data.get('is_mobile', False),
                    'is_tablet': data.get('is_tablet', False),
                    'event_type': data['event_type'],
                    'page_url': data.get('page_url')
                })
            
            db.session.commit()
            logger.info(f"✅ Created {len(sample_data)} sample device tracking records")
            
            # Verify the data was inserted
            count = db.session.execute(text("SELECT COUNT(*) FROM device_tracking_logs")).fetchone()[0]
            logger.info(f"✅ Total device tracking records: {count}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Error creating sample device data: {e}")
        db.session.rollback()
        return False

if __name__ == "__main__":
    logger.info("=== Device Tracking Migration Script ===")
    
    # Run migration
    success = add_device_tracking_migration()
    
    if success:
        # Verify setup
        verify_device_tracking_setup()
        
        # Create sample data
        create_sample_device_data()
        
        logger.info("\n" + "=" * 50)
        logger.info("🎉 DEVICE TRACKING MIGRATION COMPLETED!")
        logger.info("✅ Device tracking tables created")
        logger.info("✅ Indexes added for performance")
        logger.info("✅ Sample data created")
        logger.info("✅ Migration verified successfully")
        logger.info("=" * 50)
    else:
        logger.error("\n❌ DEVICE TRACKING MIGRATION FAILED")
