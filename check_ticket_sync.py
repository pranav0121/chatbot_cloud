#!/usr/bin/env python3
"""
Check recent tickets and Odoo sync status
"""

import pyodbc
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_recent_tickets():
    """Check recent tickets and their Odoo sync status"""
    config = Config()
    
    try:
        # Connect to database
        if config.DB_USE_WINDOWS_AUTH:
            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config.DB_SERVER};DATABASE={config.DB_DATABASE};Trusted_Connection=yes;"
        else:
            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config.DB_SERVER};DATABASE={config.DB_DATABASE};UID={config.DB_USERNAME};PWD={config.DB_PASSWORD};"
        
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Check for recent tickets
        print("🔍 CHECKING RECENT TICKETS...")
        print("="*60)
        
        cursor.execute("""
            SELECT TOP 10 TicketID, Subject, odoo_ticket_id, odoo_customer_id, 
                   CreatedAt, Status, CreatedBy, OrganizationName
            FROM Tickets 
            ORDER BY TicketID DESC
        """)
        
        recent_tickets = cursor.fetchall()
        
        if not recent_tickets:
            print("❌ No tickets found in database")
            return
        
        print(f"Found {len(recent_tickets)} recent tickets:")
        print("-" * 60)
        
        for ticket in recent_tickets:
            tid, subject, odoo_tid, odoo_cid, created, status, created_by, org = ticket
            
            # Check if this is ticket #40
            is_new_ticket = tid == 40
            marker = "🆕 NEW TICKET" if is_new_ticket else ""
            
            print(f"Ticket #{tid} {marker}")
            print(f"  Subject: {subject}")
            print(f"  Created By: {created_by}")
            print(f"  Organization: {org}")
            print(f"  Status: {status}")
            print(f"  Created: {created}")
            print(f"  Odoo Ticket ID: {odoo_tid if odoo_tid else '❌ NOT SYNCED'}")
            print(f"  Odoo Customer ID: {odoo_cid if odoo_cid else '❌ NOT SYNCED'}")
            
            if is_new_ticket:
                if not odoo_tid:
                    print("  🚨 ISSUE: This ticket was NOT synced to Odoo!")
                else:
                    print("  ✅ This ticket WAS synced to Odoo")
            
            print("-" * 60)
        
        # Check if Odoo columns exist
        print("\n🔍 CHECKING DATABASE SCHEMA...")
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'Tickets' 
            AND COLUMN_NAME IN ('odoo_customer_id', 'odoo_ticket_id')
        """)
        
        odoo_columns = [row[0] for row in cursor.fetchall()]
        print(f"Odoo columns in database: {odoo_columns}")
        
        if len(odoo_columns) < 2:
            print("❌ Missing Odoo columns in database!")
        else:
            print("✅ Odoo columns exist in database")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking tickets: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_recent_tickets()
