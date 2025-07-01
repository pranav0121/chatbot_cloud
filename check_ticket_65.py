#!/usr/bin/env python3
"""
Check Specific Ticket Device Info
Check device info for ticket 65 specifically
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from config import Config

def check_ticket_65():
    """Check device info for ticket 65"""
    
    print("🔍 Checking Device Info for Ticket 65")
    print("=" * 50)
    
    try:
        config = Config()
        engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
        
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    TicketID, Subject, device_type, operating_system, browser, 
                    browser_version, os_version, device_brand, device_model,
                    device_fingerprint, user_agent, ip_address, CreatedAt
                FROM Tickets 
                WHERE TicketID = 65
            """))
            
            ticket = result.fetchone()
            
            if ticket:
                print(f"✅ Found ticket 65:")
                print(f"   Subject: {ticket[1]}")
                print(f"   Device Type: {ticket[2] or 'Not captured'}")
                print(f"   OS: {ticket[3] or 'Not captured'}")
                print(f"   Browser: {ticket[4] or 'Not captured'}")
                print(f"   Browser Version: {ticket[5] or 'Not captured'}")
                print(f"   OS Version: {ticket[6] or 'Not captured'}")
                print(f"   Device Brand: {ticket[7] or 'Not captured'}")
                print(f"   Device Model: {ticket[8] or 'Not captured'}")
                print(f"   Device Fingerprint: {ticket[9] or 'Not captured'}")
                print(f"   User Agent: {ticket[10] or 'Not captured'}")
                print(f"   IP Address: {ticket[11] or 'Not captured'}")
                print(f"   Created: {ticket[12]}")
                
                # Count captured fields
                device_fields = [ticket[2], ticket[3], ticket[4], ticket[5], ticket[6], ticket[7], ticket[8], ticket[9], ticket[10], ticket[11]]
                captured_count = sum(1 for field in device_fields if field is not None)
                
                print(f"\n📊 Device Info Status: {captured_count}/10 fields captured")
                
                if captured_count > 0:
                    print("✅ Some device information captured")
                else:
                    print("❌ No device information captured")
            else:
                print("❌ Ticket 65 not found")
                
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    check_ticket_65()
