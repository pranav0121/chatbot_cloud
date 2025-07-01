#!/usr/bin/env python3
"""
Test Ticket Creation with Device Tracking
"""

import urllib.request
import json

def test_ticket_creation():
    url = "http://127.0.0.1:5000/api/tickets"
    
    data = {
        "message": "Device tracking test after Flask restart",
        "subject": "Device Test After Restart",
        "priority": "medium"
    }
    
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'X-Forwarded-For': '192.168.1.100'
    }
    
    try:
        json_data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=json_data, headers=headers, method='POST')
        
        with urllib.request.urlopen(req) as response:
            result = response.read().decode()
            print(f"Status: {response.status}")
            print(f"Response: {result}")
            
            # Parse the JSON to get ticket ID
            if response.status == 200:
                ticket_data = json.loads(result)
                ticket_id = ticket_data.get('ticket_id')
                print(f"\n✅ Ticket created: {ticket_id}")
                return ticket_id
                
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    ticket_id = test_ticket_creation()
    if ticket_id:
        print(f"\nNext: Check if device info was captured for ticket {ticket_id}")
    else:
        print("\nFailed to create ticket")
