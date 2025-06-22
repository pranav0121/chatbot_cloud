#!/usr/bin/env python3
"""
Manual Sync Script - Sync existing tickets to Odoo
This will test and fix the integration
"""

import pyodbc
import logging
from config import Config
from odoo_service import OdooService
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def manual_sync_recent_tickets():
    """Manually sync recent tickets to Odoo"""
    logger.info("🔄 Starting Manual Ticket Sync to Odoo...")
    
    config = Config()
    stats = {'synced': 0, 'errors': 0, 'skipped': 0}
    
    try:
        # Initialize connections
        logger.info("Connecting to Odoo...")
        odoo_service = OdooService(
            url=config.ODOO_URL,
            db=config.ODOO_DB,
            username=config.ODOO_USERNAME,
            password=config.ODOO_PASSWORD
        )
        logger.info("✅ Odoo connected")
        
        # Connect to MSSQL
        logger.info("Connecting to MSSQL...")
        if config.DB_USE_WINDOWS_AUTH:
            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config.DB_SERVER};DATABASE={config.DB_DATABASE};Trusted_Connection=yes;"
        else:
            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config.DB_SERVER};DATABASE={config.DB_DATABASE};UID={config.DB_USERNAME};PWD={config.DB_PASSWORD};"
        
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        logger.info("✅ MSSQL connected")
        
        # Get tickets that haven't been synced (focus on recent ones)
        cursor.execute("""
            SELECT TOP 5 t.TicketID, t.UserID, t.Subject, t.Priority, t.Status,
                   t.OrganizationName, t.CreatedBy, t.CreatedAt,
                   u.Name, u.Email, u.Phone
            FROM Tickets t
            LEFT JOIN Users u ON t.UserID = u.UserID
            WHERE t.odoo_ticket_id IS NULL 
            ORDER BY t.TicketID DESC
        """)
        
        tickets = cursor.fetchall()
        logger.info(f"Found {len(tickets)} tickets to sync")
        
        for ticket in tickets:
            (ticket_id, user_id, subject, priority, status, org_name, created_by, 
             created_at, user_name, user_email, user_phone) = ticket
            
            try:
                logger.info(f"🔄 Syncing Ticket #{ticket_id}: {subject}")
                
                # Step 1: Create/find customer in Odoo
                odoo_customer_id = None
                if user_email and user_email.strip():
                    try:
                        logger.info(f"  📧 Creating customer: {user_name} ({user_email})")
                        odoo_customer_id = odoo_service.create_customer(
                            name=user_name or created_by or "Unknown Customer",
                            email=user_email.strip(),
                            phone=user_phone,
                            comment=f"From Ticket #{ticket_id}\\nOrganization: {org_name or 'N/A'}"
                        )
                        logger.info(f"  ✅ Customer created/found: ID {odoo_customer_id}")
                    except Exception as e:
                        if "already exists" in str(e).lower():
                            # Find existing customer
                            existing_customers = odoo_service.models.execute_kw(
                                odoo_service.db, odoo_service.uid, odoo_service.password,
                                'res.partner', 'search', [[('email', '=', user_email.strip())]]
                            )
                            if existing_customers:
                                odoo_customer_id = existing_customers[0]
                                logger.info(f"  ✅ Found existing customer: ID {odoo_customer_id}")
                        else:
                            logger.warning(f"  ⚠️ Customer creation failed: {e}")
                
                # Step 2: Get first message for description
                cursor.execute("""
                    SELECT TOP 1 Content FROM Messages 
                    WHERE TicketID = ? AND IsAdminReply = 0 
                    ORDER BY CreatedAt
                """, ticket_id)
                
                first_message = cursor.fetchone()
                description = first_message[0] if first_message else subject
                
                # Step 3: Create ticket in Odoo
                logger.info(f"  🎫 Creating ticket in Odoo...")
                full_description = f"{description}\\n\\n--- Ticket Details ---\\n"
                full_description += f"Original Ticket ID: {ticket_id}\\n"
                full_description += f"Status: {status}\\n"
                full_description += f"Created By: {created_by or 'Unknown'}\\n"
                full_description += f"Organization: {org_name or 'N/A'}\\n"
                full_description += f"Created At: {created_at}"
                
                # Map priority
                odoo_priority = '2' if priority in ['high', 'critical'] else '1'
                
                odoo_ticket_id = odoo_service.create_ticket(
                    name=subject or "Support Request",
                    description=full_description,
                    partner_id=odoo_customer_id,
                    priority=odoo_priority,
                    tag_ids=['migrated-from-chatbot']
                )
                
                logger.info(f"  ✅ Ticket created in Odoo: ID {odoo_ticket_id}")
                
                # Step 4: Update MSSQL with Odoo IDs
                cursor.execute("""
                    UPDATE Tickets 
                    SET odoo_ticket_id = ?, odoo_customer_id = ?
                    WHERE TicketID = ?
                """, odoo_ticket_id, odoo_customer_id, ticket_id)
                
                stats['synced'] += 1
                logger.info(f"  🎉 Successfully synced Ticket #{ticket_id}")
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.error(f"❌ Failed to sync ticket {ticket_id}: {e}")
                import traceback
                traceback.print_exc()
                stats['errors'] += 1
        
        # Commit changes
        conn.commit()
        logger.info("✅ Database updated with Odoo IDs")
        
        # Print summary
        logger.info("="*60)
        logger.info("📊 MANUAL SYNC SUMMARY")
        logger.info("="*60)
        logger.info(f"✅ Tickets synced: {stats['synced']}")
        logger.info(f"⚠️ Skipped: {stats['skipped']}")
        logger.info(f"❌ Errors: {stats['errors']}")
        logger.info("="*60)
        
        if stats['synced'] > 0:
            logger.info("🎉 Manual sync completed successfully!")
            logger.info("📋 Check your Odoo Helpdesk now - tickets should appear!")
        
        conn.close()
        
        return stats['synced'] > 0
        
    except Exception as e:
        logger.error(f"❌ Manual sync failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run manual sync"""
    print("🚀 MANUAL ODOO SYNC")
    print("This will sync your recent tickets (including #40) to Odoo...")
    print("")
    
    success = manual_sync_recent_tickets()
    
    if success:
        print("\\n🎯 SUCCESS! Check your Odoo Helpdesk:")
        print("1. Go to https://youcloudpay.odoo.com")
        print("2. Open Helpdesk → All Tickets")
        print("3. Your tickets should now appear!")
        print("\\n⚠️ IMPORTANT: Restart your Flask app to enable auto-sync for future tickets")
    else:
        print("\\n❌ Sync failed. Check the logs above for details.")

if __name__ == "__main__":
    main()
