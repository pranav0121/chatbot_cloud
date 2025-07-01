#!/usr/bin/env python3
"""
Direct test of force escalation API with extensive logging
"""

import requests
import json
import sys

# Test the force escalation API directly
def test_force_escalation():
    base_url = "http://127.0.0.1:5000"
    
    print("=== TESTING FORCE ESCALATION API ===")
    
    # Step 1: Login as super admin
    print("\n1. Logging in as super admin...")
    login_data = {
        'email': 'superadmin@youcloudpay.com',
        'password': 'SuperSecure2024!'
    }
    
    session = requests.Session()
    login_response = session.post(f"{base_url}/auth/admin/login", data=login_data, allow_redirects=False)
    print(f"Login response status: {login_response.status_code}")
    
    if login_response.status_code not in [200, 302]:
        print(f"Login failed. Response: {login_response.text}")
        return
    
    # Step 2: Get a test ticket
    print("\n2. Getting ticket for escalation...")
    tickets_response = session.get(f"{base_url}/super-admin/api/escalation/dashboard")
    print(f"Tickets API status: {tickets_response.status_code}")
    
    if tickets_response.status_code == 200:
        tickets_data = tickets_response.json()
        print(f"Found {len(tickets_data.get('tickets', []))} tickets")
        
        if tickets_data.get('tickets'):
            test_ticket = tickets_data['tickets'][0]
            ticket_id = test_ticket['id']
            print(f"Using ticket ID: {ticket_id}")
            print(f"Current ticket status: {test_ticket.get('status')}")
            print(f"Current escalation level: {test_ticket.get('escalation_level')}")
            print(f"Current partner: {test_ticket.get('assigned_partner', 'None')}")
        else:
            print("No tickets found for testing")
            return
    else:
        print("Failed to get tickets. Using ticket ID 1 as fallback")
        ticket_id = 1
    
    # Step 3: Force escalate the ticket
    print(f"\n3. Force escalating ticket {ticket_id}...")
    escalation_data = {
        'level': 1,
        'comment': 'Test escalation from direct API test'
    }
    
    escalation_response = session.post(
        f"{base_url}/super-admin/api/escalation/force/{ticket_id}",
        json=escalation_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Escalation response status: {escalation_response.status_code}")
    print(f"Escalation response headers: {dict(escalation_response.headers)}")
    
    try:
        response_data = escalation_response.json()
        print(f"Escalation response data: {json.dumps(response_data, indent=2)}")
    except:
        print(f"Escalation response text: {escalation_response.text}")
    
    # Step 4: Check the escalation dashboard again
    print("\n4. Checking escalation dashboard after escalation...")
    dashboard_response = session.get(f"{base_url}/super-admin/api/escalation/dashboard")
    
    if dashboard_response.status_code == 200:
        dashboard_data = dashboard_response.json()
        print(f"Dashboard has {len(dashboard_data.get('tickets', []))} tickets")
        
        # Find our ticket
        for ticket in dashboard_data.get('tickets', []):
            if ticket['id'] == ticket_id:
                print(f"\nTicket {ticket_id} after escalation:")
                print(f"  Status: {ticket.get('status')}")
                print(f"  Escalation level: {ticket.get('escalation_level')}")
                print(f"  Partner: {ticket.get('assigned_partner', 'None')}")
                print(f"  Partner type: {ticket.get('partner_type', 'None')}")
                break
        else:
            print(f"Ticket {ticket_id} not found in dashboard after escalation")
    else:
        print(f"Failed to get dashboard data: {dashboard_response.status_code}")

if __name__ == "__main__":
    test_force_escalation()
