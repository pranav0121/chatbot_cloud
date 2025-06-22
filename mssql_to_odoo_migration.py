#!/usr/bin/env python3
"""
Complete MSSQL to Odoo Migration Script
This script migrates all relevant data from MSSQL database to Odoo Online
"""

import pyodbc
import logging
from datetime import datetime, timezone
from config import Config
from odoo_service import OdooService
import json
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MSSQLToOdooMigrator:
    def __init__(self):
        self.config = Config()
        self.odoo_service = None
        self.mssql_conn = None
        
        # Migration mapping statistics
        self.migration_stats = {
            'customers_migrated': 0,
            'categories_migrated': 0,
            'tickets_migrated': 0,
            'messages_migrated': 0,
            'errors': []
        }
        
        # ID mapping for reference
        self.id_mapping = {
            'users': {},      # mssql_user_id -> odoo_partner_id
            'categories': {}, # mssql_category_id -> odoo_team_id 
            'tickets': {}     # mssql_ticket_id -> odoo_ticket_id
        }
    
    def initialize_connections(self):
        """Initialize both MSSQL and Odoo connections"""
        try:
            # Initialize Odoo service
            self.odoo_service = OdooService(
                url=self.config.ODOO_URL,
                db=self.config.ODOO_DB,
                username=self.config.ODOO_USERNAME,
                password=self.config.ODOO_PASSWORD
            )
            logger.info("✅ Odoo connection established")
            
            # Initialize MSSQL connection
            if self.config.DB_USE_WINDOWS_AUTH:
                conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.config.DB_SERVER};DATABASE={self.config.DB_DATABASE};Trusted_Connection=yes;"
            else:
                conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.config.DB_SERVER};DATABASE={self.config.DB_DATABASE};UID={self.config.DB_USERNAME};PWD={self.config.DB_PASSWORD};"
            
            self.mssql_conn = pyodbc.connect(conn_str)
            logger.info("✅ MSSQL connection established")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize connections: {e}")
            return False
    
    def migrate_users_to_customers(self):
        """Migrate Users table to Odoo res.partner (customers)"""
        logger.info("🔄 Starting Users -> Customers migration...")
        
        try:
            cursor = self.mssql_conn.cursor()
            
            # Get all active users
            cursor.execute("""
                SELECT UserID, Name, Email, OrganizationName, Position, 
                       Phone, Department, CreatedAt, PriorityLevel
                FROM Users 
                WHERE IsActive = 1 OR IsActive IS NULL
                ORDER BY UserID
            """)
            
            users = cursor.fetchall()
            logger.info(f"Found {len(users)} users to migrate")
            
            for user in users:
                try:
                    user_id, name, email, org_name, position, phone, dept, created_at, priority = user
                    
                    # Skip if no email (Odoo requires email for partners)
                    if not email or email.strip() == '':
                        logger.warning(f"Skipping user {user_id} - no email address")
                        continue
                      # Check if customer already exists in Odoo
                    existing_partners = self.odoo_service.models.execute_kw(
                        self.odoo_service.db, self.odoo_service.uid, self.odoo_service.password,
                        'res.partner', 'search', [[('email', '=', email.strip())]]
                    )
                    
                    if existing_partners:
                        odoo_partner_id = existing_partners[0]
                        logger.info(f"Customer already exists: {email} -> Odoo ID {odoo_partner_id}")
                    else:
                        # Create new customer in Odoo using the service method
                        odoo_partner_id = self.odoo_service.create_customer(
                            name=name or 'Unknown Customer',
                            email=email.strip(),
                            phone=phone,
                            comment=f"Migrated from MSSQL User ID: {user_id}\\n"
                                   f"Organization: {org_name or 'N/A'}\\n"
                                   f"Position: {position or 'N/A'}\\n"
                                   f"Department: {dept or 'N/A'}\\n"
                                   f"Priority Level: {priority or 'medium'}"
                        )
                        
                        logger.info(f"✅ Created customer: {name} ({email}) -> Odoo ID {odoo_partner_id}")
                    
                    # Store mapping
                    self.id_mapping['users'][user_id] = odoo_partner_id
                    self.migration_stats['customers_migrated'] += 1
                    
                    # Small delay to avoid API rate limits
                    time.sleep(0.1)
                    
                except Exception as e:
                    error_msg = f"Failed to migrate user {user_id}: {e}"
                    logger.error(error_msg)
                    self.migration_stats['errors'].append(error_msg)
            
            logger.info(f"✅ Users migration completed: {self.migration_stats['customers_migrated']} customers migrated")
            
        except Exception as e:
            error_msg = f"Fatal error in users migration: {e}"
            logger.error(error_msg)
            self.migration_stats['errors'].append(error_msg)
    
    def migrate_categories_to_teams(self):
        """Migrate Categories to Odoo Helpdesk Teams"""
        logger.info("🔄 Starting Categories -> Helpdesk Teams migration...")
        
        try:
            cursor = self.mssql_conn.cursor()
            
            # Get all categories
            cursor.execute("""
                SELECT CategoryID, Name, Team, CreatedAt
                FROM Categories 
                ORDER BY CategoryID
            """)
            
            categories = cursor.fetchall()
            logger.info(f"Found {len(categories)} categories to migrate")
            
            for category in categories:
                try:
                    category_id, name, team, created_at = category
                      # Check if team already exists
                    existing_teams = self.odoo_service.models.execute_kw(
                        self.odoo_service.db, self.odoo_service.uid, self.odoo_service.password,
                        'helpdesk.team', 'search', [[('name', '=', name)]]
                    )
                    
                    if existing_teams:
                        odoo_team_id = existing_teams[0]
                        logger.info(f"Team already exists: {name} -> Odoo ID {odoo_team_id}")
                    else:
                        # Create helpdesk team
                        team_data = {
                            'name': name,
                            'description': f"Migrated from MSSQL Category ID: {category_id}\\n"
                                         f"Original Team: {team}",
                            'use_website_helpdesk_form': True,
                            'use_website_helpdesk_livechat': False,
                            'use_helpdesk_timesheet': False,
                            'use_helpdesk_sale_timesheet': False,
                        }
                        
                        # Create team via API
                        odoo_team_id = self.odoo_service.models.execute_kw(
                            self.odoo_service.db, self.odoo_service.uid, self.odoo_service.password,
                            'helpdesk.team', 'create', [team_data]
                        )
                        logger.info(f"✅ Created team: {name} -> Odoo ID {odoo_team_id}")
                    
                    # Store mapping
                    self.id_mapping['categories'][category_id] = odoo_team_id
                    self.migration_stats['categories_migrated'] += 1
                    
                    time.sleep(0.1)
                    
                except Exception as e:
                    error_msg = f"Failed to migrate category {category_id}: {e}"
                    logger.error(error_msg)
                    self.migration_stats['errors'].append(error_msg)
            
            logger.info(f"✅ Categories migration completed: {self.migration_stats['categories_migrated']} teams migrated")
            
        except Exception as e:
            error_msg = f"Fatal error in categories migration: {e}"
            logger.error(error_msg)
            self.migration_stats['errors'].append(error_msg)
    
    def migrate_tickets(self):
        """Migrate Tickets to Odoo Helpdesk Tickets"""
        logger.info("🔄 Starting Tickets migration...")
        
        try:
            cursor = self.mssql_conn.cursor()
            
            # Get all tickets with related data
            cursor.execute("""
                SELECT t.TicketID, t.UserID, t.CategoryID, t.Subject, t.Status, 
                       t.Priority, t.OrganizationName, t.CreatedBy, t.CreatedAt, 
                       t.UpdatedAt, t.escalation_level, t.resolution_method,
                       t.bot_attempted
                FROM Tickets t
                ORDER BY t.TicketID
            """)
            
            tickets = cursor.fetchall()
            logger.info(f"Found {len(tickets)} tickets to migrate")
            
            for ticket in tickets:
                try:
                    (ticket_id, user_id, category_id, subject, status, priority, 
                     org_name, created_by, created_at, updated_at, escalation_level, 
                     resolution_method, bot_attempted) = ticket
                    
                    # Get partner ID from mapping
                    partner_id = self.id_mapping['users'].get(user_id) if user_id else None
                    
                    # Get team ID from mapping
                    team_id = self.id_mapping['categories'].get(category_id, 1)  # Default team if not found
                    
                    # Map status
                    odoo_stage_id = self.get_odoo_stage_id(status)
                    
                    # Map priority
                    odoo_priority = self.map_priority_to_odoo(priority)
                    
                    # Get first message for description
                    cursor.execute("""
                        SELECT TOP 1 Content FROM Messages 
                        WHERE TicketID = ? AND IsAdminReply = 0 
                        ORDER BY CreatedAt
                    """, ticket_id)
                    
                    first_message = cursor.fetchone()
                    description = first_message[0] if first_message else subject
                      # Create ticket in Odoo
                    ticket_data = {
                        'name': subject,
                        'description': f"{description}\\n\\n--- Migration Info ---\\n"
                                     f"Original Ticket ID: {ticket_id}\\n"
                                     f"Created By: {created_by or 'Unknown'}\\n"
                                     f"Organization: {org_name or 'N/A'}\\n"
                                     f"Bot Attempted: {'Yes' if bot_attempted else 'No'}\\n"
                                     f"Resolution Method: {resolution_method or 'N/A'}\\n"
                                     f"Escalation Level: {escalation_level or 0}",
                        'team_id': team_id,
                        'priority': odoo_priority,
                        'stage_id': odoo_stage_id,
                    }
                    
                    if partner_id:
                        ticket_data['partner_id'] = partner_id
                    
                    # Create ticket using Odoo service method
                    odoo_ticket_id = self.odoo_service.create_ticket(
                        name=subject,
                        description=ticket_data['description'],
                        partner_id=partner_id,
                        priority=odoo_priority
                    )
                    
                    # Store mapping
                    self.id_mapping['tickets'][ticket_id] = odoo_ticket_id
                    self.migration_stats['tickets_migrated'] += 1
                    
                    logger.info(f"✅ Created ticket: {subject} (ID: {ticket_id}) -> Odoo ID {odoo_ticket_id}")
                    
                    # Migrate messages for this ticket
                    self.migrate_ticket_messages(ticket_id, odoo_ticket_id, cursor)
                    
                    time.sleep(0.2)  # Longer delay for tickets
                    
                except Exception as e:
                    error_msg = f"Failed to migrate ticket {ticket_id}: {e}"
                    logger.error(error_msg)
                    self.migration_stats['errors'].append(error_msg)
            
            logger.info(f"✅ Tickets migration completed: {self.migration_stats['tickets_migrated']} tickets migrated")
            
        except Exception as e:
            error_msg = f"Fatal error in tickets migration: {e}"
            logger.error(error_msg)
            self.migration_stats['errors'].append(error_msg)
    
    def migrate_ticket_messages(self, mssql_ticket_id, odoo_ticket_id, cursor):
        """Migrate messages for a specific ticket"""
        try:
            # Get all messages for this ticket
            cursor.execute("""
                SELECT MessageID, SenderID, Content, IsAdminReply, IsBotResponse, CreatedAt
                FROM Messages
                WHERE TicketID = ?
                ORDER BY CreatedAt
            """, mssql_ticket_id)
            
            messages = cursor.fetchall()
            
            for message in messages:
                message_id, sender_id, content, is_admin, is_bot, created_at = message
                
                try:                    # Create message/note in Odoo ticket
                    if is_bot:
                        # Bot response - create as internal note
                        note_data = {
                            'res_id': odoo_ticket_id,
                            'res_model': 'helpdesk.ticket',
                            'body': f"<p><strong>🤖 Bot Response:</strong></p><p>{content}</p>",
                            'message_type': 'comment',
                            'author_id': 1,  # System user
                        }
                    elif is_admin:
                        # Admin reply - create as message
                        note_data = {
                            'res_id': odoo_ticket_id,
                            'res_model': 'helpdesk.ticket',
                            'body': f"<p><strong>👨‍💼 Admin Reply:</strong></p><p>{content}</p>",
                            'message_type': 'comment',
                            'author_id': 1,  # System user - could map to actual admin if needed
                        }
                    else:
                        # Customer message
                        partner_id = self.id_mapping['users'].get(sender_id) if sender_id else None
                        note_data = {
                            'res_id': odoo_ticket_id,
                            'res_model': 'helpdesk.ticket',
                            'body': f"<p><strong>👤 Customer:</strong></p><p>{content}</p>",
                            'message_type': 'comment',
                            'author_id': partner_id or 1,
                        }
                    
                    # Create the message
                    self.odoo_service.models.execute_kw(
                        self.odoo_service.db, self.odoo_service.uid, self.odoo_service.password,
                        'mail.message', 'create', [note_data]
                    )
                    self.migration_stats['messages_migrated'] += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to migrate message {message_id}: {e}")        
        except Exception as e:
            logger.error(f"Failed to migrate messages for ticket {mssql_ticket_id}: {e}")
    
    def get_odoo_stage_id(self, mssql_status):
        """Map MSSQL status to Odoo stage ID"""
        try:
            # Common Odoo helpdesk stages
            stage_mapping = {
                'open': 'new',
                'in_progress': 'in_progress', 
                'resolved': 'solved',
                'closed': 'solved',
                'cancelled': 'cancelled'
            }
            
            odoo_stage_name = stage_mapping.get(mssql_status, 'new')
            
            # Find the stage ID
            stages = self.odoo_service.models.execute_kw(
                self.odoo_service.db, self.odoo_service.uid, self.odoo_service.password,
                'helpdesk.stage', 'search', [[('name', 'ilike', odoo_stage_name)]], {'limit': 1}
            )
              return stages[0] if stages else 1  # Default to first stage
            
        except Exception as e:
            logger.warning(f"Failed to map stage {mssql_status}: {e}")
            return 1
    
    def map_priority_to_odoo(self, mssql_priority):
        """Map MSSQL priority to Odoo priority"""
        priority_mapping = {
            'low': '0',
            'medium': '1', 
            'high': '2',
            'critical': '3'
        }
        return priority_mapping.get(mssql_priority, '1')
    
    def update_mssql_with_odoo_ids(self):
        """Update MSSQL records with Odoo IDs for future sync"""
        logger.info("🔄 Updating MSSQL records with Odoo IDs...")
        
        try:
            cursor = self.mssql_conn.cursor()
            
            # First, add the columns if they don't exist (run migration script)
            try:
                cursor.execute("ALTER TABLE Tickets ADD odoo_customer_id INT NULL")
            except:
                pass  # Column might already exist
            
            try:
                cursor.execute("ALTER TABLE Tickets ADD odoo_ticket_id INT NULL")
            except:
                pass  # Column might already exist
            
            # Update tickets with Odoo IDs
            for mssql_ticket_id, odoo_ticket_id in self.id_mapping['tickets'].items():
                try:
                    # Get user ID for this ticket
                    cursor.execute("SELECT UserID FROM Tickets WHERE TicketID = ?", mssql_ticket_id)
                    result = cursor.fetchone()
                    
                    if result and result[0]:
                        user_id = result[0]
                        odoo_customer_id = self.id_mapping['users'].get(user_id)
                        
                        cursor.execute("""
                            UPDATE Tickets 
                            SET odoo_ticket_id = ?, odoo_customer_id = ?
                            WHERE TicketID = ?
                        """, odoo_ticket_id, odoo_customer_id, mssql_ticket_id)
                
                except Exception as e:
                    logger.warning(f"Failed to update ticket {mssql_ticket_id} with Odoo IDs: {e}")
            
            self.mssql_conn.commit()
            logger.info("✅ MSSQL records updated with Odoo IDs")
            
        except Exception as e:
            logger.error(f"Failed to update MSSQL with Odoo IDs: {e}")
    
    def print_migration_summary(self):
        """Print migration summary"""
        logger.info("="*60)
        logger.info("🎉 MIGRATION SUMMARY")
        logger.info("="*60)
        logger.info(f"👥 Customers migrated: {self.migration_stats['customers_migrated']}")
        logger.info(f"📋 Categories/Teams migrated: {self.migration_stats['categories_migrated']}")
        logger.info(f"🎫 Tickets migrated: {self.migration_stats['tickets_migrated']}")
        logger.info(f"💬 Messages migrated: {self.migration_stats['messages_migrated']}")
        logger.info(f"❌ Errors encountered: {len(self.migration_stats['errors'])}")
        
        if self.migration_stats['errors']:
            logger.info("\\n📝 ERROR DETAILS:")
            for error in self.migration_stats['errors'][:10]:  # Show first 10 errors
                logger.info(f"  - {error}")
            
            if len(self.migration_stats['errors']) > 10:
                logger.info(f"  ... and {len(self.migration_stats['errors']) - 10} more errors")
        
        logger.info("="*60)
    
    def run_full_migration(self):
        """Run the complete migration process"""
        logger.info("🚀 Starting Full MSSQL to Odoo Migration")
        
        if not self.initialize_connections():
            logger.error("❌ Failed to initialize connections. Aborting migration.")
            return False
        
        try:
            # Step 1: Migrate users to customers
            self.migrate_users_to_customers()
            
            # Step 2: Migrate categories to helpdesk teams  
            self.migrate_categories_to_teams()
            
            # Step 3: Migrate tickets (includes messages)
            self.migrate_tickets()
            
            # Step 4: Update MSSQL with Odoo IDs
            self.update_mssql_with_odoo_ids()
            
            # Print summary
            self.print_migration_summary()
            
            logger.info("✅ Migration completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            return False
        
        finally:
            if self.mssql_conn:
                self.mssql_conn.close()

def main():
    """Main migration function"""
    migrator = MSSQLToOdooMigrator()
    success = migrator.run_full_migration()
    
    if success:
        print("\\n🎉 Migration completed successfully!")
        print("\\n📋 Next Steps:")
        print("1. Check your Odoo Helpdesk to verify all tickets were created")
        print("2. Test creating new tickets via the chatbot to ensure they sync to Odoo")
        print("3. Set up periodic sync jobs if needed")
        print("4. Configure Odoo Helpdesk team settings and workflows")
    else:
        print("\\n❌ Migration failed. Please check the logs above for details.")
        
if __name__ == "__main__":
    main()
