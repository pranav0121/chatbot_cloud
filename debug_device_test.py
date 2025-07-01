#!/usr/bin/env python3
"""
Test Device Tracking with Debug Output
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

test_data = {
    "message": "Device tracking debug test",
    "subject": "Debug Test Ticket",
    "priority": "medium"
}

headers = {
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'X-Forwarded-For': '192.168.1.100'
}

print("🧪 Testing Device Tracking with Debug Headers")
print("=" * 50)
print(f"User-Agent: {headers['User-Agent']}")
print(f"X-Forwarded-For: {headers['X-Forwarded-For']}")

try:
    response = requests.post(f"{BASE_URL}/api/tickets", json=test_data, headers=headers)
    
    print(f"\nResponse Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        ticket_id = result.get('ticket_id')
        print(f"✅ Ticket created: {ticket_id}")
        
        # Now let's check the Flask logs for our device tracking debug messages
        print(f"\n📋 Check Flask logs for these messages:")
        print(f"   'Device tracking - Request data for ticket {ticket_id}'")
        print(f"   'Device tracking - Successfully parsed device data for ticket {ticket_id}'")
        print(f"   'Added device info to ticket {ticket_id}'")
    else:
        print(f"❌ Request failed: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n📝 If you don't see device tracking messages in Flask logs,")
print("   the device tracking code might not be executing.")
print("   This could be due to import issues or code placement.")
