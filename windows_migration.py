#!/usr/bin/env python3
"""
Windows-Compatible MSSQL to Odoo Migration
Simple migration without Unix signals
"""

import pyodbc
import logging
from datetime import datetime
from config import Config
from odoo_service import OdooService
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WindowsMigrator:
    def __init__(self):
        self.config = Config()
        self.odoo_service = None
        self.mssql_conn = None
        self.stats = {'customers': 0, 'tickets': 0, 'errors': 0, 'skipped': 0}
    
    def connect(self):
        """Initialize connections"""
        try:
            logger.info("🔄 Connecting to Odoo...")
            self.odoo_service = OdooService(
                url=self.config.ODOO_URL,
                db=self.config.ODOO_DB,
                username=self.config.ODOO_USERNAME,
                password=self.config.ODOO_PASSWORD
            )
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
            
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def migrate_sample_users(self):
        """Migrate sample users to Odoo customers"""
        logger.info("🔄 Migrating sample users...")
        
        try:
            cursor = self.mssql_conn.cursor()
            
            # Get first 5 users with email
            cursor.execute("""
                SELECT TOP 5 UserID, Name, Email, OrganizationName, Phone
                FROM Users 
                WHERE Email IS NOT NULL AND Email != '' AND Email NOT LIKE '%test%'
                ORDER BY UserID
            """)
            
            users = cursor.fetchall()
            logger.info(f"Found {len(users)} users to migrate")
            
            user_mapping = {}
            
            for user in users:
                user_id, name, email, org, phone = user
                try:
                    logger.info(f"🔄 Creating customer: {name} ({email})")
                    
                    customer_id = self.odoo_service.create_customer(
                        name=name or "Unknown Customer",
                        email=email.strip(),
                        phone=phone,
                        comment=f"Migrated from MSSQL User ID: {user_id}\\nOrganization: {org or 'N/A'}"
                    )
                    
                    user_mapping[user_id] = customer_id
                    self.stats['customers'] += 1
                    logger.info(f"✅ Created customer ID: {customer_id}")
                    
                    time.sleep(0.5)  # Rate limiting
                    
                except Exception as e:
                    error_msg = str(e).lower()
                    if "already exists" in error_msg or "duplicate" in error_msg:
                        logger.info(f"⚠️ Customer already exists: {email}")
                        
                        # Try to find existing customer
                        try:
                            existing_customers = self.odoo_service.models.execute_kw(
                                self.odoo_service.db, self.odoo_service.uid, self.odoo_service.password,
                                'res.partner', 'search', [[('email', '=', email.strip())]]
                            )
                            if existing_customers:
                                user_mapping[user_id] = existing_customers[0]
                                self.stats['customers'] += 1
                                logger.info(f"✅ Found existing customer ID: {existing_customers[0]}")
                        except:
                            pass
                        
                        self.stats['skipped'] += 1
                    else:
                        logger.error(f"❌ Failed to create customer {user_id}: {e}")
                        self.stats['errors'] += 1
            
            return user_mapping
            
        except Exception as e:
            logger.error(f"❌ User migration failed: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def migrate_sample_tickets(self, user_mapping):
        """Migrate sample tickets"""
        if not user_mapping:
            logger.warning("⚠️ No users migrated, skipping tickets")
            return
        
        logger.info("🔄 Migrating sample tickets...")
        
        try:
            cursor = self.mssql_conn.cursor()
            
            # Get tickets from migrated users
            user_ids = list(user_mapping.keys())
            placeholders = ','.join(['?'] * len(user_ids))
            
            cursor.execute(f"""
                SELECT TOP 3 t.TicketID, t.UserID, t.Subject, t.Priority, t.Status,
                       t.OrganizationName, t.CreatedBy
                FROM Tickets t
                WHERE t.UserID IN ({placeholders})
                ORDER BY t.TicketID
            """, user_ids)
            
            tickets = cursor.fetchall()
            logger.info(f"Found {len(tickets)} tickets to migrate")
            
            for ticket in tickets:
                ticket_id, user_id, subject, priority, status, org, created_by = ticket
                try:
                    partner_id = user_mapping.get(user_id)
                    
                    # Get first message for description
                    cursor.execute("""
                        SELECT TOP 1 Content FROM Messages 
                        WHERE TicketID = ? AND IsAdminReply = 0 
                        ORDER BY CreatedAt
                    """, ticket_id)
                    
                    first_message = cursor.fetchone()
                    description = first_message[0] if first_message else subject
                    
                    logger.info(f"🔄 Creating ticket: {subject}")
                    
                    full_description = f"{description}\\n\\n--- Migration Info ---\\n"
                    full_description += f"Original Ticket ID: {ticket_id}\\n"
                    full_description += f"Status: {status}\\n"
                    full_description += f"Created By: {created_by or 'Unknown'}\\n"
                    full_description += f"Organization: {org or 'N/A'}"
                    
                    # Map priority
                    odoo_priority = '2' if priority in ['high', 'critical'] else '1'
                    
                    odoo_ticket_id = self.odoo_service.create_ticket(
                        name=subject or "Support Request",
                        description=full_description,
                        partner_id=partner_id,
                        priority=odoo_priority,
                        tag_ids=['migrated-from-mssql']
                    )
                    
                    self.stats['tickets'] += 1
                    logger.info(f"✅ Created ticket ID: {odoo_ticket_id}")
                    
                    # Update MSSQL with Odoo IDs
                    cursor.execute("""
                        UPDATE Tickets 
                        SET odoo_ticket_id = ?, odoo_customer_id = ?
                        WHERE TicketID = ?
                    """, odoo_ticket_id, partner_id, ticket_id)
                    
                    time.sleep(1)  # Rate limiting for tickets
                    
                except Exception as e:
                    logger.error(f"❌ Failed to create ticket {ticket_id}: {e}")
                    import traceback
                    traceback.print_exc()
                    self.stats['errors'] += 1
            
            # Commit MSSQL changes
            self.mssql_conn.commit()
            logger.info("✅ MSSQL records updated with Odoo IDs")
            
        except Exception as e:
            logger.error(f"❌ Ticket migration failed: {e}")
            import traceback
            traceback.print_exc()
    
    def run_sample_migration(self):
        """Run a sample migration"""
        logger.info("🚀 Starting Sample MSSQL to Odoo Migration")
        
        if not self.connect():
            logger.error("❌ Failed to connect. Aborting.")
            return False
        
        try:
            # Step 1: Migrate sample users
            user_mapping = self.migrate_sample_users()
            
            # Step 2: Migrate sample tickets
            self.migrate_sample_tickets(user_mapping)
            
            # Print summary
            logger.info("="*60)
            logger.info("📊 SAMPLE MIGRATION SUMMARY")
            logger.info("="*60)
            logger.info(f"👥 Customers migrated: {self.stats['customers']}")
            logger.info(f"🎫 Tickets migrated: {self.stats['tickets']}")
            logger.info(f"⚠️ Skipped (duplicates): {self.stats['skipped']}")
            logger.info(f"❌ Errors: {self.stats['errors']}")
            logger.info("="*60)
            
            if self.stats['customers'] > 0 or self.stats['tickets'] > 0:
                logger.info("🎉 Sample migration completed successfully!")
                logger.info("\\n📋 Next steps:")
                logger.info("1. ✅ Check your Odoo Helpdesk to verify tickets were created")
                logger.info("2. ✅ Test creating a new ticket via chatbot to ensure sync works")
                logger.info("3. If everything looks good, run full migration script")
                return True
            else:
                logger.error("❌ No data was migrated")
                return False
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            if self.mssql_conn:
                self.mssql_conn.close()

def main():
    migrator = WindowsMigrator()
    success = migrator.run_sample_migration()
    
    if success:
        print("\\n🎯 NEXT ACTION REQUIRED:")
        print("1. Go to your Odoo Helpdesk and verify the migrated tickets appear")
        print("2. Test creating a ticket via your chatbot to ensure integration works")
        print("3. Let me know if you see the tickets in Odoo!")
    else:
        print("\\n❌ Migration failed. Check the logs above for details.")

if __name__ == "__main__":
    main()
