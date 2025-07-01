#!/usr/bin/env python3
"""
Check Device Info for Specific Ticket
"""

import pyodbc
from config import Config

def check_ticket_device_info(ticket_id):
    """Check device info for a specific ticket"""
    
    config = Config()
    
    # Parse connection string to get connection parameters
    if config.DB_USE_WINDOWS_AUTH:
        conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config.DB_SERVER};DATABASE={config.DB_DATABASE};Trusted_Connection=yes;"
    else:
        conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={config.DB_SERVER};DATABASE={config.DB_DATABASE};UID={config.DB_USERNAME};PWD={config.DB_PASSWORD};"
    
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Query ticket device info
        query = """
        SELECT TicketID, device_type, operating_system, browser, browser_version, 
               os_version, device_brand, device_model, device_fingerprint, 
               user_agent, ip_address, CreatedAt
        FROM Tickets 
        WHERE TicketID = ?
        """
        
        cursor.execute(query, (ticket_id,))
        row = cursor.fetchone()
        
        if row:
            print(f"✅ Found ticket {ticket_id}:")
            print(f"   Device Type: {row.device_type or 'Not captured'}")
            print(f"   OS: {row.operating_system or 'Not captured'}")
            print(f"   Browser: {row.browser or 'Not captured'}")
            print(f"   Browser Version: {row.browser_version or 'Not captured'}")
            print(f"   OS Version: {row.os_version or 'Not captured'}")
            print(f"   Device Brand: {row.device_brand or 'Not captured'}")
            print(f"   Device Model: {row.device_model or 'Not captured'}")
            print(f"   Device Fingerprint: {row.device_fingerprint or 'Not captured'}")
            print(f"   User Agent: {row.user_agent or 'Not captured'}")
            print(f"   IP Address: {row.ip_address or 'Not captured'}")
            print(f"   Created: {row.CreatedAt}")
            
            # Check if any device info was captured
            device_fields = [row.device_type, row.operating_system, row.browser, 
                           row.browser_version, row.os_version, row.device_brand,
                           row.device_model, row.device_fingerprint, row.user_agent, row.ip_address]
            
            captured_count = sum(1 for field in device_fields if field)
            print(f"\n📊 Device Info Status: {captured_count}/10 fields captured")
            
            if captured_count > 0:
                print("✅ Device tracking is working!")
            else:
                print("❌ No device information captured")
        else:
            print(f"❌ Ticket {ticket_id} not found")
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    # Check the most recent ticket (64)
    check_ticket_device_info(64)
