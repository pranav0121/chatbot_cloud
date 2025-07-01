#!/usr/bin/env python3
"""
Check Device Info in Database
Direct database query to verify device tracking storage
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from config import Config

def check_device_info_in_db():
    """Check if device info is being stored in database"""
    
    print("🔍 Checking Device Info in Database")
    print("=" * 40)
    
    try:
        # Connect to database
        config = Config()
        engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
        
        with engine.connect() as conn:
            # Check the last few tickets for device info
            result = conn.execute(text("""
                SELECT TOP 5 
                    TicketID, Subject, device_type, operating_system, browser, 
                    browser_version, ip_address, user_agent, CreatedAt
                FROM Tickets 
                ORDER BY TicketID DESC
            """))
            
            tickets = result.fetchall()
            
            print(f"📋 Last 5 tickets in database:")
            print("-" * 80)
            
            for ticket in tickets:
                print(f"Ticket #{ticket[0]}: {ticket[1]}")
                print(f"   Device Type: {ticket[2] or 'None'}")
                print(f"   OS: {ticket[3] or 'None'}")
                print(f"   Browser: {ticket[4] or 'None'} {ticket[5] or ''}")
                print(f"   IP: {ticket[6] or 'None'}")
                print(f"   User-Agent: {(ticket[7][:50] + '...') if ticket[7] else 'None'}")
                print(f"   Created: {ticket[8]}")
                print("-" * 80)
                
                # Check if any device info exists
                has_device_info = any([ticket[2], ticket[3], ticket[4], ticket[6], ticket[7]])
                if has_device_info:
                    print("   ✅ Has device information")
                else:
                    print("   ❌ No device information")
                print()
            
    except Exception as e:
        print(f"❌ Database error: {e}")

def check_specific_ticket_device(ticket_id):
    """Check device info for a specific ticket"""
    try:
        # Create database connection
        config = Config()
        engine = create_engine(config.SQLALCHEMY_DATABASE_URI, echo=False)
        
        with engine.connect() as conn:
            query = text("""
                SELECT device_type, operating_system, browser, browser_version, 
                       ip_address, user_agent
                FROM Tickets 
                WHERE TicketID = :ticket_id
            """)
            
            result = conn.execute(query, {'ticket_id': ticket_id}).fetchone()
            
            if result:
                return {
                    'device_type': result[0],
                    'operating_system': result[1], 
                    'browser': result[2],
                    'browser_version': result[3],
                    'ip_address': result[4],
                    'user_agent': result[5]
                }
            else:
                return None
                
    except Exception as e:
        print(f"Error checking device info for ticket {ticket_id}: {e}")
        return None

if __name__ == "__main__":
    check_device_info_in_db()
