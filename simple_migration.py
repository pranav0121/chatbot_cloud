#!/usr/bin/env python3
"""
Simple MSSQL to Odoo Migration with Timeout Handling
Focus on core migration with better error handling
"""

import pyodbc
import logging
from datetime import datetime
from config import Config
from odoo_service import OdooService
import time
import signal

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")

class SimpleMigrator:
    def __init__(self):
        self.config = Config()
        self.odoo_service = None
        self.mssql_conn = None
        self.stats = {'success': 0, 'errors': 0, 'skipped': 0}
    
    def connect(self):
        """Initialize connections with timeout"""
        try:
            logger.info("🔄 Connecting to Odoo...")
            # Set timeout for Odoo connection
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(30)  # 30 second timeout
            
            self.odoo_service = OdooService(
                url=self.config.ODOO_URL,
                db=self.config.ODOO_DB,
                username=self.config.ODOO_USERNAME,
                password=self.config.ODOO_PASSWORD
            )
            signal.alarm(0)  # Cancel timeout
            logger.info("✅ Odoo connected")
            
            # Connect to MSSQL
            logger.info("🔄 Connecting to MSSQL...")
            if self.config.DB_USE_WINDOWS_AUTH:
                conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.config.DB_SERVER};DATABASE={self.config.DB_DATABASE};Trusted_Connection=yes;"
            else:
                conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.config.DB_SERVER};DATABASE={self.config.DB_DATABASE};UID={self.config.DB_USERNAME};PWD={self.config.DB_PASSWORD};"
            
            self.mssql_conn = pyodbc.connect(conn_str)
            logger.info("✅ MSSQL connected")
            
            return True
            
        except TimeoutError:
            logger.error("❌ Odoo connection timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            return False
        finally:
            signal.alarm(0)  # Make sure to cancel any pending alarm
    
    def migrate_sample_data(self):
        """Migrate a small sample of data first"""
        logger.info("🔄 Starting sample data migration...")
        
        try:
            cursor = self.mssql_conn.cursor()
            
            # Get first 3 users with email
            cursor.execute("""
                SELECT TOP 3 UserID, Name, Email, OrganizationName
                FROM Users 
                WHERE Email IS NOT NULL AND Email != ''
                ORDER BY UserID
            """)
            
            users = cursor.fetchall()
            logger.info(f"Found {len(users)} sample users")
            
            user_mapping = {}
            
            # Migrate users
            for user in users:
                user_id, name, email, org = user
                try:
                    logger.info(f"🔄 Creating customer: {name} ({email})")
                    
                    # Set timeout for API call
                    signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(15)  # 15 second timeout for each API call
                    
                    customer_id = self.odoo_service.create_customer(
                        name=name or "Unknown",
                        email=email,
                        comment=f"Migrated from MSSQL ID: {user_id}, Org: {org or 'N/A'}"
                    )
                    
                    signal.alarm(0)  # Cancel timeout
                    
                    user_mapping[user_id] = customer_id
                    self.stats['success'] += 1
                    logger.info(f"✅ Created customer ID: {customer_id}")
                    
                    time.sleep(1)  # Rate limiting
                    
                except TimeoutError:
                    logger.error(f"❌ Timeout creating customer for user {user_id}")
                    self.stats['errors'] += 1
                except Exception as e:
                    if "already exists" in str(e).lower():
                        logger.info(f"⚠️ Customer already exists: {email}")
                        self.stats['skipped'] += 1
                    else:
                        logger.error(f"❌ Failed to create customer: {e}")
                        self.stats['errors'] += 1
                finally:
                    signal.alarm(0)
            
            # Get first 2 tickets from these users
            if user_mapping:
                user_ids = list(user_mapping.keys())
                cursor.execute(f"""
                    SELECT TOP 2 TicketID, UserID, Subject, Priority
                    FROM Tickets 
                    WHERE UserID IN ({','.join(['?'] * len(user_ids))})
                    ORDER BY TicketID
                """, user_ids)
                
                tickets = cursor.fetchall()
                logger.info(f"Found {len(tickets)} sample tickets")
                
                # Migrate tickets
                for ticket in tickets:
                    ticket_id, user_id, subject, priority = ticket
                    try:
                        partner_id = user_mapping.get(user_id)
                        
                        logger.info(f"🔄 Creating ticket: {subject}")
                        
                        # Set timeout for API call
                        signal.signal(signal.SIGALRM, timeout_handler)
                        signal.alarm(20)  # 20 second timeout for ticket creation
                        
                        odoo_ticket_id = self.odoo_service.create_ticket(
                            name=subject,
                            description=f"Migrated from MSSQL Ticket ID: {ticket_id}",
                            partner_id=partner_id,
                            priority='2' if priority == 'high' else '1'
                        )
                        
                        signal.alarm(0)  # Cancel timeout
                        
                        self.stats['success'] += 1
                        logger.info(f"✅ Created ticket ID: {odoo_ticket_id}")
                        
                        # Update MSSQL with Odoo IDs
                        cursor.execute("""
                            UPDATE Tickets 
                            SET odoo_ticket_id = ?, odoo_customer_id = ?
                            WHERE TicketID = ?
                        """, odoo_ticket_id, partner_id, ticket_id)
                        
                        time.sleep(2)  # Rate limiting for tickets
                        
                    except TimeoutError:
                        logger.error(f"❌ Timeout creating ticket {ticket_id}")
                        self.stats['errors'] += 1
                    except Exception as e:
                        logger.error(f"❌ Failed to create ticket: {e}")
                        self.stats['errors'] += 1
                    finally:
                        signal.alarm(0)
                
                # Commit MSSQL changes
                self.mssql_conn.commit()
            
            logger.info("="*50)
            logger.info("📊 SAMPLE MIGRATION SUMMARY")
            logger.info(f"✅ Successful: {self.stats['success']}")
            logger.info(f"⚠️ Skipped: {self.stats['skipped']}")
            logger.info(f"❌ Errors: {self.stats['errors']}")
            logger.info("="*50)
            
            return self.stats['success'] > 0
            
        except Exception as e:
            logger.error(f"❌ Sample migration failed: {e}")
            return False
        finally:
            signal.alarm(0)
    
    def run(self):
        """Run the sample migration"""
        logger.info("🚀 Starting Simple MSSQL to Odoo Migration")
        
        if not self.connect():
            logger.error("❌ Failed to connect. Aborting.")
            return False
        
        try:
            success = self.migrate_sample_data()
            
            if success:
                logger.info("🎉 Sample migration completed successfully!")
                logger.info("📋 Next steps:")
                logger.info("1. Check Odoo Helpdesk to verify tickets were created")
                logger.info("2. If sample looks good, run full migration")
                logger.info("3. Test chatbot ticket creation")
            else:
                logger.error("❌ Sample migration had issues")
            
            return success
            
        finally:
            if self.mssql_conn:
                self.mssql_conn.close()

def main():
    migrator = SimpleMigrator()
    migrator.run()

if __name__ == "__main__":
    main()
