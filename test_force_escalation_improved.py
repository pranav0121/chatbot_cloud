#!/usr/bin/env python3
"""
Improved test of force escalation API with proper session handling
"""

import requests
import json
import sys
from urllib.parse import urlparse, parse_qs

# Test the force escalation API directly
def test_force_escalation():
    base_url = "http://127.0.0.1:5000"
    
    print("=== TESTING FORCE ESCALATION API WITH BETTER SESSION HANDLING ===")
    
    # Step 1: Login as super admin using form data
    print("\n1. Logging in as super admin...")
    login_data = {
        'email': 'superadmin@youcloudpay.com',
        'password': 'SuperSecure2024!'
    }
    
    session = requests.Session()
    
    # First get the login page to establish session
    print("Getting login page...")
    login_page = session.get(f"{base_url}/auth/admin/login")
    print(f"Login page status: {login_page.status_code}")
    
    # Now submit login
    print("Submitting login...")
    login_response = session.post(f"{base_url}/auth/admin/login", data=login_data, allow_redirects=True)
    print(f"Login response status: {login_response.status_code}")
    print(f"Login response URL: {login_response.url}")
    
    # Check if we ended up on admin dashboard
    if 'admin' not in login_response.url and 'super-admin' not in login_response.url:
        print("Login may have failed - not redirected to admin area")
        print(f"Final URL: {login_response.url}")
        print("Response content snippet:")
        print(login_response.text[:500])
        return
    
    print("Login successful - proceeding with API tests...")
    
    # Step 2: Test direct access to a super admin API
    print("\n2. Testing super admin API access...")
    dashboard_test = session.get(f"{base_url}/super-admin/api/dashboard-metrics")
    print(f"Dashboard metrics API status: {dashboard_test.status_code}")
    
    if dashboard_test.status_code == 200:
        print("Super admin authentication working!")
    else:
        print(f"Super admin authentication failed: {dashboard_test.text[:200]}")
        return
    
    # Step 3: Get a test ticket
    print("\n3. Getting ticket for escalation...")
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
            print("No tickets found. Creating a test ticket...")
            # Let's use ticket ID 1 as it should exist
            ticket_id = 1
    else:
        print(f"Failed to get tickets: {tickets_response.text[:200]}")
        print("Using ticket ID 1 as fallback")
        ticket_id = 1
    
    # Step 4: Force escalate the ticket
    print(f"\n4. Force escalating ticket {ticket_id}...")
    escalation_data = {
        'level': 1,
        'comment': 'Test escalation from improved API test'
    }
    
    print(f"Sending escalation request to: {base_url}/super-admin/api/escalation/force/{ticket_id}")
    print(f"Request data: {escalation_data}")
    
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
    
    # Step 5: Check the escalation dashboard again
    print("\n5. Checking escalation dashboard after escalation...")
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
