#!/usr/bin/env python3
"""
Check Device Info in Created Ticket
Verify that device tracking was captured
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

try:
    # Get all tickets from admin API
    response = requests.get(f"{BASE_URL}/admin/api/tickets")
    
    if response.status_code == 200:
        tickets = response.json()
        print(f"Retrieved {len(tickets)} tickets")
        
        # Find ticket 58 (the one we just created)
        for ticket in tickets:
            if ticket.get('TicketID') == 58:
                print(f"\n🎯 Found Ticket {ticket['TicketID']}:")
                print(f"   Subject: {ticket.get('Subject', 'N/A')}")
                print(f"   Priority: {ticket.get('Priority', 'N/A')}")
                print(f"   Status: {ticket.get('Status', 'N/A')}")
                
                print(f"\n📱 Device Information:")
                device_fields = [
                    'device_type', 'operating_system', 'browser', 
                    'browser_version', 'os_version', 'device_brand',
                    'device_model', 'ip_address', 'user_agent'
                ]
                
                device_found = False
                for field in device_fields:
                    value = ticket.get(field)
                    if value:
                        print(f"   {field}: {value}")
                        device_found = True
                
                if not device_found:
                    print("   No device information found")
                
                break
        else:
            print("Ticket 58 not found in admin API")
    else:
        print(f"Admin API failed: {response.status_code}")
        
except Exception as e:
    print(f"Error: {e}")
