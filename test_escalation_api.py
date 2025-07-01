#!/usr/bin/env python3
"""
Test escalation dashboard API specifically
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_escalation_api():
    session = requests.Session()
    
    print("=== TESTING ESCALATION DASHBOARD API ===\n")
    
    # Login
    print("1. Logging in...")
    login_data = {
        'email': 'admin@youcloudtech.com', 
        'password': 'admin123'
    }
    
    login_response = session.post(f"{BASE_URL}/auth/admin/login", data=login_data, allow_redirects=False)
    print(f"   Login status: {login_response.status_code}")
    
    if login_response.status_code != 302:
        print("   ❌ Login failed!")
        return
    
    print("   ✅ Login successful!")
    
    # Test escalation dashboard API
    print("\n2. Testing escalation dashboard API...")
    response = session.get(f"{BASE_URL}/super-admin/api/escalation/dashboard")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("   ✅ API call successful!")
        print("\nFull response:")
        print(json.dumps(data, indent=2))
        
        # Check if we have tickets data
        if 'tickets' in data:
            tickets = data['tickets']
            print(f"\n📊 Analysis:")
            print(f"   Within SLA: {data.get('within_sla', 0)}")
            print(f"   SLA Warning: {data.get('sla_warning', 0)}")
            print(f"   SLA Breached: {data.get('sla_breached', 0)}")
            print(f"   Total tickets returned: {len(tickets)}")
            
            if len(tickets) > 0:
                print(f"\n   Sample tickets:")
                for i, ticket in enumerate(tickets[:3]):  # Show first 3 tickets
                    print(f"     {i+1}. ID: {ticket.get('ticket_id')}, Priority: {ticket.get('priority')}, SLA: {ticket.get('sla_status')}")
            else:
                print(f"\n   ⚠️  No tickets returned in response")
    else:
        print(f"   ❌ API call failed: {response.text}")

if __name__ == "__main__":
    test_escalation_api()
