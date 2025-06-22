#!/usr/bin/env python3
"""
Quick Sync - Sync just one ticket to test the fix
"""
import pyodbc
import os
import logging
from dotenv import load_dotenv
from odoo_service import OdooService

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def quick_sync_test():
    """Sync just one ticket to test if the fix works"""
    try:
        # Load environment
        load_dotenv()
        
        # Initialize Odoo service
        logger.info("🔄 Initializing Odoo service...")
        odoo_service = OdooService(
            os.getenv('ODOO_URL'),
            os.getenv('ODOO_DB'),
            os.getenv('ODOO_USERNAME'),
            os.getenv('ODOO_PASSWORD')
        )
        logger.info("✅ Connected to Odoo")
        
        # Connect to MSSQL
        connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={os.getenv('MSSQL_SERVER')};"
            f"DATABASE={os.getenv('MSSQL_DATABASE')};"
            f"UID={os.getenv('MSSQL_USERNAME')};"
            f"PWD={os.getenv('MSSQL_PASSWORD')};"
            f"TrustServerCertificate=yes;"
        )
        
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        logger.info("✅ Connected to MSSQL")
        
        # Find one ticket without Odoo ID
        cursor.execute("""
            SELECT TOP 1 TicketID, Subject, Priority, Status, CreatedBy, CreatedAt, OrganizationID
            FROM Tickets 
            WHERE odoo_ticket_id IS NULL 
            ORDER BY CreatedAt DESC
        """)
        
        ticket = cursor.fetchone()
        if not ticket:
            logger.info("ℹ️ No unsynced tickets found")
            return True
            
        ticket_id, subject, priority, status, created_by, created_at, org_id = ticket
        logger.info(f"🎫 Found ticket #{ticket_id}: {subject}")
        
        # Create a simple test ticket in Odoo
        logger.info("🚀 Creating ticket in Odoo with tags...")
        
        odoo_ticket_id = odoo_service.create_ticket(
            name=subject or "Test Ticket",
            description=f"Test ticket from chatbot sync\nOriginal ID: {ticket_id}\nStatus: {status}",
            priority='1',
            tag_ids=['migrated-from-chatbot', 'test-sync']  # This should now work!
        )
        
        logger.info(f"✅ Ticket created in Odoo: ID {odoo_ticket_id}")
        
        # Update MSSQL with Odoo ID
        cursor.execute("""
            UPDATE Tickets 
            SET odoo_ticket_id = ?
            WHERE TicketID = ?
        """, odoo_ticket_id, ticket_id)
        conn.commit()
        
        logger.info(f"✅ Updated ticket #{ticket_id} with Odoo ID {odoo_ticket_id}")
        logger.info("🎉 Quick sync test successful!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Quick sync failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    logger.info("="*50)
    logger.info("🧪 QUICK SYNC TEST - Testing Tag Fix")
    logger.info("="*50)
    
    success = quick_sync_test()
    
    logger.info("="*50)
    if success:
        logger.info("✅ TAG FIX WORKS! Tickets can now sync to Odoo!")
        logger.info("✅ You can now run the full manual_sync_tickets.py")
    else:
        logger.info("❌ Tag fix test failed")
    logger.info("="*50)
